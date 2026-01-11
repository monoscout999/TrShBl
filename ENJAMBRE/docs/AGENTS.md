# Guia del Sistema ENJAMBRE

## Rol del Orquestador

**NO generes codigo directamente.** Usa el sistema batch:

```bash
python tool/generate_project.py <nombre> basic
```

---

## Uso

### Metodo Automatico (Recomendado)
```bash
python tool/generate_project.py mi-proyecto basic
```

### Metodo Manual
```bash
mkdir mi-proyecto
mkdir mi-proyecto/templates mi-proyecto/static
# Crear tasks.json (ver ejemplo abajo)
python tool/ask_agent_batch_v2.py --tasks tasks.json --output-dir mi-proyecto --template flask-simple
```

---

## Formato de Prompts (CRITICO)

### El Formato Optimo: Codigo Completo Inline

```
Generate ONLY [LANG] code (no HTML/CSS/explanations). Code: [CODIGO_LITERAL_COMPLETO]
```

**Por que funciona:** El LLM copia el codigo en lugar de interpretar instrucciones.
Esto elimina errores de interpretacion y genera resultados 100% predecibles.

### Comparacion de Enfoques

| Enfoque | Tiempo | Exito | Complejidad |
|---------|--------|-------|-------------|
| Template enhancement | 45s | 75% | Alta |
| Prompts descriptivos | 30s | 60% | Media |
| **Codigo completo inline** | **7s** | **100%** | **Baja** |

### NO Funciona

- `"Generate app.py with Flask..."` (vago, LLM interpreta libremente)
- `"Create a button that starts audio..."` (genera HTML en lugar de JS)
- Templates complejos con reglas
- Prompts divididos en partes

### Leccion Aprendida

Prompt vago:
```
"Generate button that starts audio and removes itself"
```
Resultado: LLM genera HTML con `<button>` en lugar de JavaScript.

Prompt correcto:
```
"Generate ONLY JavaScript code. Code: var btn=document.createElement('button');btn.onclick=function(){initAudio();btn.remove();};document.body.appendChild(btn);"
```
Resultado: Copia exacta del codigo esperado.

---

## Ejemplo tasks.json

```json
[
  {
    "name": "Backend",
    "prompt": "Generate ONLY Python Flask code (no HTML/JS/CSS). Code: from flask import Flask, render_template; app = Flask(__name__, static_folder='static', template_folder='templates'); @app.route('/'); def index(): return render_template('index.html'); if __name__ == '__main__': app.run(port=5000, debug=True)",
    "output": "app.py"
  },
  {
    "name": "HTML",
    "prompt": "Generate ONLY HTML5 code (no CSS/JS). Code: <!DOCTYPE html><html lang='en'><head><meta charset='UTF-8'><title>App</title><link rel='stylesheet' href='/static/style.css'></head><body><script src='/static/script.js'></script></body></html>",
    "output": "templates/index.html"
  },
  {
    "name": "CSS",
    "prompt": "Generate ONLY CSS code (no HTML/JS). Code: body{margin:0;background:#0a0a0a;overflow:hidden}canvas{position:fixed;top:0;left:0;width:100%;height:100vh}",
    "output": "static/style.css"
  },
  {
    "name": "JavaScript",
    "prompt": "Generate ONLY JavaScript code (no HTML/CSS). Code: const canvas=document.createElement('canvas');document.body.appendChild(canvas);const ctx=canvas.getContext('2d');canvas.width=window.innerWidth;canvas.height=window.innerHeight;function animate(){ctx.fillStyle='rgba(10,10,10,0.1)';ctx.fillRect(0,0,canvas.width,canvas.height);requestAnimationFrame(animate);}animate();",
    "output": "static/script.js"
  }
]
```

---

## Herramientas

| Herramienta | Uso |
|-------------|-----|
| `generate_project.py` | `python tool/generate_project.py <nombre> basic` |
| `ask_agent_batch_v2.py` | `python tool/ask_agent_batch_v2.py --tasks tasks.json --output-dir . --template flask-simple` |
| `validate_media.py` | `python tool/validate_media.py <directorio>` |

---

## Validacion

```bash
# Verificar archivos
dir mi-proyecto\app.py
dir mi-proyecto\templates\index.html
dir mi-proyecto\static\style.css
dir mi-proyecto\static\script.js

# Validar contenido
python tool/validate_media.py mi-proyecto

# Probar
python mi-proyecto/app.py
# Abrir: http://localhost:5000
```

---

## Errores Comunes

| Problema | Causa | Solucion |
|----------|-------|----------|
| Archivos vacios | Prompt muy largo | Acortar prompt |
| HTML en JS | Falta "Generate ONLY" | Agregar prefijo |
| Python en CSS | Template enhancement | Usar prompts directos |
| Rutas incorrectas | Path mal escrito | Usar rutas relativas |

---

## Troubleshooting

**Generacion falla:**
1. Verificar Qwen: `curl http://127.0.0.1:8080`
2. Reducir longitud del prompt
3. Usar `generate_project.py`

**Archivos vacios:**
1. Prompt muy largo - acortar
2. Timeout - reintentar

**Contenido incorrecto:**
1. Verificar prefijo "Generate ONLY"
2. Revisar formato del prompt

---

## Reglas

1. **NUNCA** modificar codigo del usuario directamente
2. **SIEMPRE** usar sistema batch para proyectos
3. **SIEMPRE** verificar archivos despues de generar
4. **SIEMPRE** usar prefijo "Generate ONLY"
