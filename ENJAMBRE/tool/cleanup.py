#!/usr/bin/env python3
"""
Limpieza de archivos de prueba
Elimina proyectos de prueba generados durante el desarrollo
"""

import os
import shutil
import sys

def cleanup_project(project_dir):
    """Elimina un proyecto de prueba"""
    if not os.path.exists(project_dir):
        print(f"SKIP: No existe: {project_dir}")
        return False
    
    try:
        shutil.rmtree(project_dir)
        print(f"OK: Eliminado: {project_dir}")
        return True
    except Exception as e:
        print(f"FAIL: Error al eliminar {project_dir}: {e}")
        return False

def main():
    """Punto de entrada principal"""
    print("\n" + "="*60)
    print("CLEANUP - TEST FILES")
    print("="*60 + "\n")
    
    # Lista de proyectos de prueba a eliminar
    test_projects = [
        'tests/particle-system-test',
        'test-project',
        'my-project',
        'demo-project'
    ]
    
    # Directorios de prueba en tool/
    test_files = [
        'tool/test_tasks.json',
        'tool/example_tasks.json'
    ]
    
    cleaned = 0
    failed = 0
    
    # Limpiar proyectos
    for project in test_projects:
        if cleanup_project(project):
            cleaned += 1
        else:
            # No contar como fallo si no existe
            if os.path.exists(project):
                failed += 1
    
    # Limpiar archivos sueltos
    for file_path in test_files:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"OK: Eliminado: {file_path}")
                cleaned += 1
            except Exception as e:
                print(f"FAIL: Error al eliminar {file_path}: {e}")
                failed += 1
        else:
            # Verificar si existe en cualquier ruta relativa
            for root, dirs, files in os.walk('.'):
                if file_path in files:
                    full_path = os.path.join(root, file_path)
                    try:
                        os.remove(full_path)
                        print(f"OK: Eliminado: {full_path}")
                        cleaned += 1
                    except Exception as e:
                        print(f"FAIL: Error al eliminar {full_path}: {e}")
                        failed += 1
    
    print("\n" + "="*60)
    print(f"SUMMARY: {cleaned} deleted, {failed} errors")
    print("="*60)
    
    if failed == 0 and cleaned > 0:
        print("\nOK: Cleanup completed successfully")
        return 0
    elif cleaned == 0:
        print("\nINFO: No test files to clean")
        return 0
    else:
        print(f"\nWARN: Partial cleanup ({failed} errors)")
        return 1

if __name__ == '__main__':
    sys.exit(main())