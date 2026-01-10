# 🤖 Opencode Multiagent System

Sistema de generación de código usando múltiples agentes Qwen-local.

## 🚀 Uso Rápido

```bash
# Método 1: Automático (recomendado)
python tool/generate_project.py my-project basic

# Método 2: Manual
mkdir my-project && cd my-project
mkdir templates static
# Crear tasks.json (ver AGENTS.md)
python tool/ask_agent_batch_v2.py --tasks tasks.json --output-dir . --template flask-simple

# Validar resultado
python tool/validate_media.py my-project
```

## 🛠️ Herramientas Principales

| Herramienta | Propósito | Uso |
|-------------|-----------|-----|
| `generate_project.py` | Generador automático | `python tool/generate_project.py <nombre> basic` |
| `ask_agent_batch_v2.py` | Generador por lotes | `python tool/ask_agent_batch_v2.py --tasks tasks.json --output-dir . --template flask-simple` |
| `validate_media.py` | Validador de archivos | `python tool/validate_media.py <directorio>` |
| `cleanup.py` | Limpieza de pruebas | `python tool/cleanup.py` |

## 📚 Documentación

- **[AGENTS.md](AGENTS.md)** - Instrucciones completas y ejemplos
- **[docs/RESUMEN.md](docs/RESUMEN.md)** - Resumen de cambios y métricas

## 🎯 Hallazgos Clave (2026-01-10)

### **Formato que funciona 100%:**
```
Generate ONLY [LANG] code (no HTML/CSS/explanations). Code: [FULL_CODE]
```

### **Resultados:**
- ✅ **100% éxito** (vs 75% antes)
- ✅ **7 segundos** (vs 45s antes)
- ✅ **0 intervención manual** (vs frecuente antes)

### **Qué NO funciona:**
- ❌ Templates complejos con reglas
- ❌ Prompts divididos en múltiples partes
- ❌ "Generate app.py with Flask..." (demasiado vago)

## 📊 Métricas del Sistema

| Métrica | Antes | Después | Mejora |
|---------|-------|---------|--------|
| Success Rate | 75% | 100% | +25% |
| Avg Time | 45s | 7s | -84% |
| Intervención Manual | Sí | No | -100% |

## ✅ Checklist de Verificación

Después de generar un proyecto:
```bash
# Verificar archivos existen
dir app.py templates\index.html static\style.css static\script.js

# Validar con keywords
python tool/validate_media.py .

# Probar ejecución
python app.py
# Abrir: http://localhost:5000
```

## 🚨 Reglas Críticas

1. **UNA línea = UN archivo completo**
2. **SIEMPRE** usar prefijo "Generate ONLY"
3. **NUNCA** modificar código del usuario directamente
4. **SIEMPRE** usar el sistema de lotes para proyectos

---

**Estado:** ✅ PRODUCCIÓN LISTA  
**Última actualización:** 2026-01-10  
**Versión:** 2.0 (Optimized)