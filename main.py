import streamlit as st
import requests
import json
import pandas as pd
import logging
import os
import base64
from utils import generate_html_content

# Set up logging to monitor issues in the app
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

# OpenRouter API Key
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    st.error("OpenRouter API Key not found. Please set the OPENROUTER_API_KEY environment variable.")
    st.stop()

# Function to load templates from a file
def load_templates():
    if 'templates' not in st.session_state:
        if os.path.exists('templates.json'):
            with open('templates.json', 'r') as f:
                st.session_state.templates = json.load(f)
            logging.info("Templates loaded from file.")
        else:
            st.session_state.templates = {}
            logging.info("No templates file found. Starting with an empty template list.")

# Function to save templates to a file
def save_templates():
    with open('templates.json', 'w') as f:
        json.dump(st.session_state.templates, f)
    logging.info("Templates saved to file.")

# Function to handle admin authentication
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

# Function to display the admin interface
def admin_interface():
    st.header("🔒 Admin Interface")

    # Load templates
    load_templates()

    # Template Management
    st.subheader("Manage Templates")

    # Add a new template
    with st.expander("➕ Add New Template"):
        template_name = st.text_input("Template Name")
        template_content = st.text_area("Template Content (use {subject} and {input} as placeholders)")
        category = st.text_input("Category")
        if st.button("Add Template"):
            if template_name and template_content and category:
                if "{subject}" in template_content and "{input}" in template_content:
                    st.session_state.templates[template_name] = {
                        "content": template_content,
                        "category": category
                    }
                    save_templates()
                    st.success(f"Template '{template_name}' added.")
                else:
                    st.error("Template content must include both {subject} and {input} placeholders.")
            else:
                st.error("Please provide a template name, content, and category.")

    # Edit existing templates
    if st.session_state.templates:
        with st.expander("✏️ Edit Existing Templates"):
            selected_template = st.selectbox("Select a template to edit", list(st.session_state.templates.keys()))
            new_name = st.text_input("New Template Name", value=selected_template)
            new_content = st.text_area("New Template Content", value=st.session_state.templates[selected_template]["content"])
            new_category = st.text_input("New Category", value=st.session_state.templates[selected_template]["category"])
            if st.button("Update Template"):
                if new_name and new_content and new_category:
                    if "{subject}" in new_content and "{input}" in new_content:
                        del st.session_state.templates[selected_template]
                        st.session_state.templates[new_name] = {
                            "content": new_content,
                            "category": new_category
                        }
                        save_templates()
                        st.success(f"Template '{new_name}' updated.")
                    else:
                        st.error("Template content must include both {subject} and {input} placeholders.")
                else:
                    st.error("Please provide a new name, content, and category.")

    # Delete templates
    if st.session_state.templates:
        with st.expander("🗑️ Delete Templates"):
            templates_to_delete = st.multiselect("Select templates to delete", list(st.session_state.templates.keys()))
            if st.button("Delete Selected Templates"):
                if templates_to_delete:
                    for tmpl in templates_to_delete:
                        del st.session_state.templates[tmpl]
                    save_templates()
                    st.success("Selected templates have been deleted.")
                else:
                    st.error("No templates selected for deletion.")

# Function to generate prompt text
def call_openrouter_api(prompt):
    logging.info("Sending prompt to OpenRouter API.")
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            data=json.dumps({
                "model": "google/gemini-flash-1.5-8b-exp",
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }),
            timeout=30  # Set a timeout of 30 seconds
        )

        if response.status_code == 200:
            response_data = response.json()
            prompt_text = response_data.get('choices', [{}])[0].get('message', {}).get('content', "").strip()
            logging.info("Received prompt text from OpenRouter API.")
            return prompt_text
        else:
            logging.warning(f"API Error {response.status_code}: {response.text}")
            return f"Error: {response.status_code}, {response.text}"
    except requests.exceptions.Timeout:
        st.error("The request to the API timed out. Please try again later.")
        return "Request Timed Out"
    except Exception as e:
        logging.error(f"Exception occurred while generating prompt text: {e}")
        return f"Exception occurred: {e}"

# Function to generate prompt name and category using AI
def generate_name_and_category(subject, prompt_input, prompt_text):
    logging.info("Generating prompt name and category using AI.")
    prompt = (
        f"Based on the following information, generate a suitable prompt name and assign a relevant category.\n\n"
        f"Subject: {subject}\n"
        f"Input: {prompt_input}\n"
        f"Generated Prompt: {prompt_text}\n\n"
        f"Respond in the following JSON format:\n"
        f"{{\n"
        f"  \"Prompt Name\": \"Your Prompt Name\",\n"
        f"  \"Category\": \"Your Category\"\n"
        f"}}"
    )

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            data=json.dumps({
                "model": "google/gemini-flash-1.5-8b-exp",
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }),
            timeout=30  # Set a timeout of 30 seconds
        )

        if response.status_code == 200:
            response_data = response.json()
            ai_response = response_data.get('choices', [{}])[0].get('message', {}).get('content', "").strip()
            logging.info("Received name and category from OpenRouter API.")

            try:
                metadata = json.loads(ai_response)
                prompt_name = metadata.get("Prompt Name", "Unnamed Prompt")
                category = metadata.get("Category", "Uncategorized")
                return prompt_name, category
            except json.JSONDecodeError:
                logging.error("Failed to parse AI response for name and category.")
                st.error("Failed to parse the AI response for prompt name and category.")
                return "Unnamed Prompt", "Uncategorized"
        else:
            logging.warning(f"API Error {response.status_code} while generating name and category: {response.text}")
            st.error(f"Error generating name and category: {response.status_code}")
            return "Unnamed Prompt", "Uncategorized"
    except requests.exceptions.Timeout:
        logging.error("The request to the API for name and category timed out.")
        st.error("The request to the API for name and category timed out. Please try again later.")
        return "Unnamed Prompt", "Uncategorized"
    except Exception as e:
        logging.error(f"Exception occurred while generating name and category: {e}")
        st.error(f"Exception occurred while generating name and category: {e}")
        return "Unnamed Prompt", "Uncategorized"

# Main Streamlit App
def main():
    st.set_page_config(page_title="Custom Prompt Generator", page_icon="🧠")

    # Sidebar Navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Go to", ["User Interface", "Admin Interface", "Prompt Data Uploader"])

    if page == "Admin Interface":
        admin_auth()
        if st.session_state.authenticated:
            admin_interface()
    elif page == "Prompt Data Uploader":
        from pages.Prompt_Data_Uploader import main as uploader_main
        uploader_main()
    else:
        # User Interface
        st.title("🧠 Custom Prompt Generator")

        st.markdown("""
        Welcome to the **Custom Prompt Generator**! Generate creative and detailed prompts tailored to your needs.
        """)

        # Load templates
        load_templates()

        # Input form for prompt details
        with st.form(key='prompt_form'):
            subject = st.text_input(
                "**Subject:**",
                placeholder="e.g., AI, Quantum Computing, Climate Change",
                help="Enter the main subject for the prompt."
            )
            prompt_input = st.text_input(
                "**Input for the Prompts:**",
                placeholder="e.g., Focus on AI ethics",
                help="Provide additional details or context for the prompt."
            )
            template_names = ["None"] + list(st.session_state.templates.keys())
            selected_template = st.selectbox(
                "**Select a Prompt Template:**",
                template_names,
                help="Select a prompt template to use."
            )
            prompt_count = st.number_input(
                "**Number of Prompts to Generate:**",
                min_value=1,
                max_value=10,
                value=1,
                step=1,
                help="Specify how many prompts you want to generate."
            )
            submit_button = st.form_submit_button(label='Generate Prompts')

        # Generate prompts when form is submitted
        if submit_button:
            # Input validation to ensure required fields are filled
            if not subject.strip() or not prompt_input.strip():
                st.error("Please fill in both **Subject** and **Input for the Prompts** fields.")
            elif selected_template == "None":
                st.error("Please select a prompt template.")
            else:
                with st.spinner('Generating prompts...'):
                    generated_prompts = []

                    for i in range(int(prompt_count)):
                        # Use the selected prompt template
                        template_info = st.session_state.templates[selected_template]
                        template = template_info["content"]
                        formatted_prompt = template.replace("{subject}", subject).replace("{input}", prompt_input)
                        ai_response = call_openrouter_api(formatted_prompt)

                        # Generate prompt name and category using AI
                        prompt_name, category = generate_name_and_category(subject, prompt_input, ai_response)

                        # Determine the letter based on the first character of the prompt name
                        letter = prompt_name[0].upper() if prompt_name else "U"

                        # Store the generated prompt details
                        generated_prompts.append({
                            "Letter": letter,
                            "Prompt Name": prompt_name,
                            "Category": category,
                            "Prompt Text": ai_response
                        })

                # Display the generated prompts in a table
                if generated_prompts:
                    df = pd.DataFrame(generated_prompts)
                    st.success('📄 Prompts generated successfully!')
                    st.dataframe(df, use_container_width=True)

                    # Provide an option to download the generated prompts as CSV
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Prompts as CSV",
                        data=csv,
                        file_name='generated_prompts.csv',
                        mime='text/csv',
                    )

                    # Generate and download HTML
                    generate_html = st.button("🖥️ Generate HTML")
                    if generate_html:
                        header_title = "Generated Prompts"
                        theme = "light"
                        html_content = generate_html_content(generated_prompts, has_image_url=False, theme=theme, header_title=header_title)

                        b64 = base64.b64encode(html_content.encode()).decode()
                        href = f'<a href="data:text/html;base64,{b64}" download="{header_title}.html">📥 Download Generated HTML</a>'
                        st.markdown(href, unsafe_allow_html=True)

                        st.components.v1.html(html_content, height=600, scrolling=True)

if __name__ == "__main__":
    main()
