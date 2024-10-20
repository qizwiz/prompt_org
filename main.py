import streamlit as st
import requests
import json
import pandas as pd
import logging
import os
import base64
from utils import generate_html_content, AVAILABLE_MODELS

# Set up logging
logging.basicConfig(
    filename='app.log',
    level=logging.DEBUG,
    format='%(asctime)s:%(levelname)s:%(message)s'
)

def parse_ai_response(response_text):
    """
    Parse the AI response from JSON or extract JSON objects from text.
    """
    try:
        parsed_data = json.loads(response_text)
        if isinstance(parsed_data, list):
            return parsed_data
    except json.JSONDecodeError:
        import re
        # Find all JSON objects in the response text
        json_objects = re.findall(r'\{.*?\}', response_text, re.DOTALL)
        parsed_data = []
        for obj in json_objects:
            try:
                parsed_obj = json.loads(obj)
                # Check for required keys
                if all(key in parsed_obj for key in ['Letter', 'PromptName', 'Categories', 'PromptText']):
                    parsed_data.append(parsed_obj)
            except json.JSONDecodeError:
                continue
    return parsed_data

def load_data():
    try:
        with open('prompt_data.pkl', 'rb') as f:
            data = pd.read_pickle(f)
        logging.info(f"Loaded data with {len(data)} prompts")
        return data
    except FileNotFoundError:
        logging.warning("prompt_data.pkl not found. Creating new DataFrame.")
        return pd.DataFrame(columns=["Categories", "PromptName", "PromptText", "Model"])

def main():
    st.set_page_config(page_title="Custom Prompt Generator", page_icon="🧠")

    # Sidebar Navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Go to", ["User Interface", "Admin Interface", "About"])

    if page == "User Interface":
        user_interface()
    elif page == "Admin Interface":
        st.header("🔒 Admin Interface")
        st.info("Please navigate to the Admin Interface page to access admin features.")
    elif page == "About":
        about_page()

def user_interface():
    st.title("🧠 Custom Prompt Generator")

    st.markdown("""
    Welcome to the **Custom Prompt Generator**! Generate creative and detailed prompts tailored to your needs. More at information can be found at bottalks.promtasticworld.com https://youtu.be/N6Lvx4G9SLM v1.0.0
    """)

    # Initialize session state for generated prompts
    if "generated_prompts" not in st.session_state:
        st.session_state.generated_prompts = []

    # Load existing prompts
    existing_prompts = load_data()
    logging.debug(f"Loaded existing prompts: {existing_prompts.to_dict('records')}")

    # Input form for prompt details
    with st.form(key='prompt_form'):
        # Add category selection
        all_categories = set(cat.strip() for cats in existing_prompts['Categories'] for cat in cats.split(',') if cats)
        categories = [""] + sorted(all_categories)
        selected_category = st.selectbox("Select Category", categories)
        logging.debug(f"All categories: {categories}")
        logging.debug(f"Selected category: {selected_category}")

        # Update prompt name selection
        if selected_category:
            prompt_names = existing_prompts[existing_prompts['Categories'].str.contains(selected_category, case=False, na=False)]['PromptName'].tolist()
            logging.debug(f"Filtered prompts for category '{selected_category}': {prompt_names}")
        else:
            prompt_names = existing_prompts['PromptName'].tolist()
            logging.debug(f"All prompts (no category selected): {prompt_names}")

        prompt_names = [""] + sorted(prompt_names)
        selected_prompt = st.selectbox("Select Prompt", prompt_names)
        logging.debug(f"Selected prompt: {selected_prompt}")

        # Topic input
        topic = st.text_input("Topic:")

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
            value=10,
            step=1,
            help="Specify how many prompts you want to generate."
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
        # Include an API Key input field if not set in environment variables
        if not os.getenv('OPENROUTER_API_KEY'):
            openrouter_api_key = st.text_input(
                "**OpenRouter API Key:**",
                type="password",
                help="Enter your OpenRouter API Key."
            )
        else:
            openrouter_api_key = os.getenv('OPENROUTER_API_KEY')

        # Update the submit button condition
        submit_button = st.form_submit_button(label='Generate Prompts')

    if submit_button:
        logging.info(f"Generate Prompts button clicked. Selected prompt: {selected_prompt}, Topic: {topic}")
        if selected_prompt and topic:
            # Use both selected prompt and topic
            selected_prompt_data = existing_prompts[existing_prompts['PromptName'] == selected_prompt].iloc[0]
            ai_prompt = f"""
Based on the prompt: {selected_prompt_data['PromptText']}

Generate {num_prompts} unique, long, and detailed writing prompts about the topic '{topic}'.

Each prompt should include:
- **Letter**: The first letter of the 'PromptName'.
- **PromptName**: A catchy and relevant title starting with the specified 'Letter'.
- **Categories**: Comma-separated categories or tags.
- **PromptText**: A detailed description with rich context.

Format:
[
  {{
    "Letter": "A",
    "PromptName": "Example Title",
    "Categories": "Category1, Category2",
    "PromptText": "Detailed prompt text."
  }},
  ...
]
"""
        elif selected_prompt:
            # Use only the selected prompt
            selected_prompt_data = existing_prompts[existing_prompts['PromptName'] == selected_prompt].iloc[0]
            st.session_state.generated_prompts = [{
                "Letter": selected_prompt_data['PromptName'][0],
                "PromptName": selected_prompt_data['PromptName'],
                "Categories": selected_prompt_data['Categories'],
                "PromptText": selected_prompt_data['PromptText']
            }]
            st.subheader("Selected Prompt:")
            st.markdown(f"**{selected_prompt_data['PromptName']}** ({selected_prompt_data['Categories']}):\n{selected_prompt_data['PromptText']}")
        elif topic:
            # Generate new prompts based on the topic
            ai_prompt = f"""
Generate {num_prompts} unique, long, and detailed writing prompts about the topic '{topic}'.

Each prompt should include:
- **Letter**: The first letter of the 'PromptName'.
- **PromptName**: A catchy and relevant title starting with the specified 'Letter'.
- **Categories**: Comma-separated categories or tags.
- **PromptText**: A detailed description with rich context.

Format:
[
  {{
    "Letter": "A",
    "PromptName": "Example Title",
    "Categories": "Category1, Category2",
    "PromptText": "Detailed prompt text."
  }},
  ...
]
"""
        else:
            st.warning("Please enter a topic or select a prompt.")
            return

        if (selected_prompt and topic) or topic:
            try:
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {openrouter_api_key}",
                }
                payload = {
                    "model": AVAILABLE_MODELS[model]['id'],
                    "messages": [
                        {"role": "user", "content": ai_prompt.strip()}
                    ],
                    "max_tokens": max_tokens,
                    "temperature": creativity,
                }
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=60  # Add timeout to prevent hanging
                )

                response.raise_for_status()
                result = response.json()

                if "choices" in result and len(result["choices"]) > 0:
                    generated_text = result["choices"][0]["message"]["content"].strip()
                    logging.debug(f"Generated text: {generated_text}")
                    generated_prompts = parse_ai_response(generated_text)

                    if not generated_prompts:
                        st.error("Failed to parse the generated prompts. Please try again.")
                    else:
                        st.subheader("Generated Prompts:")
                        for idx, item in enumerate(generated_prompts, 1):
                            st.markdown(f"**{idx}. {item['PromptName']}** ({item['Categories']}):\n{item['PromptText']}\n")
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

                    b64_html = base64.b64encode(html_content.encode()).decode()
                    href_html = f'<a href="data:text/html;base64,{b64_html}" download="{header_title}.html">📥 Download Generated HTML</a>'
                    st.markdown(href_html, unsafe_allow_html=True)

                    st.markdown(f"<h3>Generated HTML Preview:</h3>", unsafe_allow_html=True)
                    st.components.v1.html(html_content, height=600, scrolling=True)
                    logging.info("HTML content displayed successfully")
                except Exception as e:
                    logging.error(f"Error generating or displaying HTML content: {str(e)}")
                    st.error(f"An error occurred while generating the HTML content: {str(e)}")

def about_page():
    st.markdown("""
    ## About the Custom Prompt Generator

    This application uses advanced AI models to generate creative and engaging prompts based on your input. It's designed to help writers, educators, and creatives overcome writer's block and spark new ideas.

    ### How it works:
    1. Enter a topic or subject, or select an existing prompt.
    2. Choose an AI model (if generating new prompts).
    3. Set the number of prompts you want (if generating new prompts).
    4. Adjust the creativity level (if generating new prompts).
    5. Generate your custom prompts or use the selected prompt!

    ### Features:
    - Multiple AI models to choose from.
    - Adjustable creativity settings.
    - Export options (CSV and HTML).
    - Categorized prompts for easy organization.
    - Admin interface for managing prompts and categories.
    - Option to select existing prompts by category.

    Enjoy using the Custom Prompt Generator for your creative projects!
    """)

if __name__ == "__main__":
    main()
