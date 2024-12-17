import json
import logging
import os
import re

import pandas as pd
import requests
import streamlit as st
from jsonschema import ValidationError, validate

from utils import AVAILABLE_MODELS, process_csv, process_json

# --- Logging Configuration ---
logging.basicConfig(
    filename="app.log",
    level=logging.DEBUG,
    format="%(asctime)s:%(levelname)s:%(message)s",
)

# --- Constants ---
DATA_FILE = "prompt_data.parquet"
ADMIN_PASSWORD = "admin123"

PROMPT_SCHEMA = ["Categories", "PromptName", "PromptText", "Model"]
DEFAULT_COLUMNS = pd.Index(PROMPT_SCHEMA, dtype="object")


# --- Utility Functions ---
def safe_load_data():
    """
    Safely load prompt data from Parquet or return an empty DataFrame.
    """
    try:
        if os.path.exists(DATA_FILE):
            data = pd.read_parquet(DATA_FILE)
            if list(data.columns) != PROMPT_SCHEMA:
                raise ValueError("Schema mismatch detected.")
            return data
        return pd.DataFrame([], columns=DEFAULT_COLUMNS)
    except Exception as e:
        logging.error(f"Error loading data: {e}")
        return pd.DataFrame([], columns=DEFAULT_COLUMNS)


def save_data_to_parquet(data):
    """
    Save data to a Parquet file.
    """
    try:
        data.to_parquet(DATA_FILE, index=False)
        logging.info("Data successfully saved to Parquet.")
    except Exception as e:
        logging.error(f"Failed to save data: {e}")
        raise


# Define the expected schema for a valid prompt response
RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "Letter": {"type": "string"},
        "PromptName": {"type": "string"},
        "Categories": {"type": "string"},
        "PromptText": {"type": "string"},
    },
    "required": ["Letter", "PromptName", "Categories", "PromptText"],
}


def parse_api_response(response_text):
    """
    Parse AI API response to extract valid JSON objects and validate schema.
    """
    parsed_data = []
    try:
        # Attempt to parse the response directly as JSON
        response_objects = json.loads(response_text)
        if isinstance(response_objects, list):
            for obj in response_objects:
                try:
                    validate(instance=obj, schema=RESPONSE_SCHEMA)
                    parsed_data.append(obj)
                except ValidationError as e:
                    logging.error(f"Validation error: {e}")
        return parsed_data
    except json.JSONDecodeError:
        # Fallback: Extract potential JSON objects using regex
        json_objects = re.findall(r"\{.*?\}", response_text, re.DOTALL)
        for obj in json_objects:
            try:
                obj_parsed = json.loads(obj)
                validate(instance=obj_parsed, schema=RESPONSE_SCHEMA)
                parsed_data.append(obj_parsed)
            except (json.JSONDecodeError, ValidationError) as e:
                logging.error(f"Skipping invalid object: {e}")
    return parsed_data


def upload_and_process_file(uploaded_file, upload_option):
    if upload_option == "CSV":
        df = pd.read_csv(uploaded_file)
        processed_data = process_csv(df, has_image_url=False, upload_option="Option 1")
    elif upload_option == "JSON":
        data_json = json.loads(uploaded_file.read())
        processed_data = process_json(
            data_json, has_image_url=False, upload_option="Option 1"
        )
    else:
        raise ValueError("Unsupported upload option.")

    return pd.DataFrame(processed_data)  # Ensure return type is DataFrame


def generate_api_payload(prompt, model_id, max_tokens, creativity):
    return {
        "model": model_id,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": creativity,
    }


def call_ai_api(payload):
    """
    Make a call to the AI API.
    """
    headers = {"Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}"}
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions", json=payload, headers=headers
    )
    response.raise_for_status()
    return response.json()


# --- Admin Interface ---
def admin_interface():
    st.title("🔒 Admin Interface")
    if st.text_input("Enter Admin Password:", type="password") != ADMIN_PASSWORD:
        st.error("Incorrect Password. Access Denied.")
        return

    st.success("Access Granted! Welcome, Admin.")
    data = safe_load_data()

    # File Upload Section
    uploaded_file = st.file_uploader("Upload CSV or JSON", type=["csv", "json"])
    if uploaded_file:
        try:
            processed_data = upload_and_process_file(uploaded_file, uploaded_file.type)
            new_data = pd.DataFrame(processed_data, columns=DEFAULT_COLUMNS)
            updated_data = pd.concat([data, new_data], ignore_index=True)
            save_data_to_parquet(updated_data)
            st.success("Data successfully uploaded and updated.")
        except Exception as e:
            st.error(f"Error: {e}")

    # Data Editor Section
    if not data.empty:
        st.subheader("Manage Existing Prompts")
        edited_data = st.data_editor(data)
        if st.button("Save Changes"):
            save_data_to_parquet(edited_data)
            st.success("Changes saved successfully.")


# --- User Interface ---
def user_interface():
    st.title("🧠 Custom Prompt Generator")
    data = safe_load_data()

    # User Inputs
    selected_category = st.selectbox(
        "Select Category", sorted(data["Categories"].dropna().unique())
    )

    selected_prompt = st.selectbox(
        "Select Prompt",
        sorted(
            pd.Series(data.loc[data["Categories"] == selected_category, "PromptName"])
            .dropna()
            .unique()
        ),
    )

    topic = st.text_input("Enter Topic:")
    model = st.selectbox("Select AI Model", AVAILABLE_MODELS.keys())
    num_prompts = st.number_input("Number of Prompts", 1, 20, 5)
    max_tokens = st.slider("Max Tokens", 50, 1000, 500, step=50)
    creativity = st.slider("Creativity", 0.0, 1.0, 0.7, step=0.1)

    # Generate Prompts
    if st.button("Generate Prompts"):
        try:
            prompt = f"Generate {num_prompts} prompts about '{topic}' based on '{selected_prompt}'."
            payload = generate_api_payload(
                prompt, AVAILABLE_MODELS[model]["id"], max_tokens, creativity
            )
            response = call_ai_api(payload)
            generated = parse_api_response(response["choices"][0]["message"]["content"])
            st.write(pd.DataFrame(generated))
        except Exception as e:
            st.error(f"Error: {e}")


# --- Main Navigation ---
def main():
    st.set_page_config(page_title="Custom Prompt Generator", page_icon="🧠")
    page = st.sidebar.selectbox("Navigation", ["User Interface", "Admin Interface"])
    if page == "User Interface":
        user_interface()
    else:
        admin_interface()


if __name__ == "__main__":
    main()
