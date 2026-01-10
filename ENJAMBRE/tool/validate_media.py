#!/usr/bin/env python3
"""
Validación media de archivos generados
Verifica que contengan keywords esenciales según el tipo
"""

import os
import sys

def validate_file(file_path, file_type):
    """Valida un archivo individual"""
    if not os.path.exists(file_path):
        return False, "Archivo no existe"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Keywords obligatorias por tipo (flexible con comillas)
    keywords = {
        'python': ['Flask', 'render_template', '@app.route'],
        'html': ['<!DOCTYPE html>', 'link rel=', 'script src'],
        'css': ['body', 'margin', 'background', 'canvas'],
        'js': ['const canvas', 'particles', 'requestAnimationFrame', 'mouse']
    }
    
    required = keywords.get(file_type, [])
    
    for keyword in required:
        if keyword not in content:
            return False, f"Falta keyword: {keyword}"
    
    return True, "OK"

def validate_project(project_dir):
    """Valida todo el proyecto"""
    files_to_check = {
        'app.py': 'python',
        'templates/index.html': 'html',
        'static/style.css': 'css',
        'static/script.js': 'js'
    }
    
    results = {}
    all_passed = True
    
    for file_path, file_type in files_to_check.items():
        full_path = os.path.join(project_dir, file_path)
        passed, message = validate_file(full_path, file_type)
        results[file_path] = {'passed': passed, 'message': message}
        if not passed:
            all_passed = False
    
    return {
        'success': all_passed,
        'details': results
    }

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python validate_media.py <project_dir>")
        sys.exit(1)
    
    project_dir = sys.argv[1]
    result = validate_project(project_dir)
    
    print("\n" + "="*60)
    print("VALIDACION MEDIA - KEYWORDS")
    print("="*60)
    
    for file_path, info in result['details'].items():
        status = "OK" if info['passed'] else "FAIL"
        print(f"{status} {file_path}: {info['message']}")
    
    print("\n" + "="*60)
    if result['success']:
        print("OK: TODAS LAS VALIDACIONES PASARON")
    else:
        print("FAIL: ALGUNAS VALIDACIONES FALLARON")
    print("="*60)