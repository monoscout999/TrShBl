import subprocess
import argparse
import json
import os
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import requests

from config import SCRIPTS, PROJECT_ROOT, LLM_SERVER

def load_tasks(tasks_file):
    """Carga las tareas desde un archivo JSON"""
    with open(tasks_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_template(template_name):
    """Carga un template de la librería de templates"""
    templates_path = os.path.join(os.path.dirname(__file__), 'templates.json')
    if not os.path.exists(templates_path):
        return None

    with open(templates_path, 'r', encoding='utf-8') as f:
        templates = json.load(f)

    for template in templates:
        if template['template_name'] == template_name:
            return template

    return None

def normalize_path(base_dir, output_path):
    """Evita duplicación de rutas: base_dir/file.py no se convierte en base_dir/base_dir/file.py"""
    if not base_dir or not output_path:
        return output_path
    
    # Si la ruta ya contiene el base_dir al inicio, no duplicar
    if output_path.startswith(base_dir + os.sep) or output_path.startswith(base_dir + '/'):
        return output_path
    
    return os.path.join(base_dir, output_path)

def get_contract_rules(output_file, template):
    """Genera reglas de contrato minimalistas basadas en el tipo de archivo"""
    if not template or 'contracts' not in template:
        return ""
    
    # Normalizar ruta
    output_file = output_file.replace('\\', '/')
    
    # Buscar en contratos (puede ser nombre completo o solo archivo)
    contract = None
    if output_file in template['contracts']:
        contract = template['contracts'][output_file]
    else:
        # Buscar por nombre de archivo solo
        filename = output_file.split('/')[-1]
        for key, value in template['contracts'].items():
            if key.endswith('/' + filename) or key == filename:
                contract = value
                break
    
    if not contract:
        return ""
    
    lang = contract.get('lang', '')
    
    # Reglas simplificadas
    rules = {
        'python': "⚠️ PYTHON: Solo sintaxis Python.\n",
        'html': "⚠️ HTML: Estructura HTML5.\n",
        'css': "⚠️ CSS: Propiedades CSS.\n",
        'js': "⚠️ JS: JavaScript para navegador.\n"
    }
    
    return rules.get(lang, "")

def get_example_code(output_file, template):
    """Obtiene ejemplo minimalista del template"""
    if not template or 'examples' not in template:
        return ""
    
    # Normalizar ruta
    output_file = output_file.replace('\\', '/')
    
    # Buscar en ejemplos (puede ser nombre completo o solo archivo)
    example_code = None
    if output_file in template['examples']:
        example_code = template['examples'][output_file]
    else:
        # Buscar por nombre de archivo solo
        filename = output_file.split('/')[-1]
        for key, value in template['examples'].items():
            if key.endswith('/' + filename) or key == filename:
                example_code = value
                break
    
    if not example_code:
        return ""
    
    lines = example_code.split('\n')[:5]  # Máximo 5 líneas
    return f"Ejemplo:\n```\n{'\n'.join(lines)}\n```\n"

def generate_enhanced_prompt(prompt, template_name=None, output_file=None):
    """
    Genera prompt optimizado basado en contratos simples.
    Si el prompt ya contiene "Generate ONLY", lo usa tal cual.
    """
    if not template_name or not output_file:
        return prompt
    
    # Si el prompt ya está optimizado (contiene "Generate ONLY"), devolverlo
    if "Generate ONLY" in prompt or "Generate ONLY" in prompt.upper():
        return prompt
    
    template = load_template(template_name)
    if not template or 'contracts' not in template:
        return prompt
    
    # Extraer extensión y tipo de archivo
    ext = output_file.split('.')[-1].lower()
    filename = output_file.split('/')[-1]
    
    # Buscar contrato para este archivo
    contract = None
    if filename in template['contracts']:
        contract = template['contracts'][filename]
    else:
        # Buscar por extensión
        for key, value in template['contracts'].items():
            if key.endswith(f'.{ext}'):
                contract = value
                break
    
    if not contract:
        return prompt
    
    # Determinar prefijo basado en lenguaje
    lang = contract.get('lang', '')
    framework = contract.get('framework', '')
    
    prefix_map = {
        'python': f"Generate ONLY Python code (no HTML/JS/CSS/explanations). Code: ",
        'html': f"Generate ONLY HTML5 code (no CSS/JS/explanations). Code: ",
        'css': f"Generate ONLY CSS code (no HTML/JS/explanations). Code: ",
        'js': f"Generate ONLY JavaScript code (no HTML/CSS/explanations). Code: "
    }
    
    prefix = prefix_map.get(lang, "Generate ONLY code. ")
    if framework:
        prefix = prefix_map.get(lang, "").replace("code", f"{framework} code")
    
    # Si el prompt ya empieza con el prefijo, no duplicar
    if prompt.startswith(prefix):
        return prompt
    
    return prefix + prompt

def extract_python_dependencies(file_path):
    """Extrae dependencias externas de un archivo Python"""
    if not os.path.exists(file_path):
        return []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Lista de librerías estándar de Python para filtrar
        standard_library = {
            'os', 'sys', 'json', 'time', 'datetime', 're', 'math',
            'collections', 'itertools', 'functools', 'pathlib', 'random',
            'subprocess', 'shutil', 'argparse', 'logging', 'typing',
            'threading', 'multiprocessing', 'queue', 'socket', 'urllib'
        }

        dependencies = set()

        # Detectar patrones: from X import Y, import X
        import_patterns = [
            r'from\s+([a-zA-Z0-9_]+)\s+import',
            r'import\s+([a-zA-Z0-9_]+)(?:\s+as|$)',
            r'from\s+([a-zA-Z0-9_]+)\.([a-zA-Z0-9_]+)\s+import'
        ]

        for pattern in import_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if isinstance(match, tuple):
                    import_name = match[0]
                else:
                    import_name = match

                # Filtrar imports relativos y librerías estándar
                if import_name and import_name not in standard_library and not import_name.startswith('.'):
                    # Convertir _ a - para nombres de paquetes (ej: flask_cors -> flask-cors)
                    package_name = import_name.replace('_', '-')
                    dependencies.add(package_name)

        return sorted(list(dependencies))
    except Exception as e:
        print(f"Error extrayendo dependencias de {file_path}: {e}")
        return []

def generate_requirements_txt(project_dir, dependencies):
    """Genera archivo requirements.txt con las dependencias detectadas"""
    if not dependencies:
        return False

    try:
        requirements_path = os.path.join(project_dir, 'requirements.txt')
        with open(requirements_path, 'w', encoding='utf-8') as f:
            for dep in dependencies:
                # Agregar versión mínima para Flask
                if dep == 'flask':
                    f.write(f"{dep}>=2.0.0\n")
                else:
                    f.write(f"{dep}\n")
        return True
    except Exception as e:
        print(f"Error generando requirements.txt: {e}")
        return False

def check_forbidden_imports(file_path, template_name):
    """Verifica si el archivo tiene imports prohibidos según el template"""
    if not os.path.exists(file_path):
        return []

    try:
        template = load_template(template_name)
        if not template or 'forbidden_imports' not in template:
            return []

        forbidden_imports = template['forbidden_imports']
        warnings = []

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        for forbidden in forbidden_imports:
            # Convertir _ a - y viceversa para match
            patterns = [forbidden, forbidden.replace('-', '_')]
            for pattern in patterns:
                if f'from {pattern}' in content or f'import {pattern}' in content:
                    warnings.append(f"Import prohibido detectado: {pattern} (no permitido en template {template_name})")
                    break

        return warnings
    except Exception as e:
        print(f"Error verificando imports prohibidos: {e}")
        return []

def early_validation_check(output_file, template_name=None):
    """Validación temprana post-generación (sin IA) para detectar errores obvios"""
    if not output_file:
        return {'valid': True, 'errors': [], 'warnings': []}

    errors = []
    warnings = []

    # Check 1: Archivo existe?
    if not os.path.exists(output_file):
        errors.append(f"Archivo no creado: {output_file}")
        return {'valid': False, 'errors': errors, 'warnings': warnings}

    # Check 2: Tamaño mínimo (evitar archivos vacíos o truncados)
    file_size = os.path.getsize(output_file)
    if file_size < 50:  # Menos de 50 bytes es sospechosamente pequeño
        errors.append(f"Archivo demasiado pequeño: {file_size} bytes (mínimo esperado: 50)")
        return {'valid': False, 'errors': errors, 'warnings': warnings}

    # Check 3: Estructura básica según extensión
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            content = f.read()

        if output_file.endswith('.html'):
            if '</html>' not in content:
                errors.append("HTML incompleto: falta </html>")
            if '<body>' not in content or '</body>' not in content:
                errors.append("HTML incompleto: falta <body> o </body>")
            if '<head>' not in content or '</head>' not in content:
                errors.append("HTML incompleto: falta <head> o </head>")

        elif output_file.endswith('.py'):
            if not content.strip():
                errors.append("Archivo Python vacío")
            # Check básico para Flask
            if 'from flask import' not in content:
                errors.append("Falta import de Flask en archivo Python")

            # Check 4: Verificar imports prohibidos según template
            if template_name:
                import_warnings = check_forbidden_imports(output_file, template_name)
                warnings.extend(import_warnings)

        elif output_file.endswith('.js'):
            if not content.strip():
                errors.append("Archivo JavaScript vacío")
            
            # Check básico para evitar código Python en JS
            # Python comment style: # comment at beginning
            lines = content.strip().split('\n')
            if lines and lines[0].strip().startswith('#'):
                errors.append("Archivo JavaScript contiene comentarios estilo Python (#) - debe usar // o /* */")
            
            # Check más estricto para contenido Python
            python_patterns = [
                'from flask import',
                'from flask import Flask',
                'app = Flask(',
                '@app.route(',
                'def index(',
                "render_template('",
                "if __name__ == '__main__':",
                'app.run(port=5000',
                'app.run(port=5000,',
                'debug=True'
            ]
            for pattern in python_patterns:
                if pattern in content:
                    errors.append(f"Archivo JavaScript contiene código Python: '{pattern}' - debe ser código de navegador")
                    break  # Solo reportar el primer patrón Python
            
            # Check 2: Detectar Node.js/CommonJS patterns
            if "require('" in content or "require(\"" in content or "require(`" in content:
                errors.append("JavaScript contiene require() - sintaxis Node.js/CommonJS (debe ser para navegador)")
            if 'module.exports' in content:
                errors.append("JavaScript contiene module.exports - sintaxis Node.js (no funciona en navegador)")
            
            # Check 3: Detectar ES Modules (import from)
            if 'import ' in content and ' from ' in content:
                # Solo validar si es ES Modules real (import con from), no solo import
                if not content.count('import ') > 5:  # Permitir múltiples import básicos pero no muchos
                    errors.append("JavaScript contiene 'import ... from' - ES Modules (requiere bundler, usar <script> en HTML)")
            
            # Check 4: Detectar server-side patterns
            nodejs_patterns = ['fs.', 'path.', 'process.', '__dirname', '__filename']
            for pattern in nodejs_patterns:
                if pattern in content:
                    errors.append(f"JavaScript contiene '{pattern}' - API de Node.js server-side (no funciona en navegador)")
                    break  # Solo reportar el primer error de Node.js
    except UnicodeDecodeError:
        errors.append("Error de encoding al leer el archivo")
    except Exception as e:
        errors.append(f"Error al leer archivo: {str(e)}")

    # Check 4: Estructura de carpetas (evitar nested folders)
    path_parts = output_file.replace('\\', '/').split('/')
    # Detectar si hay patrones como tests/test-suite/test-suite/
    for i in range(len(path_parts) - 1):
        if path_parts[i] == path_parts[i+1]:
            errors.append(f"Estructura de carpetas duplicada detectada: {path_parts[i]}")

    is_valid = len(errors) == 0
    return {'valid': is_valid, 'errors': errors, 'warnings': warnings}

def execute_task(task, agent="qwen", mode="default", max_retries=3, template_name=None):
    """Ejecuta una tarea individual con retry automático"""
    prompt = task.get('prompt', '')
    output = task.get('output', '')
    task_name = task.get('name', 'unnamed')

    # Mejorar prompt si se especifica un template
    enhanced_prompt = generate_enhanced_prompt(prompt, template_name, output)

    cmd = [
        'python',
        SCRIPTS['ask_agent'],
        agent,
        enhanced_prompt,
        '--mode', mode
    ]

    if output:
        cmd.extend(['--output', output])

    attempts = []
    for attempt in range(1, max_retries + 1):
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            attempt_result = {
                'attempt': attempt,
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr
            }
            attempts.append(attempt_result)

            if result.returncode == 0:
                # Early validation check (solo si hay archivo de salida)
                if output:
                    early_check = early_validation_check(output)
                    if not early_check['valid']:
                        # Early validation failed - si hay mas intentos, reintentar. Si no, reportar error.
                        if attempt < max_retries:
                            error_info = f"\n\nPREVIOUS ERROR (Intento {attempt}): Early validation failed - {'; '.join(early_check['errors'])}"
                            cmd = [
                                'python',
                                SCRIPTS['ask_agent'],
                                agent,
                                enhanced_prompt + error_info,
                                '--mode', mode
                            ]
                            if output:
                                cmd.extend(['--output', output])
                            continue  # Continuar al siguiente intento
                        else:
                            # No hay mas intentos, reportar error
                            error_msg = "Early validation failed: " + "; ".join(early_check['errors'])
                            return {
                                'name': task_name,
                                'success': False,
                                'output': result.stdout,
                                'error': error_msg,
                                'file_saved': output,
                                'attempts': attempts,
                                'total_attempts': attempt
                            }

                # Si llegamos aqui, todo esta bien (subprocess exitoso y validacion pasada)
                return {
                    'name': task_name,
                    'success': True,
                    'output': result.stdout,
                    'error': '',
                    'file_saved': output if output else None,
                    'attempts': attempts,
                    'total_attempts': attempt
                }
            else:
                # Si falló y hay más intentos, agregar información de error al prompt
                if attempt < max_retries:
                    error_info = f"\n\nPREVIOUS ERROR (Intento {attempt}): {result.stderr[:200]}"
                    cmd = [
                        'python',
                        SCRIPTS['ask_agent'],
                        agent,
                        enhanced_prompt + error_info,
                        '--mode', mode
                    ]
                    if output:
                        cmd.extend(['--output', output])

        except subprocess.TimeoutExpired:
            attempts.append({
                'attempt': attempt,
                'success': False,
                'output': '',
                'error': 'Timeout exceeded'
            })
        except Exception as e:
            attempts.append({
                'attempt': attempt,
                'success': False,
                'output': '',
                'error': str(e)
            })

    return {
        'name': task_name,
        'success': False,
        'output': '',
        'error': f'Failed after {max_retries} attempts',
        'file_saved': None,
        'attempts': attempts,
        'total_attempts': max_retries
    }

def validate_output(project_path, template_type="flask"):
    """Ejecuta validación post-generación con verificación de estructura de carpetas"""
    try:
        # === VALIDACIÓN DE ESTRUCTURA DE CARPETAS ===
        print(f"\n  Verificando estructura de carpetas en: {project_path}")
        
        # Verificar carpetas obligatorias
        required_folders = ['templates', 'static']
        missing_folders = []
        
        for folder in required_folders:
            folder_path = os.path.join(project_path, folder)
            if not os.path.exists(folder_path):
                missing_folders.append(folder)
        
        if missing_folders:
            return {
                'success': False,
                'error': f"Faltan carpetas obligatorias: {', '.join(missing_folders)}"
            }

        print(f"  [OK] Carpetas 'templates/' y 'static/' existen")

        # Verificar archivos obligatorios según template
        template = load_template(template_type)
        if template and 'files' in template:
            missing_files = []
            for filename in template['files'].keys():
                file_path = os.path.join(project_path, filename)
                if not os.path.exists(file_path):
                    missing_files.append(filename)

            if missing_files:
                return {
                    'success': False,
                    'error': f"Faltan archivos: {', '.join(missing_files)}"
                }

            print(f"  [OK] Todos los archivos del template existen")
        
        # Ejecutar validación específica del template
        try:
            report_path = os.path.join(project_path, 'validation_report.json')
            result = subprocess.run(
                ['python', SCRIPTS['validate_output'], '--path', project_path, '--type', template_type, '--output', report_path],
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=30
            )

            validation_output = result.stdout
        except Exception as e:
            print(f"  [ERROR] Error ejecutando validación: {str(e)}")
            return {
                'success': False,
                'error': f"Error ejecutando validación: {str(e)}"
            }

        # Parsear si existe el reporte JSON
        if os.path.exists(report_path):
            try:
                with open(report_path, 'r', encoding='utf-8') as f:
                    validation_data = json.load(f)
                return validation_data
            except Exception as e:
                print(f"  [ERROR] Error leyendo reporte de validación: {str(e)}")

        # Si no hay reporte JSON, extraer del output
        return {
            'success': result.returncode == 0,
            'output': validation_output
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def test_generation(project_path, port=5000):
    """Ejecuta pruebas automáticas sobre la aplicación generada"""
    try:
        test_script = os.path.join(os.path.dirname(__file__), 'test_generation.py')
        result = subprocess.run(
            ['python', test_script, '--path', project_path, '--port', str(port)],
            capture_output=True,
            text=True,
            timeout=30
        )

        return {
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def check_qwen_health():
    """Verifica que el servidor LLM esté corriendo antes de iniciar"""
    try:
        response = requests.post(
            f"{LLM_SERVER['url']}{LLM_SERVER['endpoint']}",
            json={
                "model": LLM_SERVER['model'],
                "messages": [{"role": "user", "content": "test"}],
                "max_tokens": 5
            },
            timeout=5
        )
        return response.status_code == 200
    except Exception:
        return False

def create_directory_structure(base_dir):
    """Crea la estructura de carpetas necesaria"""
    if not base_dir:
        return True
    
    try:
        os.makedirs(base_dir, exist_ok=True)
        templates_dir = os.path.join(base_dir, 'templates')
        static_dir = os.path.join(base_dir, 'static')
        os.makedirs(templates_dir, exist_ok=True)
        os.makedirs(static_dir, exist_ok=True)
        return True
    except Exception as e:
        print(f"ADVERTENCIA: Error creando estructura de carpetas: {e}")
        return False

def update_metrics_execution(execution_report_path, metrics_file='metrics.json'):
    """Actualiza metrics.json automáticamente después de cada ejecución"""
    try:
        result = subprocess.run(
            ['python', SCRIPTS['update_metrics'],
             '--execution-report', execution_report_path,
             '--metrics-file', metrics_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            print("Métricas actualizadas automáticamente")
        else:
            print("No se pudieron actualizar las métricas automáticamente")
    except Exception as e:
        print(f"ADVERTENCIA: Error actualizando métricas: {e}")

def main():
    parser = argparse.ArgumentParser(description='Ejecuta multiples tareas en paralelo usando workers con retry y validacion')
    parser.add_argument('--tasks', required=True, help='Archivo JSON con las tareas a ejecutar')
    parser.add_argument('--agent', default='qwen', choices=['qwen', 'mimo'], help='Agente a usar')
    parser.add_argument('--mode', default='default', choices=['default', 'patch'], help='Modo de ejecucion')
    parser.add_argument('--output-dir', help='Directorio base para archivos de salida (opcional)')
    parser.add_argument('--template', help='Template a usar para mejorar prompts (flask, cyberpunk, etc.)')
    parser.add_argument('--validate', action='store_true', help='Ejecutar validacion post-generacion')
    parser.add_argument('--test', action='store_true', help='Ejecutar pruebas automaticas post-generacion')
    parser.add_argument('--max-retries', type=int, default=3, help='Maximo de intentos por tarea')
    parser.add_argument('--metrics-file', default='metrics.json', help='Archivo de métricas a actualizar')

    args = parser.parse_args()

    # === PRE-FLIGHT CHECKS ===
    print("Realizando pre-flight checks...")
    
    # 1. Verificar Phi-3 está corriendo
    if not check_qwen_health():
        print(f"ERROR: El servidor LLM no esta corriendo en {LLM_SERVER['url']}")
        print("   Solucion: Inicia el servidor LLM primero")
        return

    print("   OK: Phi-3-mini esta operativo")
    
    # 2. Verificar archivo de tareas existe
    if not os.path.exists(args.tasks):
        print(f"ERROR: No existe el archivo de tareas: {args.tasks}")
        return
    
    print(f"   OK: Archivo de tareas encontrado: {args.tasks}")
    
    # 3. Crear estructura de carpetas si se especifica output-dir
    if args.output_dir:
        if not create_directory_structure(args.output_dir):
            print("ERROR: No se pudo crear la estructura de carpetas")
            return
        print(f"   OK: Estructura de carpetas creada: {args.output_dir}")
    
    # 4. Verificar template existe si se especifica
    if args.template:
        template = load_template(args.template)
        if not template:
            print(f"ADVERTENCIA: Template '{args.template}' no encontrado en templates.json")
        else:
            print(f"   OK: Template encontrado: {args.template}")

    print("Pre-flight checks completados\n")

    # Cargar tareas
    tasks = load_tasks(args.tasks)

    # Si se especifica output-dir, normalizar rutas para evitar duplicación
    if args.output_dir:
        for task in tasks:
            if 'output' in task and task['output']:
                task['output'] = normalize_path(args.output_dir, task['output'])

    print(f"Ejecutando {len(tasks)} tareas EN PARALELO con {args.agent.upper()} en modo {args.mode.upper()}...")
    if args.template:
        print(f"Template: {args.template} (prompts mejorados)")
    if args.max_retries > 1:
        print(f"Max retries: {args.max_retries} por tarea")
    print("-" * 60)

    # Ejecutar todas las tareas en paralelo usando ThreadPoolExecutor
    results = []
    start_time = time.time()

    # Calcular workers óptimos basado en número de tareas
    num_tasks = len(tasks)
    if num_tasks <= 4:
        workers = num_tasks  # 1:1 mapping para tareas pequeñas
    elif num_tasks <= 8:
        workers = 4  # Max 4 workers para tareas medianas
    else:
        workers = min(4 + (num_tasks // 4), 8)  # Escalar hasta 8 para proyectos grandes

    print(f"Workers: {workers} (optimizado para {num_tasks} tareas)")
    print("-" * 60)

    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_task = {
            executor.submit(execute_task, task, args.agent, args.mode, args.max_retries, args.template): task
            for task in tasks
        }

        # Esperar a que TODOS los futures se completen antes de continuar
        for future in as_completed(future_to_task):
            task = future_to_task[future]
            task_name = task.get('name', 'unnamed')[:50]
            try:
                result = future.result(timeout=120)  # Timeout por future individual
                results.append(result)

                if result['success']:
                    retries_msg = f" ({result['total_attempts']} intentos)" if result['total_attempts'] > 1 else ""
                    print(f"[OK] {task_name}{retries_msg}")
                    if result['file_saved']:
                        print(f"  Archivo guardado: {result['file_saved']}")
                else:
                    print(f"[ERROR] {task_name}: {result['error'][:100]}")
                    print(f"  Intentos: {result['total_attempts']}")
            except Exception as exc:
                print(f"[CRITICAL] {task_name} genero excepcion: {exc}")
                results.append({
                    'name': task_name,
                    'success': False,
                    'output': '',
                    'error': str(exc),
                    'file_saved': None
                })

    elapsed_time = time.time() - start_time

    # Verificar que todos los tasks se completaron
    if len(results) != len(tasks):
        print(f"\n[WARNING] ADVERTENCIA: Solo se completaron {len(results)}/{len(tasks)} tareas")

    # Esperar a que todos los archivos se escriban completamente (sin delay artificial)
    print("\n[SYNC] Verificando que todos los archivos estén escritos en disco...")
    max_wait_time = 5.0  # Máximo 5 segundos esperando
    check_interval = 0.1  # Verificar cada 100ms
    waited = 0

    while waited < max_wait_time:
        all_files_ready = True
        for result in results:
            if result['success'] and result['file_saved']:
                file_path = result['file_saved']
                if not os.path.exists(file_path):
                    all_files_ready = False
                    break
                # Verificar que el archivo tenga contenido (> 0 bytes)
                if os.path.getsize(file_path) == 0:
                    all_files_ready = False
                    break

        if all_files_ready:
            print("[SYNC] Todos los archivos están listos")
            break

        time.sleep(check_interval)
        waited += check_interval

    if waited >= max_wait_time:
        print(f"[WARNING] Algunos archivos no están listos después de {max_wait_time}s")

    # Validación post-generación
    validation_result = None
    if args.validate and args.output_dir:
        print("\n" + "=" * 60)
        print("Ejecutando validacion post-generacion...")
        print(f"[DIR] Directorio: {args.output_dir}")
        print(f"[INFO] Tasks completados: {len(results)}/{len(tasks)}")
        validation_result = validate_output(args.output_dir, args.template or 'flask')
        print(f"Validacion: {'PASADA' if validation_result.get('success') else 'FALLIDA'}")

    # Pruebas automáticas
    test_result = None
    if args.test and args.output_dir:
        print("\n" + "=" * 60)
        print("Ejecutando pruebas automaticas...")
        test_result = test_generation(args.output_dir)
        print(f"Pruebas: {'PASADAS' if test_result.get('success') else 'FALLIDAS'}")

    # Resumen
    successful = sum(1 for r in results if r['success'])
    total_attempts = sum(r.get('total_attempts', 1) for r in results)

    print("=" * 60)
    print(f"RESUMEN: {successful}/{len(results)} tareas completadas exitosamente")
    print(f"Tiempo total: {elapsed_time:.2f} segundos")
    print(f"Total intentos: {total_attempts} (avg: {total_attempts/len(results):.1f} por tarea)")

    # Guardar reporte extendido
    report_file = os.path.join(args.output_dir or '.', 'execution_report.json')

    # Enhanced: Agregar detalles por archivo
    enhanced_results = []
    for result in results:
        enhanced_result = result.copy()
        if result.get('file_saved'):
            # Agregar información del archivo generado
            file_info = {
                'path': result['file_saved'],
                'size_bytes': os.path.getsize(result['file_saved']) if os.path.exists(result['file_saved']) else 0,
                'exists': os.path.exists(result['file_saved'])
            }
            enhanced_result['file_info'] = file_info
        enhanced_results.append(enhanced_result)

    report_data = {
        'results': enhanced_results,
        'validation': validation_result,
        'testing': test_result,
        'summary': {
            'successful': successful,
            'total': len(results),
            'elapsed_time': elapsed_time,
            'total_attempts': total_attempts,
            'avg_time_per_task': elapsed_time / len(results) if results else 0
        },
        'execution_info': {
            'workers_used': workers if 'workers' in locals() else 4,
            'template': args.template,
            'agent': args.agent,
            'mode': args.mode,
            'max_retries': args.max_retries
        }
    }

    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    print(f"Reporte guardado en: {report_file}")
    
    # === ACTUALIZACIÓN AUTOMÁTICA DE MÉTRICAS ===
    if successful > 0:
        print("\n" + "=" * 60)
        print("Actualizando métricas automáticamente...")
        update_metrics_execution(report_file, args.metrics_file)

if __name__ == '__main__':
    main()
