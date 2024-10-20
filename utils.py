
import pandas as pd
import json
from typing import List, Dict

def process_csv(df: pd.DataFrame, has_image_url: bool, upload_option: str) -> List[Dict]:
    # ... (rest of the code remains unchanged)

def process_json(data: List[Dict], has_image_url: bool, upload_option: str) -> List[Dict]:
    # ... (rest of the code remains unchanged)

def generate_html_content(data: List[Dict], has_image_url: bool, theme: str, header_title: str) -> str:
    # ... (rest of the code remains unchanged)

def get_css_styles() -> str:
    # ... (rest of the code remains unchanged)

AVAILABLE_MODELS = {
    "Ministral 8B": {"id": "mistralai/ministral-8b", "context_tokens": 128000},
    "Ministral 3B": {"id": "mistralai/ministral-3b", "context_tokens": 128000},
    "Qwen2.5 7B Instruct": {"id": "qwen/qwen-2.5-7b-instruct", "context_tokens": 131072},
    "Nvidia: Llama 3.1 Nemotron 70B Instruct": {"id": "nvidia/llama-3.1-nemotron-70b-instruct", "context_tokens": 131072},
    "xAI: Grok 2": {"id": "x-ai/grok-2", "context_tokens": 32768},
    "Inflection: Inflection 3 Pi": {"id": "inflection/inflection-3-pi", "context_tokens": 8000},
    "Inflection: Inflection 3 Productivity": {"id": "inflection/inflection-3-productivity", "context_tokens": 8000},
    "Google: Gemini 1.5 Flash-8B": {"id": "google/gemini-flash-1.5-8b", "context_tokens": 1000000},
    "Liquid: LFM 40B MoE": {"id": "liquid/lfm-40b", "context_tokens": 32768},
    "Liquid: LFM 40B MoE (free)": {"id": "liquid/lfm-40b", "context_tokens": 8192},
    "Rocinante 12B": {"id": "thedrummer/rocinante-12b", "context_tokens": 32768},
    "EVA Qwen2.5 14B": {"id": "eva-unit-01/eva-qwen-2.5-14b", "context_tokens": 32768},
    "Magnum v2 72B": {"id": "anthracite-org/magnum-v2-72b", "context_tokens": 32768},
    "Meta: Llama 3.2 3B Instruct": {"id": "meta-llama/llama-3.2-3b-instruct", "context_tokens": 131072},
    "Meta: Llama 3.2 1B Instruct": {"id": "meta-llama/llama-3.2-1b-instruct", "context_tokens": 131072},
    "Meta: Llama 3.2 90B Vision Instruct": {"id": "meta-llama/llama-3.2-90b-vision-instruct", "context_tokens": 131072},
    "Meta: Llama 3.2 11B Vision Instruct": {"id": "meta-llama/llama-3.2-11b-vision-instruct", "context_tokens": 131072},
    "Qwen2.5 72B Instruct": {"id": "qwen/qwen-2.5-72b-instruct", "context_tokens": 131072},
    "Qwen2-VL 72B Instruct": {"id": "qwen/qwen-2-vl-72b-instruct", "context_tokens": 32768},
    "Lumimaid v0.2 8B": {"id": "neversleep/llama-3.1-lumimaid-8b", "context_tokens": 131072},
    "OpenAI: o1-mini": {"id": "openai/o1-mini", "context_tokens": 128000},
    "OpenAI: o1-preview": {"id": "openai/o1-preview", "context_tokens": 128000},
    "Mistral: Pixtral 12B": {"id": "mistralai/pixtral-12b", "context_tokens": 4096},
    "Cohere: Command R+ (08-2024)": {"id": "cohere/command-r-plus-08-2024", "context_tokens": 128000},
    "Cohere: Command R (08-2024)": {"id": "cohere/command-r-08-2024", "context_tokens": 128000},
    "Qwen2-VL 7B Instruct": {"id": "qwen/qwen-2-vl-7b-instruct", "context_tokens": 32768},
    "Google: Gemini Flash 8B 1.5 Experimental": {"id": "google/gemini-flash-1.5-8b-exp", "context_tokens": 1000000},
    "Llama 3.1 Euryale 70B v2.2": {"id": "sao10k/l3.1-euryale-70b", "context_tokens": 8192},
    "Google: Gemini Flash 1.5 Experimental": {"id": "google/gemini-flash-1.5-exp", "context_tokens": 1000000},
    "AI21: Jamba 1.5 Large": {"id": "ai21/jamba-1-5-large", "context_tokens": 256000},
    "AI21: Jamba 1.5 Mini": {"id": "ai21/jamba-1-5-mini", "context_tokens": 256000},
    "Phi-3.5 Mini 128K Instruct": {"id": "microsoft/phi-3.5-mini-128k-instruct", "context_tokens": 128000},
    "Nous: Hermes 3 70B Instruct": {"id": "nousresearch/hermes-3-llama-3.1-70b", "context_tokens": 131072},
    "Nous: Hermes 3 405B Instruct": {"id": "nousresearch/hermes-3-llama-3.1-405b", "context_tokens": 131072},
    "Perplexity: Llama 3.1 Sonar 405B Online": {"id": "perplexity/llama-3.1-sonar-huge-128k-online", "context_tokens": 127072},
    "OpenAI: ChatGPT-4o": {"id": "openai/chatgpt-4o-latest", "context_tokens": 128000},
    "Llama 3 8B Lunaris": {"id": "sao10k/l3-lunaris-8b", "context_tokens": 8192},
    "Mistral Nemo 12B Starcannon": {"id": "aetherwiing/mn-starcannon-12b", "context_tokens": 12000},
    "OpenAI: GPT-4o (2024-08-06)": {"id": "openai/gpt-4o-2024-08-06", "context_tokens": 128000},
    "Meta: Llama 3.1 405B (base)": {"id": "meta-llama/llama-3.1-405b", "context_tokens": 131072},
    "Mistral Nemo 12B Celeste": {"id": "nothingiisreal/mn-celeste-12b", "context_tokens": 32000},
    "Google: Gemini Pro 1.5 Experimental": {"id": "google/gemini-pro-1.5-exp", "context_tokens": 1000000},
    "Perplexity: Llama 3.1 Sonar 70B Online": {"id": "perplexity/llama-3.1-sonar-large-128k-online", "context_tokens": 127072},
    "Perplexity: Llama 3.1 Sonar 70B": {"id": "perplexity/llama-3.1-sonar-large-128k-chat", "context_tokens": 131072},
    "Perplexity: Llama 3.1 Sonar 8B Online": {"id": "perplexity/llama-3.1-sonar-small-128k-online", "context_tokens": 127072},
    "Perplexity: Llama 3.1 Sonar 8B": {"id": "perplexity/llama-3.1-sonar-small-128k-chat", "context_tokens": 131072},
    "Meta: Llama 3.1 70B Instruct": {"id": "meta-llama/llama-3.1-70b-instruct", "context_tokens": 131072},
    "Meta: Llama 3.1 8B Instruct": {"id": "meta-llama/llama-3.1-8b-instruct", "context_tokens": 131072},
}
