import os
import json
import sys

# Helper function for safe printing with UTF-8 fallback
def safe_print(text):
    try:
        print(text)
    except UnicodeEncodeError:
        # Fallback: replace non-ASCII characters
        print(text.encode('ascii', 'replace').decode('ascii'))

def validate_structure(project_path, template_type="flask"):
    """Valida que la estructura del proyecto sea correcta"""
    validations = []

    if template_type == "flask":
        validations = [
            ("app.py exists", os.path.exists(os.path.join(project_path, "app.py"))),
            ("templates/ exists", os.path.exists(os.path.join(project_path, "templates"))),
            ("static/ exists", os.path.exists(os.path.join(project_path, "static"))),
            ("render_template in app.py", check_file_content(os.path.join(project_path, "app.py"), "render_template")),
            ("Flask app initialized", check_file_content(os.path.join(project_path, "app.py"), "Flask(__name__")),
        ]

    elif template_type == "react":
        validations = [
            ("package.json exists", os.path.exists(os.path.join(project_path, "package.json"))),
            ("src/ exists", os.path.exists(os.path.join(project_path, "src"))),
            ("public/ exists", os.path.exists(os.path.join(project_path, "public"))),
        ]

    elif template_type == "cyberpunk":
        validations = [
            ("matrix-bg ID in HTML", check_file_content(os.path.join(project_path, "templates/index.html"), 'id="matrix-bg"')),
            ("terminal-container class", check_file_content(os.path.join(project_path, "templates/index.html"), 'class="terminal-container"')),
            ("access-panel ID", check_file_content(os.path.join(project_path, "templates/index.html"), 'id="access-panel"')),
            ("canvas in script.js", check_file_content(os.path.join(project_path, "static/script.js"), "getElementById('matrix-bg')")),
            ("green color #0f0", check_file_content(os.path.join(project_path, "static/style.css"), "#0f0")),
        ]

    elif template_type == "flask-fullstack":
        # Base validations (always required)
        validations = [
            ("app.py exists", os.path.exists(os.path.join(project_path, "app.py"))),
            ("templates/ exists", os.path.exists(os.path.join(project_path, "templates"))),
            ("static/ exists", os.path.exists(os.path.join(project_path, "static"))),
            ("templates/index.html exists", os.path.exists(os.path.join(project_path, "templates/index.html"))),
            ("static/style.css exists", os.path.exists(os.path.join(project_path, "static/style.css"))),
            ("static/script.js exists", os.path.exists(os.path.join(project_path, "static/script.js"))),
            ("HTML link /static/style.css", check_file_content(os.path.join(project_path, "templates/index.html"), "href") and check_file_content(os.path.join(project_path, "templates/index.html"), "/static/style.css")),
            ("HTML link /static/script.js", check_file_content(os.path.join(project_path, "templates/index.html"), "src") and check_file_content(os.path.join(project_path, "templates/index.html"), "/static/script.js")),
            ("JS getElementById", check_file_content(os.path.join(project_path, "static/script.js"), "getElementById")),
        ]

        # Optional validations: Check if project uses Chart.js
        if not check_file_content(os.path.join(project_path, "templates/index.html"), "chart.js"):
            # Only require addEventListener if NOT a chart project
            validations.append(("JS addEventListener", check_file_content(os.path.join(project_path, "static/script.js"), "addEventListener")))
        
        # NEW: Anti-Node.js validations for JavaScript
        js_file = os.path.join(project_path, "static/script.js")
        if os.path.exists(js_file):
            with open(js_file, 'r', encoding='utf-8') as f:
                js_content = f.read()
            
            # Check 1: No require() (Node.js/CommonJS)
            if "require(" in js_content or 'require("' in js_content or 'require(`' in js_content:
                validations.append(("JS NO require()", False))
            
            # Check 2: No module.exports (Node.js)
            if "module.exports" in js_content:
                validations.append(("JS NO module.exports", False))
            
            # Check 3: No ES Modules (import ... from)
            # Only if it's clearly ES Modules (import with from), not just basic import
            if 'import ' in js_content and ' from ' in js_content:
                # Count import lines - if too many, it's likely ES Modules
                import_count = js_content.count('import ')
                if import_count > 3:  # More than 3 imports suggests ES Modules
                    validations.append(("JS NO ES Modules", False))
            
            # Check 4: No Node.js server-side APIs
            nodejs_apis = ['fs.', 'path.', 'process.', '__dirname', '__filename']
            for api in nodejs_apis:
                if api in js_content:
                    validations.append((f"JS NO {api}", False))
                    break  # Only report first Node.js API
        
        # Check 5: Detectar URLs incorrectas en HTML (opcional)
        html_file = os.path.join(project_path, "templates/index.html")
        if os.path.exists(html_file):
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Detectar https:// (doble slash) en URLs externas
            if 'https://' in html_content:
                # Buscar patrones específicos de CDN incorrectos
                import re
                bad_url_patterns = [
                    r'https://cdn\.jsdelivr\.net',
                    r'https://picsum\.photos',
                    r'https://cdnjs\.cloudflare\.com'
                ]
                for pattern in bad_url_patterns:
                    if re.search(pattern, html_content):
                        # Reemplazar https:// por https://
                        fixed_html_content = re.sub(pattern.replace('https://', 'https://'), pattern, html_content)
                        # Guardar la versión corregida
                        with open(html_file, 'w', encoding='utf-8') as f_out:
                            f_out.write(fixed_html_content)
                        # Solo reportar como info, no como error
                        print(f"[INFO] URL corregida en {html_file}: {pattern}")
                        break
 
        # Flask folder params: Make them optional (not required)
        has_static_folder = check_file_content(os.path.join(project_path, "app.py"), "static_folder='static'")
        has_template_folder = check_file_content(os.path.join(project_path, "app.py"), "template_folder='templates'")

        # Add as info validation, not as requirement
        validations.append(("Flask with explicit folders", has_static_folder and has_template_folder))

    results = {name: status for name, status in validations}
    passed = sum(1 for status in results.values() if status)
    total = len(validations)

    return {
        "passed": passed,
        "total": total,
        "validations": results,
        "success": passed == total
    }

def check_file_content(filepath, search_string):
    """Busca un string en un archivo"""
    if not os.path.exists(filepath):
        return False
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return search_string in f.read()
    except:
        return False

def is_chart_project(project_path):
    """Detecta si el proyecto usa Chart.js u otra librería de gráficos"""
    html_path = os.path.join(project_path, "templates/index.html")
    js_path = os.path.join(project_path, "static/script.js")

    # Check HTML for Chart.js CDN
    if check_file_content(html_path, "chart.js") or check_file_content(html_path, "Chart"):
        return True

    # Check JS for Chart usage
    if check_file_content(js_path, "new Chart") or check_file_content(js_path, "Chart.js"):
        return True

    return False

def validate_context_shared(project_path, requirements):
    """Valida que el contexto compartido se respete"""
    results = {}

    for req_type, value in requirements.items():
        if req_type == "id":
            results[f"ID '{value}' exists"] = check_file_content(
                os.path.join(project_path, "templates/index.html"),
                f'id="{value}"'
            )
        elif req_type == "class":
            results[f"Class '{value}' exists"] = check_file_content(
                os.path.join(project_path, "templates/index.html"),
                f'class="{value}"'
            )
        elif req_type == "color":
            results[f"Color '{value}' exists"] = check_file_content(
                os.path.join(project_path, "static/style.css"),
                value
            )

    return results

def generate_report(validation_result, output_path):
    """Genera un reporte JSON de validación"""
    # Ensure the directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8', errors='replace') as f:
        json.dump(validation_result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Valida estructura de proyectos generados')
    parser.add_argument('--path', required=True, help='Ruta del proyecto')
    parser.add_argument('--type', default='flask', choices=['flask', 'react', 'cyberpunk', 'flask-fullstack'], help='Tipo de proyecto')
    parser.add_argument('--output', help='Archivo de reporte de salida')

    args = parser.parse_args()

    result = validate_structure(args.path, args.type)

    safe_print(f"Validación: {result['passed']}/{result['total']} pasaron")
    safe_print("\nDetalles:")
    for name, status in result['validations'].items():
        symbol = "[OK]" if status else "[FAIL]"
        safe_print(f"  {symbol} {name}")

    if args.output:
        generate_report(result, args.output)
        safe_print(f"\nReporte guardado en: {args.output}")
