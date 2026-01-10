import sys
import requests
import json
import argparse
import os
import re
from concurrent.futures import ThreadPoolExecutor

# Configuración
AGENTS = {
    "qwen": "http://127.0.0.1:8080/v1/chat/completions",
    "mimo": "https://api.xiaomimimo.com/v1/chat/completions"
}
KEYS = { "qwen": "no-needed", "mimo": "TU_KEY_XIAOMI" }

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
    url = AGENTS.get(agent_name)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {KEYS.get(agent_name, '')}"
    }
    
    sys_msg = SYSTEM_PROMPTS["patch"] if mode == "patch" else SYSTEM_PROMPTS["default"]
    
    data = {
        "model": "qwen-local" if agent_name == "qwen" else "mimo-v2-flash",
        "messages": [
            {"role": "system", "content": sys_msg},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 4096 if mode == "default" else 1024, # Menos tokens para patches
        "stream": False
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=120)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content']
        return f"Error {response.status_code}: {response.text}"
    except Exception as e:
        return f"Exception: {e}"

def save_output(content, output_path):
    """Guarda el contenido extraido del output en el archivo especificado"""
    if not output_path:
        return None

    # Crear directorio si no existe
    dir_path = os.path.dirname(output_path)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)

    # Extraer codigo entre bloques de markdown
    code_match = re.search(r'```(?:python|javascript|json|yaml|plaintext|dockerfile|bash|shell)?\s*\n(.*?)```', content, re.DOTALL | re.IGNORECASE)
    if code_match:
        code_content = code_match.group(1)
    else:
        # Si no hay bloques, usar el contenido completo limpiando markdown
        code_content = re.sub(r'^```\w*\n|```$', '', content, flags=re.MULTILINE)

    # Guardar archivo
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(code_content)

    return output_path

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