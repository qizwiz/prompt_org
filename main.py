import streamlit as st
import requests
import json
import pandas as pd
import logging
import os
import base64
from utils import generate_html_content, AVAILABLE_MODELS

# Set up logging
logging.basicConfig(filename='app.log', level=logging.DEBUG,  # Set to DEBUG level
                    format='%(asctime)s:%(levelname)s:%(message)s')

def parse_ai_response(response_text):
    import json
    import re

    # Use regular expression to extract JSON array
    json_match = re.search(r'$$\s*\{.*\}\s*$$', response_text, re.DOTALL)
    if json_match:
        json_text = json_match.group()
        try:
            parsed_data = json.loads(json_text)
            if isinstance(parsed_data, list):
                return parsed_data
        except json.JSONDecodeError as e:
            logging.error(f"JSON decoding error: {e}")
            st.error(f"JSON decoding error: {e}")
    else:
        logging.error("No JSON array found in the AI's response.")
        st.error("No JSON array found in the AI's response.")
    return None

def main():
    st.set_page_config(page_title="Custom Prompt Generator", page_icon="🧠")

    # Sidebar Navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Go to", ["User Interface", "Admin Interface", "About"])

    if page == "User Interface":
        st.title("🧠 Custom Prompt Generator")

        st.markdown("""
        Welcome to the **Custom Prompt Generator**! Generate creative and detailed prompts with ease.
        """)

        # Initialize session state for generated prompts
        if "generated_prompts" not in st.session_state:
            st.session_state.generated_prompts = []

        # Check if prompt types exist
        if "prompt_templates" in st.session_state and st.session_state.prompt_templates:
            types = list(set([pt['type'] for pt in st.session_state.prompt_templates]))
            selected_type = st.selectbox("**Type of Prompt:**", types)
            names = [pt['name'] for pt in st.session_state.prompt_templates if pt['type'] == selected_type]
            selected_name = st.selectbox("**Prompt Name:**", names)

            # Find the selected prompt template
            selected_prompt = next((pt for pt in st.session_state.prompt_templates if pt['type'] == selected_type and pt['name'] == selected_name), None)

            if selected_prompt:
                # Display required input fields based on the placeholders in the template
                placeholders = selected_prompt.get('placeholders', [])
                user_inputs = {}
                with st.form(key='user_input_form'):
                    for placeholder in placeholders:
                        user_input = st.text_input(f"**{placeholder.capitalize()}:**", placeholder=f"Enter {placeholder}")
                        user_inputs[placeholder] = user_input
                    submit_button = st.form_submit_button(label='Generate Prompts')
            else:
                st.error("The selected prompt does not have a valid template.")
                return

        else:
            st.info("No prompt templates available. Please contact the administrator.")
            return

        if 'submit_button' in locals() and submit_button:
            missing_inputs = [key for key, value in user_inputs.items() if not value]
            if missing_inputs:
                st.warning(f"Please provide inputs for: {', '.join(missing_inputs)}")
                return

            # Input form for additional details
            model = st.selectbox(
                "**Select AI Model:**",
                list(AVAILABLE_MODELS.keys()),
                format_func=lambda x: f"{x} (Context tokens: {AVAILABLE_MODELS[x]['context_tokens']})",
                help="Choose the AI model to generate prompts."
            )

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

            # Format the AI prompt using the template and user inputs
            try:
                ai_prompt = selected_prompt['template'].format(**user_inputs)
            except KeyError as e:
                st.error(f"Missing placeholder in template: {e}. Please contact the administrator.")
                return

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
                    logging.debug(f"AI's raw response: {generated_text}")
                    st.write("AI's raw response:")
                    st.write(generated_text)  # Display the AI's response for debugging

                    generated_prompts = parse_ai_response(generated_text)

                    if not generated_prompts:
                        st.error("Failed to parse the generated prompts. Please check the AI's response.")
                        return

                    st.subheader("Generated Prompts:")
                    for idx, item in enumerate(generated_prompts, 1):
                        st.write(f"**{idx}. {item.get('PromptName', 'No Name')}** ({item.get('Categories', '')}):\n{item.get('PromptText', '')}\n")

                    st.session_state.generated_prompts = generated_prompts
                else:
                    st.error("No prompts were generated. Please try again.")
            except requests.exceptions.RequestException as e:
                st.error(f"An error occurred: {str(e)}")

        if st.session_state.generated_prompts:
            st.subheader("Prompt Details")
            df = pd.DataFrame(st.session_state.generated_prompts)
            st.dataframe(df)

            csv = df.to_csv(index=False)
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
                        st.components.v1.html(html_content, height=600, scrolling=True)
                        logging.info("HTML content displayed successfully")
                    except Exception as e:
                        logging.error(f"Error generating or displaying HTML content: {str(e)}")
                        st.error(f"An error occurred while generating the HTML content: {str(e)}")

    elif page == "Admin Interface":
        st.header("🔒 Admin Interface")

        # Initialize session state for prompt templates
        if "prompt_templates" not in st.session_state:
            st.session_state.prompt_templates = []

        # Input form for creating new prompt types and prompt names
        with st.form(key='admin_form'):
            prompt_type = st.text_input("Type of Prompt", placeholder="e.g., Story Idea")
            prompt_name = st.text_input("Prompt Name", placeholder="e.g., Mystery Story Starter")
            prompt_template = st.text_area(
                "Prompt Template",
                placeholder="Enter the AI prompt template. Use placeholders like {topic}, {style}, etc.",
                help="""Define the template to be used to generate prompts.
                Use placeholders that will be filled by user input. For example: {topic}, {audience}, etc."""
            )
            submit_admin = st.form_submit_button("Add Prompt")

        if submit_admin:
            if prompt_type and prompt_name and prompt_template:
                # Extract placeholders from the template
                import re
                placeholders = re.findall(r'{(.*?)}', prompt_template)
                new_prompt = {
                    "type": prompt_type,
                    "name": prompt_name,
                    "template": prompt_template,
                    "placeholders": placeholders
                }
                st.session_state.prompt_templates.append(new_prompt)
                st.success(f"Added new prompt: Type '{prompt_type}', Name '{prompt_name}'.")
            else:
                st.warning("Please enter Type of Prompt, Prompt Name, and Prompt Template.")

        # Display existing prompt templates
        st.subheader("Existing Prompt Templates")
        if st.session_state.prompt_templates:
            for idx, prompt in enumerate(st.session_state.prompt_templates):
                st.write(f"**{idx + 1}. Type:** {prompt['type']}, **Name:** {prompt['name']}")
                st.code(prompt['template'], language='plaintext')
                # Option to delete prompts
                if st.button(f"Delete Prompt {idx + 1}", key=f"delete_{idx}"):
                    st.session_state.prompt_templates.pop(idx)
                    st.experimental_rerun()
        else:
            st.info("No prompt templates added yet.")

    elif page == "About":
        st.markdown("""
        ## About the Custom Prompt Generator

        This application uses advanced AI models to generate creative and engaging prompts based on your selection. It's designed to help users who may not be comfortable creating prompts themselves.

        ### How it works:
        1. Select the type and name of the prompt you want to generate.
        2. Provide minimal required input as prompted (e.g., a topic).
        3. Choose an AI model and adjust settings if desired.
        4. Generate your custom prompts with ease!

        ### Features:
        - Predefined prompt types and names for easy selection.
        - Minimal input required from the user.
        - Adjustable AI model settings.
        - Export options (CSV and HTML).
        - Categorized prompts for easy organization.

        Enjoy using the Custom Prompt Generator to spark your creativity!
        """)

if __name__ == "__main__":
    main()
