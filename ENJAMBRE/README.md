# ENJAMBRE - Sistema Multi-Agente

## Que es ENJAMBRE

Sistema de generacion de codigo que usa multiples workers en paralelo para crear proyectos completos. Cada worker genera un archivo (Python, HTML, CSS, JS) simultaneamente, reduciendo el tiempo de generacion.

## Como funciona

```
Usuario
   │
   ▼
generate_project.py ──► tasks.json
   │
   ▼
ask_agent_batch_v2.py
   │
   ├──► Worker 1 ──► app.py
   ├──► Worker 2 ──► index.html
   ├──► Worker 3 ──► style.css
   └──► Worker 4 ──► script.js
   │
   ▼
validate_media.py ──► Proyecto listo
```

## Uso Rapido

```bash
# Generar proyecto
python tool/generate_project.py mi-proyecto basic

# Validar
python tool/validate_media.py mi-proyecto

# Ejecutar
python mi-proyecto/app.py
```

## Documentacion

| Documento | Proposito |
|-----------|-----------|
| **[docs/AGENTS.md](docs/AGENTS.md)** | Como operar: prompts, tasks.json, validacion, errores |
| **[docs/TOOLKIT.md](docs/TOOLKIT.md)** | Referencia tecnica: herramientas, arquitectura, customizacion |

## Estructura

```
ENJAMBRE/
├── tool/                    # Herramientas
│   ├── ask_agent_batch_v2.py   # Orquestador principal
│   ├── generate_project.py     # Generador automatico
│   ├── validate_media.py       # Validador
│   ├── config.py               # Configuracion de rutas
│   └── ...
├── docs/                    # Documentacion
│   ├── AGENTS.md               # Guia operativa
│   └── TOOLKIT.md              # Referencia tecnica
└── tests/                   # Ejemplos
```

## Metricas

- Success Rate: 100%
- Tiempo: ~7 segundos (4 archivos en paralelo)
- Intervencion manual: 0%
