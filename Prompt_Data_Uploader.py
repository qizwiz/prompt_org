# pages/Prompt_Data_Uploader.py

import streamlit as st
import pandas as pd
import json
import base64
import os
from utils import process_csv, process_json, generate_html_content

def main():
    st.title("📥 Prompt Data Uploader")

    upload_option = st.selectbox(
        "Select Upload Option",
        (
            "Option 1: [Letter, Prompt Name, Category, Prompt Text]",
            "Option 2: [Letter, Persona Name, Category, ImageURL, Prompt Text]",
        ),
    )

    has_image_url = upload_option == "Option 2: [Letter, Persona Name, Category, ImageURL, Prompt Text]"

    uploaded_file = st.file_uploader("Upload your CSV or JSON file", type=["csv", "json"])

    if uploaded_file is not None:
        # Extract the file name without extension for the header title
        file_name = uploaded_file.name
        header_title = os.path.splitext(file_name)[0].replace('_', ' ').title()

        try:
            if uploaded_file.type == "application/json":
                data = json.load(uploaded_file)
                data = process_json(data, has_image_url, upload_option)
                st.write("Processed JSON Data:")
                st.write(pd.DataFrame(data))  # Debugging statement
            else:
                df = pd.read_csv(uploaded_file)
                st.write("Uploaded CSV Data:")
                st.write(df)  # Debugging statement
                data = process_csv(df, has_image_url, upload_option)
                st.write("Processed CSV Data:")
                st.write(pd.DataFrame(data))  # Debugging statement

            # Generate HTML content
            html_content = generate_html_content(data, has_image_url, theme="light", header_title=header_title)

            # Provide download link for the generated HTML
            b64 = base64.b64encode(html_content.encode()).decode()
            href = f'<a href="data:text/html;base64,{b64}" download="{header_title}.html">📥 Download Generated HTML</a>'
            st.markdown(href, unsafe_allow_html=True)

            # Optionally display the HTML content in an iframe
            st.components.v1.html(html_content, height=600, scrolling=True)

        except Exception as e:
            st.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
