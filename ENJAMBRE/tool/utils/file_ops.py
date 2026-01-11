"""
Operaciones de entrada/salida para archivos.
Centraliza load/save JSON y manejo de directorios.
"""

import json
import os


def load_json(filepath):
    """
    Carga un archivo JSON con manejo robusto de errores.

    Args:
        filepath: Ruta al archivo JSON

    Returns:
        dict/list: Contenido del JSON parseado
        None: Si el archivo no existe o hay error de parseo
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError as e:
        print(f"Error: No se pudo parsear {filepath}: {e}")
        return None
    except Exception as e:
        print(f"Error leyendo {filepath}: {e}")
        return None


def save_json(filepath, data, indent=2):
    """
    Guarda datos en archivo JSON con formato legible.

    Args:
        filepath: Ruta donde guardar el archivo
        data: Datos a serializar (dict/list)
        indent: Indentacion (default: 2 espacios)

    Returns:
        bool: True si se guardo correctamente, False si hubo error
    """
    try:
        dir_path = os.path.dirname(filepath)
        if dir_path:
            ensure_dir_exists(dir_path)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error guardando {filepath}: {e}")
        return False


def ensure_dir_exists(dir_path):
    """
    Crea un directorio si no existe (incluyendo padres).

    Args:
        dir_path: Ruta del directorio a crear

    Returns:
        bool: True si existe o se creo, False si hubo error
    """
    if not dir_path:
        return True

    try:
        os.makedirs(dir_path, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creando directorio {dir_path}: {e}")
        return False


def save_output(content, output_path):
    """
    Guarda contenido extraido de respuesta LLM en archivo.
    Extrae codigo de bloques markdown automaticamente.

    Args:
        content: Contenido a guardar (puede contener markdown)
        output_path: Ruta donde guardar el archivo

    Returns:
        str: Ruta del archivo guardado
        None: Si output_path es None/vacio
    """
    if not output_path:
        return None

    dir_path = os.path.dirname(output_path)
    if dir_path:
        ensure_dir_exists(dir_path)

    from .code_extract import extract_code_from_markdown

    code_content = extract_code_from_markdown(content)

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(code_content)
        return output_path
    except Exception as e:
        print(f"Error guardando {output_path}: {e}")
        return None
