import streamlit as st
import pandas as pd
from utils import AVAILABLE_MODELS
import json
import os

def load_data():
    try:
        with open('prompt_data.pkl', 'rb') as f:
            return pd.read_pickle(f)
    except FileNotFoundError:
        return pd.DataFrame(columns=["Letter", "PromptName", "Categories", "PromptText"])

def save_data(data):
    data.to_pickle('prompt_data.pkl')
    st.success("Data saved successfully!")

def admin_interface():
    st.title("🔐 Admin Interface")
    
    # Load existing data
    data = load_data()
    
    # Display existing prompts
    st.subheader("Existing Prompts")
    if not data.empty:
        st.dataframe(data)
    else:
        st.info("No prompts available. Add some below!")
    
    # Add new prompt
    st.subheader("Add New Prompt")
    with st.form("new_prompt_form"):
        letter = st.text_input("Letter", max_chars=1)
        prompt_name = st.text_input("Prompt Name")
        categories = st.text_input("Categories (comma-separated)")
        prompt_text = st.text_area("Prompt Text")
        model = st.selectbox("AI Model", list(AVAILABLE_MODELS.keys()))
        
        if st.form_submit_button("Add Prompt"):
            if letter and prompt_name and categories and prompt_text:
                new_row = {
                    "Letter": letter.upper(),
                    "PromptName": prompt_name,
                    "Categories": categories,
                    "PromptText": prompt_text,
                    "Model": model
                }
                data = data.append(new_row, ignore_index=True)
                save_data(data)
                st.success("New prompt added successfully!")
            else:
                st.error("Please fill in all fields.")
    
    # Edit existing prompts
    st.subheader("Edit Existing Prompts")
    if not data.empty:
        prompt_to_edit = st.selectbox("Select a prompt to edit", data['PromptName'])
        edit_index = data[data['PromptName'] == prompt_to_edit].index[0]
        
        with st.form("edit_prompt_form"):
            edit_letter = st.text_input("Letter", data.loc[edit_index, 'Letter'], max_chars=1)
            edit_prompt_name = st.text_input("Prompt Name", data.loc[edit_index, 'PromptName'])
            edit_categories = st.text_input("Categories", data.loc[edit_index, 'Categories'])
            edit_prompt_text = st.text_area("Prompt Text", data.loc[edit_index, 'PromptText'])
            edit_model = st.selectbox("AI Model", list(AVAILABLE_MODELS.keys()), index=list(AVAILABLE_MODELS.keys()).index(data.loc[edit_index, 'Model']))
            
            if st.form_submit_button("Update Prompt"):
                data.loc[edit_index] = [edit_letter.upper(), edit_prompt_name, edit_categories, edit_prompt_text, edit_model]
                save_data(data)
                st.success("Prompt updated successfully!")
    
    # Delete prompts
    st.subheader("Delete Prompts")
    if not data.empty:
        prompt_to_delete = st.selectbox("Select a prompt to delete", data['PromptName'])
        if st.button("Delete Prompt"):
            data = data[data['PromptName'] != prompt_to_delete]
            save_data(data)
            st.success(f"Prompt '{prompt_to_delete}' deleted successfully!")
    
    # Manage categories
    st.subheader("Manage Categories")
    all_categories = set()
    for cats in data['Categories']:
        all_categories.update([cat.strip() for cat in cats.split(',')])
    
    st.write("Existing Categories:")
    st.write(", ".join(sorted(all_categories)))
    
    new_category = st.text_input("Add New Category")
    if st.button("Add Category"):
        if new_category and new_category not in all_categories:
            all_categories.add(new_category)
            st.success(f"Category '{new_category}' added successfully!")
        elif new_category in all_categories:
            st.warning(f"Category '{new_category}' already exists.")
        else:
            st.error("Please enter a category name.")

if __name__ == "__main__":
    admin_interface()
