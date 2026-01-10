# 🎯 EJEMPLOS PRÁCTICOS

## Ejemplo 1: Sistema de Partículas Completo

### **Paso 1: Crear tasks.json**
```json
[
  {
    "name": "Backend",
    "prompt": "Generate ONLY Python Flask code (no HTML/JS/CSS/explanations). Code: from flask import Flask, render_template; app = Flask(__name__, static_folder='static', template_folder='templates'); @app.route('/'); def index(): return render_template('index.html'); if __name__ == '__main__': app.run(port=5000, debug=True)",
    "output": "app.py"
  },
  {
    "name": "HTML",
    "prompt": "Generate ONLY HTML5 code (no CSS/JS/explanations). Code: <!DOCTYPE html><html lang='en'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><title>Particle System</title><link rel='stylesheet' href='/static/style.css'></head><body><script src='/static/script.js'></script></body></html>",
    "output": "templates/index.html"
  },
  {
    "name": "CSS",
    "prompt": "Generate ONLY CSS code (no HTML/JS/explanations). Code: body{margin:0;padding:0;background:#0a0a0a;overflow:hidden;font-family:monospace}canvas{position:fixed;top:0;left:0;width:100%;height:100vh;z-index:1}",
    "output": "static/style.css"
  },
  {
    "name": "JavaScript",
    "prompt": "Generate ONLY JavaScript code (no HTML/CSS/explanations). Code: const canvas=document.createElement('canvas');document.body.appendChild(canvas);const ctx=canvas.getContext('2d');canvas.width=window.innerWidth;canvas.height=window.innerHeight;let particles=[];for(let i=0;i<200;i++){particles.push({x:Math.random()*canvas.width,y:Math.random()*canvas.height,vx:(Math.random()-0.5)*3,vy:(Math.random()-0.5)*3,angle:Math.random()*Math.PI*2});}let mouse={x:-1000,y:-1000,active:false};canvas.addEventListener('mousemove',(e)=>{mouse.x=e.clientX;mouse.y=e.clientY;mouse.active=true;});canvas.addEventListener('mouseleave',()=>{mouse.active=false;});function update(){particles.forEach(p=>{p.angle+=0.05;const sineX=Math.sin(p.angle)*2;const sineY=Math.cos(p.angle*0.7)*2;if(mouse.active){const dx=mouse.x-p.x;const dy=mouse.y-p.y;const dist=Math.sqrt(dx*dx+dy*dy);if(dist>1&&dist<200){const force=1/(dist*dist)*50;const angle=Math.atan2(dy,dx);p.vx+=Math.cos(angle)*force;p.vy+=Math.sin(angle)*force;}}p.vx+=sineX*0.01;p.vy+=sineY*0.01;p.vx*=0.98;p.vy*=0.98;p.x+=p.vx;p.y+=p.vy;if(p.x<0)p.x=canvas.width;if(p.x>canvas.width)p.x=0;if(p.y<0)p.y=canvas.height;if(p.y>canvas.height)p.y=0;});}function draw(){ctx.fillStyle='rgba(10,10,10,0.15)';ctx.fillRect(0,0,canvas.width,canvas.height);particles.forEach(p=>{const vel=Math.sqrt(p.vx*p.vx+p.vy*p.vy);const hue=Math.min(vel*45,180);ctx.fillStyle=`hsl(${hue},100%,50%)`;ctx.beginPath();ctx.arc(p.x,p.y,2,0,Math.PI*2);ctx.fill();});}function animate(){update();draw();requestAnimationFrame(animate);}animate();",
    "output": "static/script.js"
  }
]
```

### **Paso 2: Ejecutar**
```bash
mkdir particle-system
cd particle-system
mkdir templates static
# Copiar tasks.json arriba
python tool/ask_agent_batch_v2.py --tasks tasks.json --output-dir . --template flask-simple
```

### **Paso 3: Probar**
```bash
python app.py
# Abrir: http://localhost:5000
```

---

## Ejemplo 2: Usando generate_project.py

```bash
# Genera todo automáticamente
python tool/generate_project.py my-app basic

# Resultado:
# ✅ app.py
# ✅ templates/index.html
# ✅ static/style.css
# ✅ static/script.js
```

---

## Ejemplo 3: Prompt para Archivo Individual

```bash
# Generar solo un archivo JavaScript
python tool/ask_agent.py qwen "Generate ONLY JavaScript code (no HTML/CSS). Code: const canvas=document.createElement('canvas');document.body.appendChild(canvas);const ctx=canvas.getContext('2d');canvas.width=window.innerWidth;canvas.height=window.innerHeight;" --output static/canvas.js
```

---

## Ejemplo 4: Validación de Proyecto

```bash
# Validar que todos los archivos tienen contenido correcto
python tool/validate_media.py particle-system

# Salida esperada:
============================================================
VALIDACIÓN MEDIA - KEYWORDS
============================================================
✅ particle-system/app.py: OK
✅ particle-system/templates/index.html: OK
✅ particle-system/static/style.css: OK
✅ particle-system/static/script.js: OK
============================================================
✅ TODAS LAS VALIDACIONES PASARON
============================================================
```

---

## Ejemplo 5: Estructura de Proyecto con Subcarpetas

```json
[
  {
    "name": "Backend",
    "prompt": "Generate ONLY Python Flask code... Code: [CODE]",
    "output": "my-project/app.py"
  },
  {
    "name": "HTML",
    "prompt": "Generate ONLY HTML5 code... Code: [CODE]",
    "output": "my-project/templates/index.html"
  }
]
```

**Nota:** El sistema automáticamente maneja las rutas sin duplicar carpetas.

---

## 📊 COMPARACIÓN DE ENFOQUES

| Enfoque | Tiempo | Éxito | Complejidad |
|---------|--------|-------|-------------|
| Template enhancement | 45s | 75% | Alta |
| Prompts separados | 30s | 60% | Media |
| **Prompt completo** | **7s** | **100%** | **Baja** |

---

## 🎯 MEJORES PRÁCTICAS RESUMIDAS

1. **Siempre** usar "Generate ONLY [LANG] code" al inicio
2. **Incluir** todo el código en el prompt
3. **Usar** `flask-simple` template
4. **Validar** con `validate_media.py`
5. **Verificar** tamaño de archivos > 0 bytes

---

**Documentación actualizada:** 2026-01-10