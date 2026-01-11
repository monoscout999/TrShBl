"""
Extraccion de codigo desde bloques markdown.
Usado para procesar respuestas de LLMs.
"""

import re

# Patron para extraer codigo de bloques markdown ```lang ... ```
MARKDOWN_CODE_PATTERN = re.compile(
    r'```(?:python|javascript|json|yaml|plaintext|dockerfile|bash|shell|html|css|js)?\s*\n(.*?)```',
    re.DOTALL | re.IGNORECASE
)


def extract_code_from_markdown(content):
    """
    Extrae codigo de bloques markdown de una respuesta LLM.

    Si encuentra bloques ```lang ... ```, extrae el contenido.
    Si no hay bloques, limpia marcadores markdown residuales.

    Args:
        content: Texto que puede contener bloques markdown

    Returns:
        str: Codigo extraido/limpiado
    """
    if not content:
        return ""

    # Buscar bloques de codigo markdown
    match = MARKDOWN_CODE_PATTERN.search(content)
    if match:
        return match.group(1)

    # Si no hay bloques, limpiar marcadores markdown residuales
    cleaned = re.sub(r'^```\w*\n|```$', '', content, flags=re.MULTILINE)
    return cleaned


def extract_all_code_blocks(content):
    """
    Extrae TODOS los bloques de codigo de un texto markdown.

    Args:
        content: Texto con posibles bloques markdown

    Returns:
        list: Lista de strings con el codigo de cada bloque
    """
    if not content:
        return []

    matches = MARKDOWN_CODE_PATTERN.findall(content)
    return matches
