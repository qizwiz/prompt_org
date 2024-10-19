import streamlit as st
import requests
import json
import pandas as pd
import logging
import os
import base64
import re
from utils import generate_html_content, AVAILABLE_MODELS

def parse_ai_response(response_text):
    try:
        # Try parsing the entire response as JSON
        return json.loads(response_text)
    except json.JSONDecodeError:
        # If that fails, try to extract JSON-like structures
        json_like = re.findall(r'\{(?:[^{}]|(?R))*\}', response_text)
        if json_like:
            try:
                return [json.loads(item) for item in json_like]
            except json.JSONDecodeError:
                pass
        
        # If all else fails, fall back to simple text-based parsing
        prompts = []
        lines = response_text.split('\n')
        for line in lines:
            if line.strip():
                parts = line.split(':', 1)
                if len(parts) == 2:
                    prompts.append({
                        'Letter': parts[0].strip()[0],
                        'PromptName': parts[0].strip(),
                        'Category': 'General',  # Default category
                        'PromptText': parts[1].strip()
                    })
        return prompts

def main():
    st.set_page_config(page_title="Prompt Generator", page_icon="🤖", layout="wide")
    st.title("🤖 Prompt Generator")

    # Initialize session state for generated_prompts
    if "generated_prompts" not in st.session_state:
        st.session_state.generated_prompts = []

    with st.sidebar:
        st.header("Configuration")
        model = st.selectbox("Select Model", list(AVAILABLE_MODELS.keys()))
        num_prompts = st.number_input("Number of Prompts", min_value=1, max_value=10, value=3)
        topic = st.text_input("Topic")
        creativity = st.slider("Creativity", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
        max_tokens = st.number_input("Max Tokens", min_value=50, max_value=500, value=150, step=10)
        submit_button = st.button("Generate Prompts")

    if submit_button:
        if not topic:
            st.warning("Please enter a topic.")
            return

        prompt = f"Generate {num_prompts} unique and creative prompts about {topic}. Each prompt should be engaging and thought-provoking. For each prompt, provide a single letter identifier, a prompt name, and a category. Format the output as a list of JSON objects, each containing 'Letter', 'PromptName', 'Category', and 'PromptText' fields."

        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
                },
                json={
                    "model": AVAILABLE_MODELS[model],
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
                generated_prompts = parse_ai_response(generated_text)

                if not generated_prompts:
                    st.error("Failed to parse the generated prompts. Please try again.")
                    return

                st.subheader("Generated Prompts:")
                for item in generated_prompts:
                    st.write(f"{item['Letter']}. {item['PromptName']} ({item['Category']}): {item['PromptText']}")

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

        generate_html = st.button("🖥️ Generate HTML")
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

if __name__ == "__main__":
    main()
