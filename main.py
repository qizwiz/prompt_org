import streamlit as st
import requests
import json
import pandas as pd
import logging
import os
import base64
from utils import generate_html_content, AVAILABLE_MODELS, generate_detailed_user_prompt

logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

def parse_ai_response(response_text):
    try:
        parsed_data = json.loads(response_text)
        if isinstance(parsed_data, list):
            return parsed_data
    except json.JSONDecodeError:
        import re
        json_objects = re.findall(r'\{[^{}]+?\}', response_text, re.DOTALL)
        parsed_data = []
        for obj in json_objects:
            try:
                parsed_obj = json.loads(obj)
                if all(key in parsed_obj for key in ['Letter', 'PromptName', 'Categories', 'PromptText']):
                    parsed_data.append(parsed_obj)
            except json.JSONDecodeError:
                continue
    return parsed_data

def admin_auth():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        password = st.text_input("Enter admin password:", type="password")
        if password == "your_admin_password":  # Replace with your admin password
            st.session_state.authenticated = True
            st.success("Authentication successful!")
        elif password:
            st.error("Incorrect password.")

def load_templates():
    try:
        with open('templates.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_templates(templates):
    with open('templates.json', 'w') as f:
        json.dump(templates, f)

def load_hidden_prompts():
    try:
        with open('hidden_prompts.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_hidden_prompts(hidden_prompts):
    with open('hidden_prompts.json', 'w') as f:
        json.dump(hidden_prompts, f)

def main():
    st.set_page_config(page_title="Custom Prompt Generator", page_icon="🧠")

    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Go to", ["User Interface", "Admin Interface", "About"])

    if page == "User Interface":
        st.title("🧠 Custom Prompt Generator")

        st.markdown("""
        Welcome to the **Custom Prompt Generator**! Generate creative and detailed prompts tailored to your needs.
        """)

        if "generated_prompts" not in st.session_state:
            st.session_state.generated_prompts = []

        # Load templates and hidden prompts
        templates = load_templates()
        hidden_prompts = load_hidden_prompts()

        with st.form(key='prompt_form'):
            topic = st.text_input(
                "**Topic:**",
                placeholder="e.g., AI, Quantum Computing, Climate Change",
                help="Enter the main topic for the prompts."
            )
            model = st.selectbox(
                "**Select AI Model:**",
                list(AVAILABLE_MODELS.keys()),
                format_func=lambda x: f"{x} (Context tokens: {AVAILABLE_MODELS[x]['context_tokens']})",
                help="Choose the AI model to generate prompts."
            )
            num_prompts = st.number_input(
                "**Number of Prompts:**",
                min_value=1,
                max_value=20,
                value=5,
                step=1,
                help="Specify how many prompts you want to generate."
            )

            # Update template selection dropdown
            available_templates = list(templates.keys())
            selected_template = st.selectbox("Select a template", ["None"] + available_templates)

            # Add custom template input
            user_template = st.text_area("Custom Template (optional)", placeholder="Enter your custom template here. Use {subject} as a placeholder for the topic.")

            # Add hidden prompts selection
            available_hidden_prompts = list(hidden_prompts.keys())
            selected_hidden_prompts = st.multiselect("Select hidden prompts", available_hidden_prompts)

            max_allowed_tokens = AVAILABLE_MODELS[model]['context_tokens'] - 500
            max_tokens = st.slider(
                "**Max Tokens:**",
                min_value=50,
                max_value=max_allowed_tokens,
                value=min(1000, max_allowed_tokens),
                step=50,
                help="Set the maximum number of tokens for the AI to generate."
            )
            creativity = st.slider(
                "**Creativity Level (Temperature):**",
                min_value=0.0,
                max_value=1.0,
                value=0.7,
                step=0.1,
                help="Adjust the creativity of the generated prompts."
            )
            submit_button = st.form_submit_button(label='Generate Prompts')

        if submit_button:
            if not topic:
                st.warning("Please enter a topic.")
                return

            # Modify prompt generation logic
            if user_template:
                ai_prompt = user_template.format(subject=topic)
            elif selected_template != "None":
                template_content = templates[selected_template]
                ai_prompt = template_content.format(subject=topic)
            else:
                ai_prompt = generate_detailed_user_prompt()

            # Add selected hidden prompts to the AI prompt
            if selected_hidden_prompts:
                ai_prompt += "\n\nIncorporate the following hidden prompts:\n"
                for prompt_name in selected_hidden_prompts:
                    ai_prompt += f"- {hidden_prompts[prompt_name]}\n"

            ai_prompt += f"\nGenerate {num_prompts} prompts now."

            try:
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                    },
                    json={
                        "model": AVAILABLE_MODELS[model]['id'],
                        "messages": [
                            {"role": "user", "content": ai_prompt.strip()}
                        ],
                        "max_tokens": max_tokens,
                        "temperature": creativity,
                    },
                )

                response.raise_for_status()
                result = response.json()

                if "choices" in result and len(result["choices"]) > 0:
                    generated_text = result["choices"][0]["message"]["content"].strip()
                    logging.debug(f"Generated text: {generated_text}")
                    generated_prompts = parse_ai_response(generated_text)

                    if not generated_prompts:
                        st.error("Failed to parse the generated prompts. Please try again.")
                        return

                    st.subheader("Generated Prompts:")
                    for idx, item in enumerate(generated_prompts, 1):
                        # Update display of generated prompts
                        st.write(f"**Type: {item['PromptName']}**")
                        st.write(item['PromptText'])
                        st.write(f"Categories: {item['Categories']}")
                        st.write("---")

                    st.session_state.generated_prompts = generated_prompts
                else:
                    st.error("No prompts were generated. Please try again.")
            except requests.exceptions.RequestException as e:
                st.error(f"An error occurred: {str(e)}")

        if st.session_state.generated_prompts:
            csv = pd.DataFrame(st.session_state.generated_prompts).to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="generated_prompts.csv">📥 Download CSV File</a>'
            st.markdown(href, unsafe_allow_html=True)

            with st.form(key='generate_html_form'):
                generate_html = st.form_submit_button("🖥️ Generate HTML")
                if generate_html:
                    try:
                        logging.info("Generate HTML button clicked")
                        logging.info(f"Generating HTML content for {len(st.session_state.generated_prompts)} prompts")

                        header_title = "Generated Prompts"
                        theme = "light"
                        html_content = generate_html_content(
                            st.session_state.generated_prompts,
                            has_image_url=False,
                            theme=theme,
                            header_title=header_title
                        )

                        logging.info(f"HTML content generated successfully. Length: {len(html_content)}")

                        b64 = base64.b64encode(html_content.encode()).decode()
                        href = f'<a href="data:text/html;base64,{b64}" download="{header_title}.html">📥 Download Generated HTML</a>'
                        st.markdown(href, unsafe_allow_html=True)

                        st.markdown(f"<h3>Generated HTML Preview:</h3>", unsafe_allow_html=True)
                        st.markdown(html_content, unsafe_allow_html=True)
                        logging.info("HTML content displayed successfully")
                    except Exception as e:
                        logging.error(f"Error generating or displaying HTML content: {str(e)}")
                        st.error(f"An error occurred while generating the HTML content: {str(e)}")

    elif page == "Admin Interface":
        admin_auth()
        if st.session_state.authenticated:
            admin_interface()

    elif page == "About":
        st.markdown("""
        ## About the Custom Prompt Generator

        This application uses advanced AI models to generate creative and engaging prompts based on your input. It's designed to help writers, educators, and creatives overcome writer's block and spark new ideas.

        ### How it works:

        1. Enter a topic or subject
        2. Choose an AI model
        3. Set the number of prompts you want
        4. Adjust the creativity level
        5. Optionally select a template, enter a custom template, or choose hidden prompts
        6. Generate your custom prompts!

        ### Features:
        - Multiple AI models to choose from
        - Adjustable creativity settings
        - Custom prompt templates
        - Hidden prompts for additional inspiration
        - Export options (CSV and HTML)
        - Categorized prompts for easy organization

        Enjoy using the Custom Prompt Generator for your creative projects!
        """)

def admin_interface():
    st.header("🔒 Admin Interface")

    # Load templates and hidden prompts
    templates = load_templates()
    hidden_prompts = load_hidden_prompts()

    # Template Management
    st.subheader("Manage Templates")

    # Add a new template
    with st.expander("➕ Add New Template"):
        template_name = st.text_input("Template Name")
        template_content = st.text_area("Template Content (use {subject} as a placeholder)")
        if st.button("Add Template"):
            if template_name and template_content:
                if "{subject}" in template_content:
                    templates[template_name] = template_content
                    save_templates(templates)
                    st.success(f"Template '{template_name}' added.")
                else:
                    st.error("Template content must include the {subject} placeholder.")
            else:
                st.error("Please provide a template name and content.")

    # Edit existing templates
    if templates:
        with st.expander("✏️ Edit Existing Templates"):
            selected_template = st.selectbox("Select a template to edit", list(templates.keys()))
            new_name = st.text_input("New Template Name", value=selected_template)
            new_content = st.text_area("New Template Content", value=templates[selected_template])
            if st.button("Update Template"):
                if new_name and new_content:
                    if "{subject}" in new_content:
                        del templates[selected_template]
                        templates[new_name] = new_content
                        save_templates(templates)
                        st.success(f"Template '{new_name}' updated.")
                    else:
                        st.error("Template content must include the {subject} placeholder.")
                else:
                    st.error("Please provide a new name and content.")

    # Delete templates
    if templates:
        with st.expander("🗑️ Delete Templates"):
            templates_to_delete = st.multiselect("Select templates to delete", list(templates.keys()))
            if st.button("Delete Selected Templates"):
                if templates_to_delete:
                    for tmpl in templates_to_delete:
                        del templates[tmpl]
                    save_templates(templates)
                    st.success("Selected templates have been deleted.")
                else:
                    st.error("No templates selected for deletion.")

    # Hidden Prompts Management
    st.subheader("Manage Hidden Prompts")

    # Add a new hidden prompt
    with st.expander("➕ Add New Hidden Prompt"):
        hidden_prompt_name = st.text_input("Hidden Prompt Name")
        hidden_prompt_content = st.text_area("Hidden Prompt Content")
        if st.button("Add Hidden Prompt"):
            if hidden_prompt_name and hidden_prompt_content:
                hidden_prompts[hidden_prompt_name] = hidden_prompt_content
                save_hidden_prompts(hidden_prompts)
                st.success(f"Hidden prompt '{hidden_prompt_name}' added.")
            else:
                st.error("Please provide a hidden prompt name and content.")

    # Edit existing hidden prompts
    if hidden_prompts:
        with st.expander("✏️ Edit Existing Hidden Prompts"):
            selected_hidden_prompt = st.selectbox("Select a hidden prompt to edit", list(hidden_prompts.keys()))
            new_hidden_name = st.text_input("New Hidden Prompt Name", value=selected_hidden_prompt)
            new_hidden_content = st.text_area("New Hidden Prompt Content", value=hidden_prompts[selected_hidden_prompt])
            if st.button("Update Hidden Prompt"):
                if new_hidden_name and new_hidden_content:
                    del hidden_prompts[selected_hidden_prompt]
                    hidden_prompts[new_hidden_name] = new_hidden_content
                    save_hidden_prompts(hidden_prompts)
                    st.success(f"Hidden prompt '{new_hidden_name}' updated.")
                else:
                    st.error("Please provide a new name and content for the hidden prompt.")

    # Delete hidden prompts
    if hidden_prompts:
        with st.expander("🗑️ Delete Hidden Prompts"):
            hidden_prompts_to_delete = st.multiselect("Select hidden prompts to delete", list(hidden_prompts.keys()))
            if st.button("Delete Selected Hidden Prompts"):
                if hidden_prompts_to_delete:
                    for prompt in hidden_prompts_to_delete:
                        del hidden_prompts[prompt]
                    save_hidden_prompts(hidden_prompts)
                    st.success("Selected hidden prompts have been deleted.")
                else:
                    st.error("No hidden prompts selected for deletion.")

if __name__ == "__main__":
    main()
