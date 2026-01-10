"""
Configuracion de rutas del sistema ENJAMBRE.
Todas las rutas se calculan dinamicamente basadas en la ubicacion de este archivo.
"""

import os

# Directorio donde esta este archivo (tool/)
TOOL_DIR = os.path.dirname(os.path.abspath(__file__))

# Directorio raiz del proyecto
PROJECT_ROOT = os.path.dirname(TOOL_DIR)

# Rutas a scripts
SCRIPTS = {
    'ask_agent': os.path.join(TOOL_DIR, 'ask_agent.py'),
    'ask_agent_batch': os.path.join(TOOL_DIR, 'ask_agent_batch_v2.py'),
    'validate_output': os.path.join(TOOL_DIR, 'validate_output.py'),
    'validate_media': os.path.join(TOOL_DIR, 'validate_media.py'),
    'update_metrics': os.path.join(TOOL_DIR, 'update_metrics.py'),
    'cleanup': os.path.join(TOOL_DIR, 'cleanup.py'),
    'generate_project': os.path.join(TOOL_DIR, 'generate_project.py'),
    'modular_generator': os.path.join(TOOL_DIR, 'modular_generator.py'),
}

# Rutas a archivos de configuracion
CONFIG_FILES = {
    'templates': os.path.join(TOOL_DIR, 'templates.json'),
    'prompt_library': os.path.join(TOOL_DIR, 'prompt-library.json'),
}

# Servidor LLM
LLM_SERVER = {
    'url': 'http://127.0.0.1:8080',
    'endpoint': '/v1/chat/completions',
    'model': 'phi3-local',
}

def get_script_path(script_name):
    """Obtiene la ruta a un script por nombre"""
    return SCRIPTS.get(script_name)

def get_config_path(config_name):
    """Obtiene la ruta a un archivo de configuracion por nombre"""
    return CONFIG_FILES.get(config_name)
