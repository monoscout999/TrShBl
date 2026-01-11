"""
Utilidades compartidas para el sistema ENJAMBRE.
Centraliza operaciones comunes para evitar duplicacion de codigo.
"""

from .file_ops import (
    load_json,
    save_json,
    save_output,
    ensure_dir_exists,
)

from .validators import (
    WRONG_LANG_PATTERNS,
    EXPECTED_KEYWORDS,
    REQUIRED_KEYWORDS,
    check_file_content,
    validate_file_language,
    detect_wrong_language,
    validate_required_keywords,
)

from .code_extract import (
    extract_code_from_markdown,
    MARKDOWN_CODE_PATTERN,
)

__all__ = [
    # file_ops
    'load_json',
    'save_json',
    'save_output',
    'ensure_dir_exists',
    # validators
    'WRONG_LANG_PATTERNS',
    'EXPECTED_KEYWORDS',
    'REQUIRED_KEYWORDS',
    'check_file_content',
    'validate_file_language',
    'detect_wrong_language',
    'validate_required_keywords',
    # code_extract
    'extract_code_from_markdown',
    'MARKDOWN_CODE_PATTERN',
]
