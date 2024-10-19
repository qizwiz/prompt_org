import pandas as pd
import json
from typing import List, Dict
import logging

# Add the AVAILABLE_MODELS dictionary
AVAILABLE_MODELS = {
    "Ministral 8B": "mistralai/ministral-8b",
    "Ministral 3B": "mistralai/ministral-3b",
    "Qwen2.5 7B Instruct": "qwen/qwen-2.5-7b-instruct",
    "Nvidia: Llama 3.1 Nemotron 70B Instruct": "nvidia/llama-3.1-nemotron-70b-instruct",
    "Google: Gemini 1.5 Flash-8B": "google/gemini-flash-1.5-8b",
    "Mistral Large": "mistralai/mistral-large",
    "OpenAI: GPT-4 Turbo Preview": "openai/gpt-4-turbo-preview",
    "Anthropic: Claude 3 Opus": "anthropic/claude-3-opus",
    "Anthropic: Claude 3 Sonnet": "anthropic/claude-3-sonnet",
    "Anthropic: Claude 3 Haiku": "anthropic/claude-3-haiku",
}

def generate_html_content(data: List[Dict], has_image_url: bool, theme: str, header_title: str) -> str:
    # Implement the HTML generation logic here
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{header_title}</title>
        <style>
            {get_css_styles()}
        </style>
    </head>
    <body>
        <h1>{header_title}</h1>
        <div class="prompts-container">
    """
    
    for prompt in data:
        html_content += f"""
        <div class="prompt-card">
            <h3>{prompt['Prompt Name'] if 'Prompt Name' in prompt else f"Prompt {prompt['id']}"}</h3>
            <p>{prompt['prompt']}</p>
        </div>
        """
    
    html_content += """
        </div>
    </body>
    </html>
    """
    
    return html_content

def get_css_styles() -> str:
    return """
    body {
        font-family: Arial, sans-serif;
        line-height: 1.6;
        color: #333;
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
    }
    h1 {
        color: #2c3e50;
        text-align: center;
    }
    .prompts-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 20px;
    }
    .prompt-card {
        background-color: #f9f9f9;
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .prompt-card h3 {
        color: #3498db;
        margin-top: 0;
    }
    """
