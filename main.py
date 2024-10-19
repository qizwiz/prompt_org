import streamlit as st
import requests
import json
import pandas as pd
import logging
import os
import base64
from utils import generate_html_content, AVAILABLE_MODELS

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

        prompt = f"Generate {num_prompts} unique and creative prompts about {topic}. Each prompt should be engaging and thought-provoking."

        try:
            response = requests.post(
                "https://api.openai.com/v1/engines/" + AVAILABLE_MODELS[model] + "/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
                },
                json={
                    "prompt": prompt,
                    "max_tokens": max_tokens,
                    "n": 1,
                    "stop": None,
                    "temperature": creativity,
                },
            )

            response.raise_for_status()
            result = response.json()

            if "choices" in result and len(result["choices"]) > 0:
                generated_text = result["choices"][0]["text"].strip()
                prompts = [p.strip() for p in generated_text.split("\n") if p.strip()]
                
                generated_prompts = []
                for i, p in enumerate(prompts, 1):
                    generated_prompts.append({"id": i, "prompt": p})

                st.subheader("Generated Prompts:")
                for item in generated_prompts:
                    st.write(f"{item['id']}. {item['prompt']}")

                st.session_state.generated_prompts = generated_prompts
            else:
                st.error("No prompts were generated. Please try again.")
        except requests.exceptions.RequestException as e:
            st.error(f"An error occurred: {str(e)}")

    if 'generated_prompts' in st.session_state and st.session_state.generated_prompts:
        generated_prompts = st.session_state.generated_prompts

        st.subheader("Prompt Details")
        df = pd.DataFrame(generated_prompts)
        st.dataframe(df)

        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="generated_prompts.csv">Download CSV File</a>'
        st.markdown(href, unsafe_allow_html=True)

        generate_html = st.button("🖥️ Generate HTML")
        if generate_html:
            try:
                logging.info("Generate HTML button clicked")
                logging.info(f"Generating HTML content for {len(generated_prompts)} prompts")
                logging.debug(f"Generated prompts content: {json.dumps(generated_prompts, indent=2)}")
                
                header_title = "Generated Prompts"
                theme = "light"
                html_content = generate_html_content(generated_prompts, has_image_url=False, theme=theme, header_title=header_title)

                logging.info(f"HTML content generated successfully. Length: {len(html_content)}")
                logging.debug(f"First 200 characters of HTML content: {html_content[:200]}")

                b64 = base64.b64encode(html_content.encode()).decode()
                href = f'<a href="data:text/html;base64,{b64}" download="{header_title}.html">📥 Download Generated HTML</a>'
                st.markdown(href, unsafe_allow_html=True)

                st.markdown(f"<h3>Generated HTML Preview:</h3>", unsafe_allow_html=True)
                st.markdown(html_content, unsafe_allow_html=True)
                logging.info("HTML content displayed successfully")
            except Exception as e:
                logging.error(f"Error generating or displaying HTML content: {str(e)}")
                st.error(f"An error occurred while generating the HTML content: {str(e)}")

if __name__ == "__main__":
    main()
