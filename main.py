import streamlit as st
import requests
import json
import pandas as pd
import logging
import os
import base64
from utils import generate_html_content

logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(message)s')

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    st.error("OpenRouter API Key not found. Please set the OPENROUTER_API_KEY environment variable.")
    st.stop()

AVAILABLE_MODELS = {
    "Ministral 8B": "mistralai/ministral-8b",
    "Ministral 3B": "mistralai/ministral-3b",
    "Qwen2.5 7B Instruct": "qwen/qwen-2.5-7b-instruct",
    "Nvidia: Llama 3.1 Nemotron 70B Instruct": "nvidia/llama-3.1-nemotron-70b-instruct",
    "xAI: Grok 2": "x-ai/grok-2",
    "Inflection: Inflection 3 Pi": "inflection/inflection-3-pi",
    "Inflection: Inflection 3 Productivity": "inflection/inflection-3-productivity",
    "Google: Gemini 1.5 Flash-8B": "google/gemini-flash-1.5-8b",
    "Liquid: LFM 40B MoE": "liquid/lfm-40b",
    "Liquid: LFM 40B MoE (free)": "liquid/lfm-40b",
    "Rocinante 12B": "thedrummer/rocinante-12b",
    "EVA Qwen2.5 14B": "eva-unit-01/eva-qwen-2.5-14b",
    "Magnum v2 72B": "anthracite-org/magnum-v2-72b",
    "Meta: Llama 3.2 3B Instruct (free)": "meta-llama/llama-3.2-3b-instruct",
    "Meta: Llama 3.2 3B Instruct": "meta-llama/llama-3.2-3b-instruct",
    "Meta: Llama 3.2 1B Instruct (free)": "meta-llama/llama-3.2-1b-instruct",
    "Meta: Llama 3.2 1B Instruct": "meta-llama/llama-3.2-1b-instruct",
    "Meta: Llama 3.2 90B Vision Instruct": "meta-llama/llama-3.2-90b-vision-instruct",
    "Meta: Llama 3.2 11B Vision Instruct (free)": "meta-llama/llama-3.2-11b-vision-instruct",
    "Meta: Llama 3.2 11B Vision Instruct": "meta-llama/llama-3.2-11b-vision-instruct",
    "Qwen2.5 72B Instruct": "qwen/qwen-2.5-72b-instruct",
    "Qwen2-VL 72B Instruct": "qwen/qwen-2-vl-72b-instruct",
    "Lumimaid v0.2 8B": "neversleep/llama-3.1-lumimaid-8b",
    "OpenAI: o1-mini (2024-09-12)": "openai/o1-mini-2024-09-12",
    "OpenAI: o1-mini": "openai/o1-mini",
    "OpenAI: o1-preview (2024-09-12)": "openai/o1-preview-2024-09-12",
    "OpenAI: o1-preview": "openai/o1-preview",
    "Mistral: Pixtral 12B": "mistralai/pixtral-12b",
    "Cohere: Command R+ (08-2024)": "cohere/command-r-plus-08-2024",
    "Cohere: Command R (08-2024)": "cohere/command-r-08-2024",
    "Qwen2-VL 7B Instruct": "qwen/qwen-2-vl-7b-instruct",
    "Google: Gemini Flash 8B 1.5 Experimental": "google/gemini-flash-1.5-8b-exp",
    "Llama 3.1 Euryale 70B v2.2": "sao10k/l3.1-euryale-70b",
    "Google: Gemini Flash 1.5 Experimental": "google/gemini-flash-1.5-exp",
    "AI21: Jamba 1.5 Large": "ai21/jamba-1-5-large",
    "AI21: Jamba 1.5 Mini": "ai21/jamba-1-5-mini",
    "Phi-3.5 Mini 128K Instruct": "microsoft/phi-3.5-mini-128k-instruct",
    "Nous: Hermes 3 70B Instruct": "nousresearch/hermes-3-llama-3.1-70b",
    "Nous: Hermes 3 405B Instruct (free)": "nousresearch/hermes-3-llama-3.1-405b",
    "Nous: Hermes 3 405B Instruct": "nousresearch/hermes-3-llama-3.1-405b",
    "Nous: Hermes 3 405B Instruct (extended)": "nousresearch/hermes-3-llama-3.1-405b",
    "Perplexity: Llama 3.1 Sonar 405B Online": "perplexity/llama-3.1-sonar-huge-128k-online",
    "OpenAI: ChatGPT-4o": "openai/chatgpt-4o-latest",
    "Llama 3 8B Lunaris": "sao10k/l3-lunaris-8b",
    "Mistral Nemo 12B Starcannon": "aetherwiing/mn-starcannon-12b",
    "OpenAI: GPT-4o (2024-08-06)": "openai/gpt-4o-2024-08-06",
    "Meta: Llama 3.1 405B (base)": "meta-llama/llama-3.1-405b",
    "Mistral Nemo 12B Celeste": "nothingiisreal/mn-celeste-12b",
    "Google: Gemini Pro 1.5 Experimental": "google/gemini-pro-1.5-exp",
    "Perplexity: Llama 3.1 Sonar 70B Online": "perplexity/llama-3.1-sonar-large-128k-online",
    "Perplexity: Llama3 Sonar 70B": "perplexity/llama-3-sonar-large-128k-chat",
    "Perplexity: Llama3 Sonar 8B Online": "perplexity/llama-3.1-sonar-small-128k-online",
    "Perplexity: Llama3 Sonar 8B": "perplexity/llama-3.1-sonar-small-128k-chat",
    "Meta: Llama 3.1 70B Instruct (free)": "meta-llama/llama-3.1-70b-instruct",
    "Meta: Llama 3.1 70B Instruct": "meta-llama/llama-3.1-70b-instruct",
    "Meta: Llama 3.1 8B Instruct (free)": "meta-llama/llama-3.1-8b-instruct",
    "Meta: Llama 3.1 8B Instruct": "meta-llama/llama-3.1-8b-instruct",
    "Meta: Llama 3.1 405B Instruct (free)": "meta-llama/llama-3.1-405b-instruct",
    "Meta: Llama 3.1 405B Instruct": "meta-llama/llama-3.1-405b-instruct",
    "Mistral: Codestral Mamba": "mistralai/codestral-mamba",
    "Mistral: Mistral Nemo": "mistralai/mistral-nemo",
    "OpenAI: GPT-4o-mini (2024-07-18)": "openai/gpt-4o-mini-2024-07-18",
    "OpenAI: GPT-4o-mini": "openai/gpt-4o-mini",
    "Qwen 2 7B Instruct (free)": "qwen/qwen-2-7b-instruct",
    "Qwen 2 7B Instruct": "qwen/qwen-2-7b-instruct",
    "Google: Gemma 2 27B": "google/gemma-2-27b-it",
    "Magnum 72B": "alpindale/magnum-72b",
    "Nous: Hermes 2 Theta 8B": "nousresearch/hermes-2-theta-llama-3-8b",
    "Google: Gemma 2 9B (free)": "google/gemma-2-9b-it",
    "Google: Gemma 2 9B": "google/gemma-2-9b-it",
    "AI21: Jamba Instruct": "ai21/jamba-instruct",
    "Anthropic: Claude 3.5 Sonnet": "anthropic/claude-3.5-sonnet",
    "Anthropic: Claude 3.5 Sonnet (self-moderated)": "anthropic/claude-3.5-sonnet",
    "Anthropic: Claude 3 Sonnet": "anthropic/claude-3-sonnet",
    "Anthropic: Claude 3 Sonnet (self-moderated)": "anthropic/claude-3-sonnet",
    "Anthropic: Claude 3 Opus": "anthropic/claude-3-opus",
    "Anthropic: Claude 3 Opus (self-moderated)": "anthropic/claude-3-opus",
    "Cohere: Command R (03-2024)": "cohere/command-r-03-2024",
    "Mistral Large": "mistralai/mistral-large",
    "OpenAI: GPT-4 Turbo Preview": "openai/gpt-4-turbo-preview",
    "OpenAI: GPT-3.5 Turbo (older v0613)": "openai/gpt-3.5-turbo-0613",
    "Nous: Hermes 2 Mixtral 8x7B DPO": "nousresearch/nous-hermes-2-mixtral-8x7b-dpo",
    "Mistral Medium": "mistralai/mistral-medium",
    "Mistral Small": "mistralai/mistral-small",
    "Mistral Tiny": "mistralai/mistral-tiny",
    "Mistral: Mistral 7B Instruct v0.2": "mistralai/mistral-7b-instruct-v0.2",
    "Dolphin 2.6 Mixtral 8x7B 🐬": "cognitivecomputations/dolphin-mixtral-8x7b",
    "Google: Gemini Pro 1.0": "google/gemini-pro",
    "Google: Gemini Pro Vision 1.0": "google/gemini-pro-vision",
    "Mixtral 8x7B Instruct": "mistralai/mixtral-8x7b-instruct",
    "Mixtral 8x7B Instruct (nitro)": "mistralai/mixtral-8x7b-instruct",
    "Mixtral 8x7B (base)": "mistralai/mixtral-8x7b",
    "MythoMist 7B (free)": "gryphe/mythomist-7b",
    "MythoMist 7B": "gryphe/mythomist-7b",
    "OpenChat 3.5 7B (free)": "openchat/openchat-7b",
    "OpenChat 3.5 7B": "openchat/openchat-7b",
    "Noromaid 20B": "neversleep/noromaid-20b",
    "Anthropic: Claude Instant v1.1": "anthropic/claude-instant-1.1",
    "Anthropic: Claude v2.1": "anthropic/claude-2.1",
    "Anthropic: Claude v2.1 (self-moderated)": "anthropic/claude-2.1",
    "Anthropic: Claude v2": "anthropic/claude-2",
    "Anthropic: Claude v2 (self-moderated)": "anthropic/claude-2",
    "OpenHermes 2.5 Mistral 7B": "teknium/openhermes-2.5-mistral-7b",
    "OpenAI: GPT-4 Vision": "openai/gpt-4-vision-preview",
    "lzlv 70B": "lizpreciatior/lzlv-70b-fp16-hf",
    "Goliath 120B": "alpindale/goliath-120b",
    "Toppy M 7B (free)": "undi95/toppy-m-7b",
    "Toppy M 7B": "undi95/toppy-m-7b",
    "Toppy M 7B (nitro)": "undi95/toppy-m-7b",
    "Auto (best for prompt)": "openrouter/auto",
    "OpenAI: GPT-4 Turbo (older v1106)": "openai/gpt-4-1106-preview",
    "OpenAI: GPT-3.5 Turbo 16k (older v1106)": "openai/gpt-3.5-turbo-16k",
    "Google: PaLM 2 Code Chat 32k": "google/palm-2-codechat-bison-32k",
    "Google: PaLM 2 Chat 32k": "google/palm-2-chat-bison-32k",
    "Airoboros 70B": "jondurbin/airoboros-l2-70b",
    "Xwin 70B": "xwin-lm/xwin-lm-70b",
    "Mistral: Mistral 7B Instruct v0.1": "mistralai/mistral-7b-instruct-v0.1",
    "OpenAI: GPT-3.5 Turbo Instruct": "openai/gpt-3.5-turbo-instruct",
    "Pygmalion: Mythalion 13B": "pygmalionai/mythalion-13b",
    "OpenAI: GPT-4 32k (older v0314)": "openai/gpt-4-32k-0314",
    "OpenAI: GPT-4 32k": "openai/gpt-4-32k",
    "OpenAI: GPT-3.5 Turbo 16k": "openai/gpt-3.5-turbo-16k",
    "Nous: Hermes 13B": "nousresearch/nous-hermes-llama2-13b",
    "Hugging Face: Zephyr 7B (free)": "huggingfaceh4/zephyr-7b-beta",
    "Mancer: Weaver (alpha)": "mancer/weaver",
    "Anthropic: Claude Instant v1.0": "anthropic/claude-instant-1.0",
    "Anthropic: Claude v1.2": "anthropic/claude-1.2",
    "Anthropic: Claude v1": "anthropic/claude-1",
    "Anthropic: Claude Instant v1": "anthropic/claude-instant-1",
    "Anthropic: Claude Instant v1 (self-moderated)": "anthropic/claude-instant-1",
    "Anthropic: Claude v2.0": "anthropic/claude-2.0",
    "Anthropic: Claude v2.0 (self-moderated)": "anthropic/claude-2.0",
    "ReMM SLERP 13B": "undi95/remm-slerp-l2-13b",
    "ReMM SLERP 13B (extended)": "undi95/remm-slerp-l2-13b",
    "Google: PaLM 2 Code Chat": "google/palm-2-codechat-bison",
    "Google: PaLM 2 Chat": "google/palm-2-chat-bison",
    "MythoMax 13B (free)": "gryphe/mythomax-l2-13b",
    "MythoMax 13B": "gryphe/mythomax-l2-13b",
    "MythoMax 13B (nitro)": "gryphe/mythomax-l2-13b",
    "MythoMax 13B (extended)": "gryphe/mythomax-l2-13b",
    "Meta: Llama v2 13B Chat": "meta-llama/llama-2-13b-chat",
    "OpenAI: GPT-4 (older v0314)": "openai/gpt-4-0314",
    "OpenAI: GPT-4": "openai/gpt-4",
    "OpenAI: GPT-3.5 Turbo 16k": "openai/gpt-3.5-turbo-0125",
    "OpenAI: GPT-3.5 Turbo": "openai/gpt-3.5-turbo",
}

def load_templates():
    if 'templates' not in st.session_state:
        if os.path.exists('templates.json'):
            with open('templates.json', 'r') as f:
                st.session_state.templates = json.load(f)
            logging.info("Templates loaded from file.")
        else:
            st.session_state.templates = {}
            logging.info("No templates file found. Starting with an empty template list.")

def save_templates():
    with open('templates.json', 'w') as f:
        json.dump(st.session_state.templates, f)
    logging.info("Templates saved to file.")

def admin_auth():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        password = st.text_input("Enter admin password:", type="password")
        if password == "your_admin_password":
            st.session_state.authenticated = True
            st.success("Authentication successful!")
        elif password:
            st.error("Incorrect password.")

def admin_interface():
    st.header("🔒 Admin Interface")

    load_templates()

    st.subheader("Manage Templates")

    with st.expander("➕ Add New Template"):
        template_name = st.text_input("Template Name")
        template_content = st.text_area("Template Content (use {subject} and {input} as placeholders)")
        category = st.text_input("Category")
        if st.button("Add Template"):
            if template_name and template_content and category:
                if "{subject}" in template_content and "{input}" in template_content:
                    st.session_state.templates[template_name] = {
                        "content": template_content,
                        "category": category
                    }
                    save_templates()
                    st.success(f"Template '{template_name}' added.")
                else:
                    st.error("Template content must include both {subject} and {input} placeholders.")
            else:
                st.error("Please provide a template name, content, and category.")

    if st.session_state.templates:
        with st.expander("✏️ Edit Existing Templates"):
            selected_template = st.selectbox("Select a template to edit", list(st.session_state.templates.keys()))
            new_name = st.text_input("New Template Name", value=selected_template)
            new_content = st.text_area("New Template Content", value=st.session_state.templates[selected_template]["content"])
            new_category = st.text_input("New Category", value=st.session_state.templates[selected_template]["category"])
            if st.button("Update Template"):
                if new_name and new_content and new_category:
                    if "{subject}" in new_content and "{input}" in new_content:
                        del st.session_state.templates[selected_template]
                        st.session_state.templates[new_name] = {
                            "content": new_content,
                            "category": new_category
                        }
                        save_templates()
                        st.success(f"Template '{new_name}' updated.")
                    else:
                        st.error("Template content must include both {subject} and {input} placeholders.")
                else:
                    st.error("Please provide a new name, content, and category.")

    if st.session_state.templates:
        with st.expander("🗑️ Delete Templates"):
            templates_to_delete = st.multiselect("Select templates to delete", list(st.session_state.templates.keys()))
            if st.button("Delete Selected Templates"):
                if templates_to_delete:
                    for tmpl in templates_to_delete:
                        del st.session_state.templates[tmpl]
                    save_templates()
                    st.success("Selected templates have been deleted.")
                else:
                    st.error("No templates selected for deletion.")

def call_openrouter_api(prompt, model):
    logging.info(f"Sending prompt to OpenRouter API using model: {model}")
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            data=json.dumps({
                "model": model,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }),
            timeout=30
        )

        if response.status_code == 200:
            response_data = response.json()
            prompt_text = response_data.get('choices', [{}])[0].get('message', {}).get('content', "").strip()
            logging.info("Received prompt text from OpenRouter API.")
            return prompt_text
        else:
            logging.warning(f"API Error {response.status_code}: {response.text}")
            return f"Error: {response.status_code}, {response.text}"
    except requests.exceptions.Timeout:
        st.error("The request to the API timed out. Please try again later.")
        return "Request Timed Out"
    except Exception as e:
        logging.error(f"Exception occurred while generating prompt text: {e}")
        return f"Exception occurred: {e}"

def generate_name_and_category(subject, prompt_input, prompt_text, model):
    logging.info(f"Generating prompt name and category using AI with model: {model}")
    prompt = (
        f"Based on the following information, generate a suitable prompt name and assign a relevant category.\n\n"
        f"Subject: {subject}\n"
        f"Input: {prompt_input}\n"
        f"Generated Prompt: {prompt_text}\n\n"
        f"Respond in the following JSON format:\n"
        f"{{\n"
        f"  \"Prompt Name\": \"Your Prompt Name\",\n"
        f"  \"Category\": \"Your Category\"\n"
        f"}}"
    )

    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            data=json.dumps({
                "model": model,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            }),
            timeout=30
        )

        response.raise_for_status()
        response_data = response.json()
        ai_response = response_data.get('choices', [{}])[0].get('message', {}).get('content', "").strip()
        logging.info("Received name and category from OpenRouter API.")
        logging.debug(f"Raw AI response: {ai_response}")

        try:
            metadata = json.loads(ai_response)
            prompt_name = metadata.get("Prompt Name")
            category = metadata.get("Category")
            
            if not prompt_name or not category:
                raise ValueError("Missing Prompt Name or Category in AI response")
            
            return prompt_name, category
        except json.JSONDecodeError as json_error:
            logging.error(f"Failed to parse AI response as JSON: {json_error}")
            logging.error(f"Raw AI response: {ai_response}")
            return "Unnamed Prompt", "Uncategorized"
        except ValueError as value_error:
            logging.error(f"Invalid data in AI response: {value_error}")
            logging.error(f"Raw AI response: {ai_response}")
            return "Unnamed Prompt", "Uncategorized"
        except Exception as e:
            logging.error(f"Unexpected error while processing AI response: {e}")
            logging.error(f"Raw AI response: {ai_response}")
            return "Unnamed Prompt", "Uncategorized"
    except requests.exceptions.RequestException as req_error:
        logging.error(f"Request to OpenRouter API failed: {req_error}")
        return "Unnamed Prompt", "Uncategorized"
    except Exception as e:
        logging.error(f"Unexpected error in generate_name_and_category: {e}")
        return "Unnamed Prompt", "Uncategorized"

def main():
    st.set_page_config(page_title="Custom Prompt Generator", page_icon="🧠")

    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Go to", ["User Interface", "Admin Interface", "Prompt Data Uploader"])

    if page == "Admin Interface":
        admin_auth()
        if st.session_state.authenticated:
            admin_interface()
    elif page == "Prompt Data Uploader":
        from pages.Prompt_Data_Uploader import main as uploader_main
        uploader_main()
    else:
        st.title("🧠 Custom Prompt Generator")

        st.markdown("""
        Welcome to the **Custom Prompt Generator**! Generate creative and detailed prompts tailored to your needs.
        """)

        load_templates()

        with st.form(key='prompt_form'):
            subject = st.text_input(
                "**Subject:**",
                placeholder="e.g., AI, Quantum Computing, Climate Change",
                help="Enter the main subject for the prompt."
            )
            prompt_input = st.text_input(
                "**Input for the Prompts:**",
                placeholder="e.g., Focus on AI ethics",
                help="Provide additional details or context for the prompt."
            )
            template_names = ["None"] + list(st.session_state.templates.keys())
            selected_template = st.selectbox(
                "**Select a Prompt Template:**",
                template_names,
                help="Select a prompt template to use."
            )
            selected_model = st.selectbox(
                "**Select AI Model:**",
                list(AVAILABLE_MODELS.keys()),
                help="Choose the AI model for generating prompts."
            )
            prompt_count = st.number_input(
                "**Number of Prompts to Generate:**",
                min_value=1,
                max_value=10,
                value=1,
                step=1,
                help="Specify how many prompts you want to generate."
            )
            submit_button = st.form_submit_button(label='Generate Prompts')

        if submit_button:
            if not subject.strip() or not prompt_input.strip():
                st.error("Please fill in both **Subject** and **Input for the Prompts** fields.")
            elif selected_template == "None":
                st.error("Please select a prompt template.")
            else:
                with st.spinner('Generating prompts...'):
                    generated_prompts = []
                    model = AVAILABLE_MODELS[selected_model]

                    for i in range(int(prompt_count)):
                        template_info = st.session_state.templates[selected_template]
                        template = template_info["content"]
                        formatted_prompt = template.replace("{subject}", subject).replace("{input}", prompt_input)
                        ai_response = call_openrouter_api(formatted_prompt, model)

                        prompt_name, category = generate_name_and_category(subject, prompt_input, ai_response, model)

                        letter = prompt_name[0].upper() if prompt_name else "U"

                        generated_prompts.append({
                            "Letter": letter,
                            "Prompt Name": prompt_name,
                            "Category": category,
                            "Prompt Text": ai_response
                        })

                if generated_prompts:
                    df = pd.DataFrame(generated_prompts)
                    st.success('📄 Prompts generated successfully!')
                    st.dataframe(df, use_container_width=True)

                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Prompts as CSV",
                        data=csv,
                        file_name='generated_prompts.csv',
                        mime='text/csv',
                    )

                    generate_html = st.button("🖥️ Generate HTML")
                    if generate_html:
                        try:
                            logging.info("Generate HTML button clicked")
                            if 'generated_prompts' not in locals():
                                logging.error("No prompts generated yet")
                                st.error("Please generate prompts before creating HTML.")
                                return

                            logging.info(f"Generating HTML content for {len(generated_prompts)} prompts")
                            header_title = "Generated Prompts"
                            theme = "light"
                            html_content = generate_html_content(generated_prompts, has_image_url=False, theme=theme, header_title=header_title)

                            logging.info("HTML content generated successfully")

                            b64 = base64.b64encode(html_content.encode()).decode()
                            href = f'<a href="data:text/html;base64,{b64}" download="{header_title}.html">📥 Download Generated HTML</a>'
                            st.markdown(href, unsafe_allow_html=True)

                            logging.info("Displaying HTML content")
                            st.components.v1.html(html_content, height=600, scrolling=True)
                            logging.info("HTML content displayed successfully")
                        except Exception as e:
                            logging.error(f"Error generating or displaying HTML content: {str(e)}")
                            st.error(f"An error occurred while generating the HTML content: {str(e)}")

if __name__ == "__main__":
    main()