"""
Validaciones de contenido y lenguaje para archivos generados.
Detecta errores comunes como mezcla de lenguajes.
"""

import os

# Patrones que indican lenguaje INCORRECTO en un tipo de archivo
WRONG_LANG_PATTERNS = {
    'css': [
        'from flask', 'function ', 'const ', 'document.',
        'def ', 'import ', '<!DOCTYPE', '<html', '<body'
    ],
    'js': [
        'from flask', '@app.route', 'def ', 'import Flask',
        'render_template', '<!DOCTYPE', '<html', '<head',
        '<body', '// HTML', '// CSS'
    ],
    'html': [
        'from flask', 'def ', '@app.route',
        'const canvas', 'function()', '=>'
    ],
    'python': [
        '<!DOCTYPE', '<html>', '</html>',
        'function()', 'const ', 'let ', 'var '
    ],
}

# Keywords ESPERADOS por tipo de archivo (minimo 50% deben estar presentes)
EXPECTED_KEYWORDS = {
    'css': ['body', '{', '}', ':', ';'],
    'js': ['function', 'const', 'let', 'var', '=>', '(', ')'],
    'html': ['<', '>', 'html', 'head', 'body', '<!DOCTYPE'],
    'python': ['def ', 'import ', 'return', ':'],
}

# Keywords OBLIGATORIOS por tipo (usados en validate_media)
REQUIRED_KEYWORDS = {
    'python': ['Flask', 'render_template', '@app.route'],
    'html': ['<!DOCTYPE html>', 'link rel=', 'script src'],
    'css': ['body', 'margin', 'background'],
    'js': ['const', 'function', 'document'],
}


def check_file_content(filepath, search_string):
    """
    Busca un string en el contenido de un archivo.

    Args:
        filepath: Ruta al archivo
        search_string: String a buscar

    Returns:
        bool: True si se encuentra, False si no existe o no se encuentra
    """
    if not os.path.exists(filepath):
        return False
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return search_string in f.read()
    except Exception:
        return False


def detect_wrong_language(content, file_type):
    """
    Detecta si hay codigo de otro lenguaje contaminando el archivo.

    Args:
        content: Contenido del archivo
        file_type: Tipo esperado ('css', 'js', 'html', 'python')

    Returns:
        list: Lista de patrones incorrectos encontrados (vacia si OK)
    """
    patterns = WRONG_LANG_PATTERNS.get(file_type, [])
    found = []
    for pattern in patterns:
        if pattern in content:
            found.append(pattern)
    return found


def validate_file_language(filepath, file_type):
    """
    Valida que un archivo contenga el lenguaje correcto.

    Args:
        filepath: Ruta al archivo
        file_type: Tipo esperado ('css', 'js', 'html', 'python')

    Returns:
        dict: {
            'valid': bool,
            'status': str ('OK', 'MISSING', 'EMPTY', 'WRONG_LANG', 'INVALID'),
            'message': str,
            'size': int (si existe)
        }
    """
    if not os.path.exists(filepath):
        return {'valid': False, 'status': 'MISSING', 'message': 'Archivo no existe'}

    size = os.path.getsize(filepath)
    if size < 50:
        return {'valid': False, 'status': 'EMPTY', 'message': f'Muy pequeno: {size} bytes', 'size': size}

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return {'valid': False, 'status': 'ERROR', 'message': str(e)}

    # Detectar lenguaje incorrecto
    wrong_patterns = detect_wrong_language(content, file_type)
    if wrong_patterns:
        return {
            'valid': False,
            'status': 'WRONG_LANG',
            'message': f'Detectado: {wrong_patterns[0]}',
            'size': size
        }

    # Verificar keywords esperados
    keywords = EXPECTED_KEYWORDS.get(file_type, [])
    found = sum(1 for kw in keywords if kw in content)
    if found < len(keywords) // 2:
        return {
            'valid': False,
            'status': 'INVALID',
            'message': f'Faltan keywords esperados ({found}/{len(keywords)})',
            'size': size
        }

    return {'valid': True, 'status': 'OK', 'size': size}


def validate_required_keywords(filepath, file_type):
    """
    Valida que un archivo contenga los keywords obligatorios.

    Args:
        filepath: Ruta al archivo
        file_type: Tipo ('python', 'html', 'css', 'js')

    Returns:
        tuple: (passed: bool, message: str)
    """
    if not os.path.exists(filepath):
        return False, "Archivo no existe"

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        return False, f"Error leyendo: {e}"

    required = REQUIRED_KEYWORDS.get(file_type, [])
    for keyword in required:
        if keyword not in content:
            return False, f"Falta keyword: {keyword}"

    return True, "OK"
