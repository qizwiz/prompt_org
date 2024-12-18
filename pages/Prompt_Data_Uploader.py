# pages/Prompt_Data_Uploader.py

import streamlit as st
import pandas as pd
import json
import base64
import os
from utils import process_csv, process_json, generate_html_content

def main():
    st.title("📥 Prompt Data Uploader")

    # Upload option selection
    upload_option = st.selectbox(
        "Select Upload Option",
        (
            "Option 1: [Letter, Prompt Name, Category, Prompt Text]",
            "Option 2: [Letter, Persona Name, Category, ImageURL, Prompt Text]",
        ),
    )

    has_image_url = upload_option == "Option 2: [Letter, Persona Name, Category, ImageURL, Prompt Text]"

    # File uploader
    uploaded_file = st.file_uploader("Upload your CSV or JSON file", type=["csv", "json"])

    if uploaded_file is not None:
        # Extract the file name without extension for the header title
        file_name = uploaded_file.name
        header_title = os.path.splitext(file_name)[0].replace('_', ' ').title()

        try:
            if uploaded_file.type == "application/json" or uploaded_file.name.endswith('.json'):
                # Process JSON file
                data = json.load(uploaded_file)
                data = process_json(data, has_image_url, upload_option)
                st.success("JSON file processed successfully.")
                st.write("Processed Data:")
                st.write(pd.DataFrame(data))
            else:
                # Process CSV file
                df = pd.read_csv(uploaded_file)
                st.success("CSV file uploaded successfully.")
                st.write("Uploaded CSV Data:")
                st.write(df)
                data = process_csv(df, has_image_url, upload_option)
                st.success("CSV file processed successfully.")
                st.write("Processed Data:")
                st.write(pd.DataFrame(data))

            # Generate HTML content
            html_content = generate_html_content(data, has_image_url, theme="light", header_title=header_title)

            # Provide download link for the generated HTML
            b64 = base64.b64encode(html_content.encode()).decode()
            href = f'<a href="data:text/html;base64,{b64}" download="{header_title}.html">📥 Download Generated HTML</a>'
            st.markdown(href, unsafe_allow_html=True)

            # Display the HTML content in an iframe
            st.components.v1.html(html_content, height=600, scrolling=True)

        except ValueError as ve:
            st.error(f"Data validation error: {ve}")
        except json.JSONDecodeError as jde:
            st.error(f"Invalid JSON file: {jde}")
        except pd.errors.ParserError as pe:
            st.error(f"CSV parsing error: {pe}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()