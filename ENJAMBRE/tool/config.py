"""
Configuracion central del sistema ENJAMBRE.
Todas las rutas y parametros se definen aqui para evitar valores hardcodeados.
"""

import os

# Directorio donde esta este archivo (tool/)
TOOL_DIR = os.path.dirname(os.path.abspath(__file__))

# Directorio raiz del proyecto
PROJECT_ROOT = os.path.dirname(TOOL_DIR)

# === TIMEOUTS (en segundos) ===
TIMEOUTS = {
    'generation': 120,      # Timeout para generacion de archivos
    'modular': 180,         # Timeout para generacion modular (mas largo)
    'subprocess': 30,       # Timeout para subprocesos
    'health_check': 5,      # Timeout para health checks
}

# === LIMITES DE GENERACION ===
GENERATION = {
    'max_tokens_default': 4096,   # Tokens para modo default
    'max_tokens_patch': 1024,     # Tokens para modo patch
    'max_retries': 3,             # Intentos maximos por tarea
    'max_workers': 8,             # Workers maximos en paralelo
    'min_file_size': 50,          # Tamano minimo de archivo valido (bytes)
    'min_combined_size': 100,     # Tamano minimo de archivo combinado (bytes)
}

# === AGENTES LLM ===
AGENTS = {
    'qwen': {
        'url': 'http://127.0.0.1:8080/v1/chat/completions',
        'key': 'no-needed',
        'model': 'qwen-local',
    },
    'mimo': {
        'url': 'https://api.xiaomimimo.com/v1/chat/completions',
        'key': 'TU_KEY_XIAOMI',
        'model': 'mimo-v2-flash',
    },
}

# Rutas a scripts
SCRIPTS = {
    'ask_agent': os.path.join(TOOL_DIR, 'ask_agent.py'),
    'ask_agent_batch': os.path.join(TOOL_DIR, 'ask_agent_batch_v2.py'),
    'validate_output': os.path.join(TOOL_DIR, 'validate_output.py'),
    'validate_media': os.path.join(TOOL_DIR, 'validate_media.py'),
    'update_metrics': os.path.join(TOOL_DIR, 'update_metrics.py'),
    'generate_project': os.path.join(TOOL_DIR, 'generate_project.py'),
    'modular_generator': os.path.join(TOOL_DIR, 'modular_generator.py'),
}

# Rutas a archivos de configuracion
CONFIG_FILES = {
    'templates': os.path.join(TOOL_DIR, 'templates.json'),
    'prompt_library': os.path.join(TOOL_DIR, 'prompt-library.json'),
}

# Servidor LLM (derivado de AGENTS para compatibilidad)
LLM_SERVER = {
    'url': AGENTS['qwen']['url'].replace('/v1/chat/completions', ''),
    'endpoint': '/v1/chat/completions',
    'model': AGENTS['qwen']['model'],
}

def get_script_path(script_name):
    """Obtiene la ruta a un script por nombre"""
    return SCRIPTS.get(script_name)

def get_config_path(config_name):
    """Obtiene la ruta a un archivo de configuracion por nombre"""
    return CONFIG_FILES.get(config_name)
