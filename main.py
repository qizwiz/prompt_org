
import streamlit as st
import requests
import json
import pandas as pd
import logging
import os
import base64
from utils import generate_html_content, AVAILABLE_MODELS

# Set up logging
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

def parse_ai_response(response_text):
    try:
        # Attempt to parse the entire response as JSON
        parsed_data = json.loads(response_text)
        if isinstance(parsed_data, list):
            return parsed_data
    except json.JSONDecodeError:
        # If parsing the entire response fails, try to find and parse individual JSON objects
        json_objects = re.findall(r'\{[^{}]*\}', response_text)
        parsed_data = []
        for obj in json_objects:
            try:
                parsed_obj = json.loads(obj)
                if all(key in parsed_obj for key in ['Letter', 'PromptName', 'Categories', 'PromptText']):
                    parsed_data.append(parsed_obj)
            except json.JSONDecodeError:
                continue
    return parsed_data

def main():
    st.set_page_config(page_title="Custom Prompt Generator", page_icon="🧠")

    # Sidebar Navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Go to", ["User Interface", "Admin Interface", "About"])

    if page == "User Interface":
        st.title("🧠 Custom Prompt Generator")

        st.markdown("""
        Welcome to the **Custom Prompt Generator**! Generate creative and detailed prompts tailored to your needs.
        """)

        # Initialize session state for generated prompts
        if "generated_prompts" not in st.session_state:
            st.session_state.generated_prompts = []

        # Input form for prompt details
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
            max_tokens = st.slider(
                "**Max Tokens:**",
                min_value=50,
                max_value=min(500, AVAILABLE_MODELS[model]['context_tokens']),
                value=min(200, AVAILABLE_MODELS[model]['context_tokens']),
                step=50,
                help="Set the maximum number of tokens for each prompt."
            )
            creativity = st.slider(
                "**Creativity Level:**",
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

            prompt = f"""Generate {num_prompts} unique and creative prompts about {topic}. Each prompt should be engaging and thought-provoking.

            Format the output as a list of JSON objects, each containing 'Letter', 'PromptName', 'Categories', and 'PromptText' fields. Ensure that the letter and prompt name are closely related to the prompt's content.

            Example format:
            [
              {{
                "Letter": "A",
                "PromptName": "Artistic Exploration",
                "Categories": "Creativity, Visual Arts, Imagination",
                "PromptText": "Describe a world where colors have sounds and music creates visible patterns in the air."
              }},
              ...
            ]
            """

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
                            {"role": "user", "content": prompt}
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
                    for item in generated_prompts:
                        st.write(f"{item['Letter']}. {item['PromptName']} ({item['Categories']}): {item['PromptText']}")

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
            href = f'<a href="data:file/csv;base64,{b64}" download="generated_prompts.csv">Download CSV File</a>'
            st.markdown(href, unsafe_allow_html=True)

            with st.form(key='generate_html_form'):
                generate_html = st.form_submit_button("🖥️ Generate HTML")
                if generate_html:
                    try:
                        logging.info("Generate HTML button clicked")
                        logging.info(f"Generating HTML content for {len(st.session_state.generated_prompts)} prompts")
                        
                        header_title = "Generated Prompts"
                        theme = "light"
                        html_content = generate_html_content(st.session_state.generated_prompts, has_image_url=False, theme=theme, header_title=header_title)

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
        st.warning("Admin interface not implemented yet.")

    elif page == "About":
        st.markdown("""
        ## About the Custom Prompt Generator

        This application uses advanced AI models to generate creative and engaging prompts based on your input. It's designed to help writers, educators, and creatives overcome writer's block and spark new ideas.

        ### How it works:
        1. Enter a topic or subject
        2. Choose an AI model
        3. Set the number of prompts you want
        4. Adjust the creativity level
        5. Generate your custom prompts!

        ### Features:
        - Multiple AI models to choose from
        - Adjustable creativity settings
        - Export options (CSV and HTML)
        - Categorized prompts for easy organization

        Enjoy using the Custom Prompt Generator for your creative projects!
        """)

if __name__ == "__main__":
    main()
