# SYSTEM TOOLKIT DOCUMENTATION

## Modulo Centralizado: utils/

Nueva estructura que centraliza codigo compartido entre todos los scripts:

```
tool/utils/
├── __init__.py      # Exporta API publica
├── file_ops.py      # load_json, save_json, save_output, ensure_dir_exists
├── validators.py    # WRONG_LANG_PATTERNS, EXPECTED_KEYWORDS, validate_file_language
└── code_extract.py  # extract_code_from_markdown
```

**Uso desde cualquier script:**
```python
from utils import load_json, save_json, ensure_dir_exists
from utils import validate_file_language, WRONG_LANG_PATTERNS
```

**Beneficios:**
- Un solo lugar para cada funcion
- Cambios se propagan automaticamente
- Menos codigo duplicado
- Testing mas facil

---

## Available Tools

### **1. ask_agent_batch_v2.py** - Main Orchestrator
**Purpose:** Generates multiple files in parallel using swarm intelligence

**Usage:**
```bash
python tool/ask_agent_batch_v2.py --tasks tasks.json --output-dir my-project --template flask-simple --max-retries 2
```

**Key Features:**
- ✅ Parallel execution (up to 4 workers)
- ✅ Automatic path normalization (prevents duplication)
- ✅ Smart prompt enhancement
- ✅ Early validation
- ✅ Execution report generation

**Modified Functions:**
- `normalize_path()` - Prevents `project/project/file.py` duplication
- `generate_enhanced_prompt()` - Adds language-specific prefixes
- `early_validation_check()` - Validates file content

---

### **2. generate_project.py** - Automatic Generator
**Purpose:** One-command project generation

**Usage:**
```bash
# Basic mode (recommended)
python tool/generate_project.py my-project basic

# Full mode (with prompt library)
python tool/generate_project.py my-project full
```

**What it does:**
1. Creates directory structure
2. Generates tasks.json with optimized prompts
3. Executes swarm system
4. Combines JS files if needed
5. Validates results
6. Shows summary

---

### **3. validate_media.py** - Media Validation
**Purpose:** Validates files contain required keywords

**Usage:**
```bash
python tool/validate_media.py my-project
```

**Validation Rules:**
- **Python:** Flask, render_template, @app.route
- **HTML:** <!DOCTYPE html>, <link rel="stylesheet", <script src
- **CSS:** body, margin, background, canvas
- **JS:** const canvas, particles, requestAnimationFrame, mouse

---

### **4. ask_agent.py** - Single File Generator
**Purpose:** Generate one file at a time

**Usage:**
```bash
python tool/ask_agent.py qwen "Generate code" --output file.py
```

---

### **5. modular_generator.py** - Modular File Generator
**Purpose:** Genera archivos complejos divididos en modulos, combina y valida.

**Cuando usarlo:**
- Archivos CSS > 1000 caracteres
- Archivos JS > 2000 caracteres
- Cualquier archivo que falle por ser muy largo

**Usage:**
```bash
# Basico
python tool/modular_generator.py --modules modules.json

# Con directorio de salida
python tool/modular_generator.py --modules modules.json --output-dir my-project

# Dry-run (ver que haria sin ejecutar)
python tool/modular_generator.py --modules modules.json --dry-run
```

**Formato modules.json:**
```json
{
  "output_file": "static/style.css",
  "file_type": "css",
  "modules": [
    {"name": "CSS-Base", "prompt": "Generate ONLY CSS: body reset, dark bg", "order": 1},
    {"name": "CSS-Controls", "prompt": "Generate ONLY CSS: control panel", "order": 2}
  ]
}
```

**Flujo:**
1. Lee modules.json
2. Genera cada modulo en paralelo
3. Verifica resultados (EMPTY, WRONG_LANG)
4. Combina en orden
5. Valida archivo final
6. Limpia temporales

---

## 🎯 SYSTEM ARCHITECTURE

```
User Request
    ↓
generate_project.py (or manual tasks.json)
    ↓
ask_agent_batch_v2.py
    ↓
┌─────────────────────────────────────┐
│  Worker 1  │  Worker 2  │  Worker 3 │
│  (Python)  │  (HTML)    │  (CSS)    │
└─────────────────────────────────────┘
    ↓
Validation (validate_media.py)
    ↓
Execution Report
    ↓
User Result
```

---

## 🔬 HALLAZGOS TÉCNICOS

### **Problema Original:**
El modelo generaba código Python en archivos .js y viceversa.

### **Causa Raíz:**
Los prompts no especificaban claramente el lenguaje objetivo.

### **Solución Implementada:**
```python
# ANTES (fallaba)
prompt = "200 particles, mouse attraction"

# DESPUÉS (funciona)
prompt = "Generate ONLY JavaScript code... Code: [CÓDIGO_COMPLETO]"
```

### **Por qué funciona:**
1. **Prefijo claro**: "Generate ONLY JavaScript code"
2. **Contexto completo**: Todo el código en el prompt
3. **Sin ambigüedad**: No hay lugar para interpretación

---

## 📋 ESTRUCTURA DE PROYECTO RECOMENDADA

```
project-name/
├── app.py                      # Flask backend
├── templates/
│   └── index.html             # HTML structure
├── static/
│   ├── style.css              # Styles
│   └── script.js              # JavaScript logic
├── tasks.json                 # Task definitions
├── execution_report.json      # Generation log
└── README.md                  # Project docs
```

---

## ⚡ PERFORMANCE METRICS

| Metric | Target | Achieved |
|--------|--------|----------|
| Success Rate | 100% | ✅ 100% |
| Avg Retries | 1.0 | ✅ 1.0 |
| Generation Time | <10s | ✅ ~7s |
| File Size | >100 bytes | ✅ All >200 |

---

## 🎯 BEST PRACTICES

### **1. Prompt Construction**
```python
# Template
"Generate ONLY {LANG} code (no other languages). Code: {CODE}"

# Example
"Generate ONLY JavaScript code (no HTML/CSS). Code: const canvas=..."
```

### **2. File Structure**
- Always create `templates/` and `static/` folders first
- Use relative paths in tasks.json
- Keep prompts under 2000 characters

### **3. Validation**
- Always check file sizes > 0
- Verify keywords are present
- Test execution before finalizing

### **4. Error Recovery**
- If file empty: Split prompt into smaller parts
- If wrong content: Add stronger prefix
- If structure wrong: Use `flask-simple` template

---

## 🔧 CUSTOMIZATION

### **Adding New Templates**
Edit `tool/templates.json`:
```json
{
  "template_name": "my-template",
  "contracts": {
    "file.ext": {"lang": "language"}
  }
}
```

### **Adding New Prompts**
Edit `tool/prompt-library.json`:
```json
{
  "my_prompt": "Generate ONLY [LANG] code... Code: [CODE]"
}
```

---

## 📞 TROUBLESHOOTING

### **Phi-3-mini not responding**
```bash
curl http://127.0.0.1:8080
# Should return JSON response
```

### **Files not generated**
1. Check `execution_report.json`
2. Verify `tasks.json` syntax
3. Run with `--max-retries 3`

### **Wrong content**
1. Verify "Generate ONLY" prefix
2. Check prompt length
3. Use `validate_media.py`

---

**Last Updated:** 2026-01-10  
**Version:** 2.0 (Optimized)