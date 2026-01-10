#!/usr/bin/env python3
"""
Sistema de actualización automática de métricas para el multiagente.
Actualiza metrics.json basado en execution_report.json después de cada ejecución.
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path

def load_json(filepath):
    """Carga un archivo JSON con manejo de errores."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        print(f"⚠️  Error: No se pudo parsear {filepath}")
        return None

def save_json(filepath, data):
    """Guarda datos en archivo JSON con formato bonito."""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"ADVERTENCIA: Error guardando {filepath}: {e}")
        return False

def analyze_execution_report(report):
    """Analiza execution_report.json y extrae métricas."""
    if not report:
        return None
    
    results = report.get('results', [])
    summary = report.get('summary', {})
    validation = report.get('validation', {})
    
    # Contadores
    successful = summary.get('successful', 0)
    total = summary.get('total', 0)
    total_attempts = summary.get('total_attempts', 0)
    elapsed_time = summary.get('elapsed_time', 0)
    
    # Calcular métricas principales
    success_rate = (successful / total * 100) if total > 0 else 0
    avg_retries = (total_attempts / total) if total > 0 else 0
    
    # Detectar errores comunes
    errors = {
        'python_js_mix': 0,
        'missing_folders': 0,
        'wrong_paths': 0,
        'encoding_unicode': 0
    }
    
    # Validación de estructura
    if validation and not validation.get('success', True):
        error_msg = validation.get('error', '').lower()
        if 'carpetas' in error_msg or 'folders' in error_msg:
            errors['missing_folders'] = 1
        if 'path' in error_msg or 'ruta' in error_msg:
            errors['wrong_paths'] = 1
    
    # Analizar archivos generados para detectar problemas
    for task in results:
        if not task.get('success', False):
            error = task.get('error', '').lower()
            if 'unicode' in error or 'encoding' in error:
                errors['encoding_unicode'] += 1
            if 'python' in error and 'javascript' in error:
                errors['python_js_mix'] += 1
        
        # Verificar archivos guardados para detectar rutas incorrectas
        saved_file = task.get('file_saved', '')
        if saved_file:
            # Detectar archivos anidados (cyberpunk-terminal/cyberpunk-terminal/)
            if saved_file.count('cyberpunk-terminal') > 1:
                errors['wrong_paths'] += 1
    
    # Detectar template usado (de execution_report o análisis de archivos)
    template_used = 'unknown'
    # Buscar en los resultados si hay indicios de qué template se usó
    for task in results:
        output = task.get('output', '').lower()
        if 'cyberpunk' in output:
            template_used = 'cyberpunk-landing'
            break
        elif 'flask' in output and 'fullstack' in output:
            template_used = 'flask-fullstack'
            break
        elif 'flask' in output:
            template_used = 'flask-basic'
            break
        elif 'quantum' in output:
            template_used = 'quantum-vortex'
            break
    
    return {
        'successful': successful,
        'total': total,
        'success_rate': round(success_rate, 2),
        'avg_retries': round(avg_retries, 2),
        'elapsed_time': round(elapsed_time, 2),
        'errors': errors,
        'template_used': template_used
    }

def update_metrics(metrics_file, execution_report_file):
    """Actualiza metrics.json con datos de execution_report.json."""
    
    # Cargar métricas actuales
    metrics = load_json(metrics_file)
    if not metrics:
        print(f"ADVERTENCIA: No se encontro {metrics_file}, creando nuevo...")
        metrics = {
            "projects_created": 0,
            "success_rate": 0,
            "avg_retries": 0,
            "common_errors": {
                "python_js_mix": 0,
                "missing_folders": 0,
                "wrong_paths": 0,
                "encoding_unicode": 0
            },
            "templates_used": {
                "flask-fullstack": 0,
                "flask-basic": 0,
                "cyberpunk-landing": 0,
                "quantum-vortex": 0
            },
            "execution_history": []
        }
    
    # Cargar execution report
    execution_report = load_json(execution_report_file)
    if not execution_report:
        print(f"ERROR: No se pudo cargar {execution_report_file}")
        return False
    
    # Analizar reporte
    analysis = analyze_execution_report(execution_report)
    if not analysis:
        print("ERROR: Error analizando execution report")
        return False
    
    # Actualizar contadores principales
    if analysis['successful'] == analysis['total'] and analysis['total'] > 0:
        metrics['projects_created'] += 1
    
    # Calcular nuevo success_rate promedio
    old_rate = metrics['success_rate']
    old_count = metrics['projects_created'] - 1 if metrics['projects_created'] > 0 else 0
    new_rate = ((old_rate * old_count) + analysis['success_rate']) / (old_count + 1) if old_count > 0 else analysis['success_rate']
    metrics['success_rate'] = round(new_rate, 2)
    
    # Calcular nuevo avg_retries promedio
    old_retries = metrics['avg_retries']
    new_retries = ((old_retries * old_count) + analysis['avg_retries']) / (old_count + 1) if old_count > 0 else analysis['avg_retries']
    metrics['avg_retries'] = round(new_retries, 2)
    
    # Actualizar errores comunes
    for error_type, count in analysis['errors'].items():
        if count > 0:
            metrics['common_errors'][error_type] += count
    
    # Actualizar templates usados
    if analysis['template_used'] != 'unknown':
        if analysis['template_used'] in metrics['templates_used']:
            metrics['templates_used'][analysis['template_used']] += 1
    
    # Agregar a historial
    history_entry = {
        "timestamp": datetime.now().isoformat(),
        "template": analysis['template_used'],
        "success_rate": analysis['success_rate'],
        "avg_retries": analysis['avg_retries'],
        "elapsed_time": analysis['elapsed_time'],
        "tasks": analysis['total'],
        "errors": analysis['errors']
    }
    
    if 'execution_history' not in metrics:
        metrics['execution_history'] = []
    
    metrics['execution_history'].append(history_entry)
    
    # Mantener solo últimas 50 entradas en historial
    if len(metrics['execution_history']) > 50:
        metrics['execution_history'] = metrics['execution_history'][-50:]
    
    # Guardar métricas actualizadas
    if save_json(metrics_file, metrics):
        print("OK: Metricas actualizadas exitosamente")
        print(f"   - Proyectos creados: {metrics['projects_created']}")
        print(f"   - Success rate promedio: {metrics['success_rate']}%")
        print(f"   - Avg retries: {metrics['avg_retries']}")
        print(f"   - Template usado: {analysis['template_used']}")
        return True
    else:
        print("ERROR: No se pudieron guardar las metricas")
        return False

def main():
    """Punto de entrada principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Actualizar metrics.json basado en execution_report.json')
    parser.add_argument('--execution-report', required=True, help='Ruta a execution_report.json')
    parser.add_argument('--metrics-file', default='metrics.json', help='Ruta a metrics.json')
    
    args = parser.parse_args()
    
    # Verificar que exista execution_report
    if not os.path.exists(args.execution_report):
        print(f"ERROR: No existe: {args.execution_report}")
        sys.exit(1)
    
    # Actualizar métricas
    success = update_metrics(args.metrics_file, args.execution_report)
    
    if success:
        print("\nRESUMEN DE METRICAS ACTUALIZADAS:")
        metrics = load_json(args.metrics_file)
        if metrics:
            print(json.dumps(metrics, indent=2))
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()