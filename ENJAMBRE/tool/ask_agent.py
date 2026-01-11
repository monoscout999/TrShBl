import sys
import requests
import json
import argparse
import os
from concurrent.futures import ThreadPoolExecutor

from config import AGENTS, TIMEOUTS, GENERATION
from utils import save_output

# Prompts Especializados
SYSTEM_PROMPTS = {
    "default": "You are a code generation expert. Generate ONLY valid code, no explanations. For .py files: Python Flask. For .html files: HTML5. For .css files: CSS. For .js files: JavaScript for browser. NEVER mix languages.",
    "patch": """You are a CODE SURGEON. DO NOT rewrite the whole file.
    Output ONLY the specific function or block that needs changing.
    Use this format:
    ```python
    # ... code before ...
    def changed_function():
        # new logic here
    # ... code after ...
    ```
    Focus strictly on the requested fix."""
}

def call_api(agent_name, prompt, mode="default"):
    agent = AGENTS.get(agent_name)
    if not agent:
        return f"Error: Agente '{agent_name}' no encontrado"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {agent['key']}"
    }

    sys_msg = SYSTEM_PROMPTS["patch"] if mode == "patch" else SYSTEM_PROMPTS["default"]
    max_tokens = GENERATION['max_tokens_patch'] if mode == "patch" else GENERATION['max_tokens_default']

    data = {
        "model": agent['model'],
        "messages": [
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "max_tokens": max_tokens,
        "stream": False
    }

    try:
        response = requests.post(agent['url'], headers=headers, json=data, timeout=TIMEOUTS['generation'])
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        return f"Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"Exception: {e}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("agent", choices=["qwen", "mimo"])
    parser.add_argument("prompt")
    parser.add_argument("--mode", choices=["default", "patch"], default="default")
    parser.add_argument("--output", help="Ruta donde guardar el archivo generado")
    args = parser.parse_args()

    print(f"--- {args.agent.upper()} ({args.mode.upper()}) ---")
    res = call_api(args.agent, args.prompt, args.mode)

    if args.output:
        saved_path = save_output(res, args.output)
        print(f"\n[SAVED] {saved_path}")
    else:
        print(res)