import streamlit as st
import pandas as pd
import json
import os

def load_hidden_prompts():
    if os.path.exists('hidden_prompts.json'):
        with open('hidden_prompts.json', 'r') as f:
            return json.load(f)
    return []

def save_hidden_prompts(prompts):
    with open('hidden_prompts.json', 'w') as f:
        json.dump(prompts, f)

def admin_interface():
    st.title("🔒 Admin Interface")

    # Simple authentication
    if 'admin_authenticated' not in st.session_state:
        st.session_state.admin_authenticated = False

    if not st.session_state.admin_authenticated:
        password = st.text_input("Enter admin password", type="password")
        if st.button("Login"):
            if password == "admin123":  # Replace with a secure password mechanism
                st.session_state.admin_authenticated = True
                st.success("Authenticated successfully!")
            else:
                st.error("Incorrect password")

    if st.session_state.admin_authenticated:
        st.subheader("Manage Hidden Prompts")

        hidden_prompts = load_hidden_prompts()

        # Display existing hidden prompts
        if hidden_prompts:
            st.write("Current Hidden Prompts:")
            df = pd.DataFrame(hidden_prompts)
            st.dataframe(df)

        # Add new hidden prompt
        st.subheader("Add New Hidden Prompt")
        new_prompt = st.text_area("Enter new hidden prompt")
        if st.button("Add Prompt"):
            if new_prompt:
                hidden_prompts.append({"prompt": new_prompt})
                save_hidden_prompts(hidden_prompts)
                st.success("New hidden prompt added successfully!")
            else:
                st.warning("Please enter a prompt before adding.")

        # Remove hidden prompt
        if hidden_prompts:
            st.subheader("Remove Hidden Prompt")
            prompt_to_remove = st.selectbox("Select prompt to remove", [p["prompt"] for p in hidden_prompts])
            if st.button("Remove Prompt"):
                hidden_prompts = [p for p in hidden_prompts if p["prompt"] != prompt_to_remove]
                save_hidden_prompts(hidden_prompts)
                st.success("Hidden prompt removed successfully!")

if __name__ == "__main__":
    admin_interface()
