# admin_interface.py

import streamlit as st
import pandas as pd
import json
import os

def load_prompts():
    if os.path.exists('prompts.json'):
        with open('prompts.json', 'r') as f:
            data = json.load(f)
            # Check if prompts are in old format (string values)
            if data and isinstance(next(iter(data.values())), str):
                # Convert to new format with 'content' and 'placeholders'
                for key in data:
                    data[key] = {
                        'content': data[key],
                        'placeholders': ['subject']
                    }
                save_prompts(data)
            return data
    return {}

def save_prompts(prompts):
    with open('prompts.json', 'w') as f:
        json.dump(prompts, f)

def admin_interface():
    st.title("🔒 Admin Interface")

    # Simple authentication
    if 'admin_authenticated' not in st.session_state:
        st.session_state.admin_authenticated = False

    if not st.session_state.admin_authenticated:
        password = st.text_input("Enter admin password", type="password")
        if st.button("Login"):
            if password == "your_admin_password":  # Replace with your secure password
                st.session_state.admin_authenticated = True
                st.success("Authenticated successfully!")
            else:
                st.error("Incorrect password")

    if st.session_state.admin_authenticated:
        st.subheader("Manage Prompt Templates")

        prompts = load_prompts()

        # Add new prompt template
        with st.expander("➕ Add New Prompt Template"):
            prompt_name = st.text_input("Prompt Name")
            placeholder_keys = st.text_input("Placeholder Keys (comma-separated)", value="subject")
            prompt_content = st.text_area("Prompt Content")
            if st.button("Add Prompt Template"):
                if prompt_name and prompt_content:
                    # Create a list of placeholder keys
                    placeholders = [key.strip() for key in placeholder_keys.split(',')]
                    for key in placeholders:
                        if f"{{{key}}}" not in prompt_content:
                            st.error(f"Placeholder '{{{key}}}' not found in prompt content.")
                            break
                    else:
                        prompts[prompt_name] = {
                            "content": prompt_content,
                            "placeholders": placeholders
                        }
                        save_prompts(prompts)
                        st.success(f"Prompt template '{prompt_name}' added.")
                else:
                    st.error("Please provide a prompt name and content.")

        if prompts:
            st.subheader("Existing Prompt Templates")
            st.write("Here are the prompt templates you've created:")
            for name in prompts.keys():
                st.write(f"- **{name}**")

            # Edit existing prompt templates
            with st.expander("✏️ Edit Existing Prompt Templates"):
                selected_prompt = st.selectbox("Select a prompt to edit", list(prompts.keys()))
                if selected_prompt:
                    prompt_data = prompts[selected_prompt]
                    new_name = st.text_input("New Prompt Name", value=selected_prompt, key='edit_name')
                    new_placeholder_keys = st.text_input("New Placeholder Keys (comma-separated)", value=', '.join(prompt_data["placeholders"]), key='edit_placeholders')
                    new_content = st.text_area("New Prompt Content", value=prompt_data["content"], key='edit_content')
                    if st.button("Update Prompt Template"):
                        if new_name and new_content:
                            placeholders = [key.strip() for key in new_placeholder_keys.split(',')]
                            for key in placeholders:
                                if f"{{{key}}}" not in new_content:
                                    st.error(f"Placeholder '{{{key}}}' not found in prompt content.")
                                    break
                            else:
                                if new_name != selected_prompt:
                                    del prompts[selected_prompt]
                                prompts[new_name] = {
                                    "content": new_content,
                                    "placeholders": placeholders
                                }
                                save_prompts(prompts)
                                st.success(f"Prompt template '{new_name}' updated.")
                        else:
                            st.error("Please provide a new name and content.")

            # Delete prompt templates
            with st.expander("🗑️ Delete Prompt Templates"):
                prompts_to_delete = st.multiselect("Select prompts to delete", list(prompts.keys()))
                if st.button("Delete Selected Prompt Templates"):
                    if prompts_to_delete:
                        for prm in prompts_to_delete:
                            del prompts[prm]
                        save_prompts(prompts)
                        st.success("Selected prompt templates have been deleted.")
                    else:
                        st.error("No prompt templates selected for deletion.")

if __name__ == "__main__":
    admin_interface()
