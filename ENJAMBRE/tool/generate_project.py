#!/usr/bin/env python3
"""
Generador de proyectos usando sistema enjambre con prompts optimizados
"""

import os
import sys
import json
import subprocess

from config import SCRIPTS, CONFIG_FILES, PROJECT_ROOT
from utils import load_json, save_json, ensure_dir_exists

def load_prompt_library():
    """Carga la librería de prompts"""
    return load_json(CONFIG_FILES['prompt_library'])

def create_tasks_file(project_name, prompt_type='basic'):
    """Crea tasks.json con prompts optimizados"""
    
    prompts = load_prompt_library()
    
    if prompt_type == 'full':
        tasks = [
            {
                "name": "Backend",
                "prompt": prompts['flask_basic'],
                "output": f"{project_name}/app.py"
            },
            {
                "name": "HTML",
                "prompt": prompts['html5_basic'],
                "output": f"{project_name}/templates/index.html"
            },
            {
                "name": "CSS",
                "prompt": prompts['css_dark'],
                "output": f"{project_name}/static/style.css"
            },
            {
                "name": "JavaScript",
                "prompt": prompts['js_particles_full'],
                "output": f"{project_name}/static/script.js"
            }
        ]
    else:
        # Basic: prompts directos sin prefijo
        tasks = [
            {
                "name": "Backend",
                "prompt": "from flask import Flask, render_template; app = Flask(__name__, static_folder='static', template_folder='templates'); @app.route('/'); def index(): return render_template('index.html'); if __name__ == '__main__': app.run(port=5000, debug=True)",
                "output": f"{project_name}/app.py"
            },
            {
                "name": "HTML",
                "prompt": "<!DOCTYPE html><html lang='en'><head><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><title>App</title><link rel='stylesheet' href='/static/style.css'></head><body><script src='/static/script.js'></script></body></html>",
                "output": f"{project_name}/templates/index.html"
            },
            {
                "name": "CSS",
                "prompt": "body{margin:0;padding:0;background:#0a0a0a;overflow:hidden;font-family:monospace}canvas{position:fixed;top:0;left:0;width:100%;height:100vh;z-index:1}",
                "output": f"{project_name}/static/style.css"
            },
            {
                "name": "JavaScript",
                "prompt": "const canvas=document.createElement('canvas');document.body.appendChild(canvas);const ctx=canvas.getContext('2d');canvas.width=window.innerWidth;canvas.height=window.innerHeight;let particles=[];for(let i=0;i<200;i++){particles.push({x:Math.random()*canvas.width,y:Math.random()*canvas.height,vx:(Math.random()-0.5)*3,vy:(Math.random()-0.5)*3,angle:Math.random()*Math.PI*2});}let mouse={x:-1000,y:-1000,active:false};canvas.addEventListener('mousemove',(e)=>{mouse.x=e.clientX;mouse.y=e.clientY;mouse.active=true;});canvas.addEventListener('mouseleave',()=>{mouse.active=false;});function update(){particles.forEach(p=>{p.angle+=0.05;const sineX=Math.sin(p.angle)*2;const sineY=Math.cos(p.angle*0.7)*2;if(mouse.active){const dx=mouse.x-p.x;const dy=mouse.y-p.y;const dist=Math.sqrt(dx*dx+dy*dy);if(dist>1&&dist<200){const force=1/(dist*dist)*50;const angle=Math.atan2(dy,dx);p.vx+=Math.cos(angle)*force;p.vy+=Math.sin(angle)*force;}}p.vx+=sineX*0.01;p.vy+=sineY*0.01;p.vx*=0.98;p.vy*=0.98;p.x+=p.vx;p.y+=p.vy;if(p.x<0)p.x=canvas.width;if(p.x>canvas.width)p.x=0;if(p.y<0)p.y=canvas.height;if(p.y>canvas.height)p.y=0;});}function draw(){ctx.fillStyle='rgba(10,10,10,0.15)';ctx.fillRect(0,0,canvas.width,canvas.height);particles.forEach(p=>{const vel=Math.sqrt(p.vx*p.vx+p.vy*p.vy);const hue=Math.min(vel*45,180);ctx.fillStyle=`hsl(${hue},100%,50%)`;ctx.beginPath();ctx.arc(p.x,p.y,2,0,Math.PI*2);ctx.fill();});}function animate(){update();draw();requestAnimationFrame(animate);}animate();",
                "output": f"{project_name}/static/script.js"
            }
        ]
    
    save_json(f'{project_name}/tasks.json', tasks)

    return tasks

def run_swarm(project_name, tasks_file, use_template='flask-simple'):
    """Ejecuta el sistema enjambre"""

    print(f"\nGenerando proyecto '{project_name}' con {len(tasks_file)} tareas...")

    cmd = [
        sys.executable, SCRIPTS['ask_agent_batch'],
        '--tasks', f'{project_name}/tasks.json',
        '--output-dir', project_name,
        '--template', use_template,
        '--validate',
        '--max-retries', '2'
    ]

    result = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, text=True)
    
    print(result.stdout)
    if result.returncode != 0:
        print("ERROR:", result.stderr)
        return False
    
    return True

def validate_project(project_name):
    """Valida el proyecto generado"""

    print(f"\nValidando proyecto '{project_name}'...")

    cmd = [
        sys.executable, SCRIPTS['validate_media'],
        project_name
    ]

    result = subprocess.run(cmd, cwd=PROJECT_ROOT, capture_output=True, text=True)
    
    print(result.stdout)
    
    return result.returncode == 0

def main():
    if len(sys.argv) < 2:
        print("Uso: python generate_project.py <project_name> [basic|full]")
        print("  basic: prompts directos (más rápido)")
        print("  full: prompts con prefijos (más robusto)")
        sys.exit(1)
    
    project_name = sys.argv[1]
    prompt_type = sys.argv[2] if len(sys.argv) > 2 else 'basic'
    
    # Crear directorio
    ensure_dir_exists(f'{project_name}/templates')
    ensure_dir_exists(f'{project_name}/static')
    
    # Crear tasks.json
    print(f"\n1. Creando tasks.json ({prompt_type})...")
    tasks = create_tasks_file(project_name, prompt_type)
    print(f"   {len(tasks)} tareas creadas")
    
    # Ejecutar enjambre
    print(f"\n2. Ejecutando sistema enjambre...")
    if not run_swarm(project_name, f'{project_name}/tasks.json', 'flask-simple'):
        print("   ❌ Falló la generación")
        return
    
    # Validar
    print(f"\n3. Validando resultados...")
    if not validate_project(project_name):
        print("   WARNING: Algunas validaciones fallaron")
    else:
        print("   OK: Validacion exitosa")
    
    # Resumen
    print("\n" + "="*60)
    print("RESUMEN")
    print("="*60)
    print(f"Proyecto: {project_name}")
    print(f"Modo: {prompt_type}")
    print(f"Tareas: {len(tasks)}")
    print(f"Archivos generados:")
    for task in tasks:
        file_path = task['output']
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"  OK {file_path} ({size} bytes)")
        else:
            print(f"  MISSING {file_path}")
    
    print("\nPara ejecutar:")
    print(f"  cd {project_name}")
    print(f"  python app.py")
    print(f"  Abrir: http://localhost:5000")

if __name__ == '__main__':
    main()