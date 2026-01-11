#!/usr/bin/env python3
"""
Generador modular para archivos complejos.
Genera modulos en paralelo, combina y valida.
"""

import argparse
import json
import os
import subprocess
import tempfile

from config import SCRIPTS, PROJECT_ROOT, TIMEOUTS, GENERATION
from utils import (
    WRONG_LANG_PATTERNS,
    EXPECTED_KEYWORDS,
    load_json,
    save_json,
    ensure_dir_exists,
    validate_file_language
)


class ModularGenerator:
    def __init__(self, modules_file, output_dir=None, keep_temp=False, dry_run=False):
        self.modules_file = modules_file
        self.output_dir = output_dir or '.'
        self.keep_temp = keep_temp
        self.dry_run = dry_run
        self.temp_dir = None
        self.temp_files = []
        self.results = []

    def load_modules(self):
        """Carga y valida modules.json"""
        data = load_json(self.modules_file)
        if data is None:
            raise FileNotFoundError(f"No existe o error: {self.modules_file}")

        # Validar estructura
        required = ['output_file', 'file_type', 'modules']
        for field in required:
            if field not in data:
                raise ValueError(f"Falta campo requerido: {field}")

        if not data['modules']:
            raise ValueError("Lista de modulos vacia")

        # Validar cada modulo
        for i, module in enumerate(data['modules']):
            if 'name' not in module:
                raise ValueError(f"Modulo {i} sin nombre")
            if 'prompt' not in module:
                raise ValueError(f"Modulo {module['name']} sin prompt")
            if 'order' not in module:
                module['order'] = i + 1

        # Ordenar por order
        data['modules'] = sorted(data['modules'], key=lambda x: x['order'])

        return data

    def generate_tasks_json(self, config):
        """Crea tasks.json temporal para ask_agent_batch_v2"""
        file_type = config['file_type']
        ext = {'css': 'css', 'js': 'js', 'html': 'html'}.get(file_type, file_type)

        tasks = []
        for module in config['modules']:
            # Asegurar prefijo correcto
            prompt = module['prompt']
            if not prompt.upper().startswith('GENERATE ONLY'):
                lang_name = {'css': 'CSS', 'js': 'JavaScript', 'html': 'HTML'}.get(file_type, file_type.upper())
                prompt = f"Generate ONLY {lang_name} code (no other languages). {prompt}"

            temp_filename = f"_temp_{module['name'].lower().replace(' ', '_')}.{ext}"
            temp_path = os.path.join(self.temp_dir, temp_filename)
            self.temp_files.append(temp_path)

            tasks.append({
                'name': module['name'],
                'prompt': prompt,
                'output': temp_path
            })

        tasks_file = os.path.join(self.temp_dir, '_modular_tasks.json')
        save_json(tasks_file, tasks)

        return tasks_file

    def execute_batch(self, tasks_file):
        """Ejecuta ask_agent_batch_v2.py y retorna resultados"""
        cmd = [
            'python', SCRIPTS['ask_agent_batch'],
            '--tasks', tasks_file,
            '--max-retries', '2'
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            cwd=PROJECT_ROOT,
            timeout=TIMEOUTS['modular']
        )

        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr
        }

    def check_module_result(self, module_name, file_path, file_type):
        """Verifica resultado de un modulo: OK, EMPTY, WRONG_LANG"""
        result = validate_file_language(file_path, file_type)
        return {'status': result['status'], 'message': result.get('message', ''), 'size': result.get('size', 0)}

    def detect_duplicates(self, content, min_block_size=50):
        """Detecta bloques de codigo duplicados"""
        lines = content.split('\n')
        seen_blocks = {}
        duplicates = []

        for i in range(len(lines) - 2):
            block = '\n'.join(lines[i:i+3]).strip()
            if len(block) > min_block_size:
                if block in seen_blocks:
                    duplicates.append({
                        'block': block[:50] + '...',
                        'first_line': seen_blocks[block],
                        'second_line': i
                    })
                else:
                    seen_blocks[block] = i

        return duplicates

    def combine_modules(self, config):
        """Combina modulos en orden"""
        output_file = os.path.join(self.output_dir, config['output_file'])

        # Crear directorio si no existe
        ensure_dir_exists(os.path.dirname(output_file))

        combined_content = []
        total_size = 0

        for temp_file in self.temp_files:
            if os.path.exists(temp_file):
                with open(temp_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    combined_content.append(content)
                    total_size += len(content)

        if not combined_content:
            return {'success': False, 'error': 'No hay contenido para combinar'}

        # Unir con separadores
        separator = '\n\n/* --- MODULE --- */\n\n' if config['file_type'] == 'css' else '\n\n// --- MODULE ---\n\n'
        final_content = separator.join(combined_content)

        # Detectar duplicados
        duplicates = self.detect_duplicates(final_content)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(final_content)

        return {
            'success': True,
            'output_file': output_file,
            'size': len(final_content),
            'duplicates': len(duplicates),
            'duplicate_details': duplicates[:3] if duplicates else []
        }

    def validate_combined(self, file_path, file_type):
        """Valida archivo combinado final"""
        if not os.path.exists(file_path):
            return {'valid': False, 'error': 'Archivo no existe'}

        size = os.path.getsize(file_path)
        if size < GENERATION['min_combined_size']:
            return {'valid': False, 'error': f'Archivo muy pequeno: {size} bytes'}

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Verificar brackets balanceados
        open_brackets = content.count('{') + content.count('(') + content.count('[')
        close_brackets = content.count('}') + content.count(')') + content.count(']')

        if abs(open_brackets - close_brackets) > 2:
            return {'valid': False, 'error': 'Brackets desbalanceados'}

        # Verificar keywords
        keywords = EXPECTED_KEYWORDS.get(file_type, [])
        found = sum(1 for kw in keywords if kw in content)

        return {
            'valid': True,
            'size': size,
            'keywords_found': found,
            'keywords_expected': len(keywords)
        }

    def cleanup(self):
        """Elimina archivos temporales si no --keep-temp"""
        if self.keep_temp:
            print(f"[KEEP] Archivos temporales en: {self.temp_dir}")
            return 0

        deleted = 0
        for temp_file in self.temp_files:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
                    deleted += 1
            except Exception:
                pass

        # Eliminar tasks.json temporal
        tasks_file = os.path.join(self.temp_dir, '_modular_tasks.json')
        if os.path.exists(tasks_file):
            try:
                os.remove(tasks_file)
                deleted += 1
            except Exception:
                pass

        return deleted

    def run(self):
        """Ejecuta flujo completo"""
        # 1. Cargar modulos
        print(f"[LOAD] {self.modules_file}")
        config = self.load_modules()
        print(f"       {len(config['modules'])} modulos para {config['output_file']}")

        if self.dry_run:
            print("\n[DRY-RUN] Modulos a generar:")
            for m in config['modules']:
                print(f"  {m['order']}. {m['name']}: {m['prompt'][:50]}...")
            return {'dry_run': True, 'modules': len(config['modules'])}

        # 2. Crear directorio temporal
        self.temp_dir = tempfile.mkdtemp(prefix='modular_')
        print(f"[TEMP] {self.temp_dir}")

        # 3. Generar tasks.json
        tasks_file = self.generate_tasks_json(config)
        print(f"[TASKS] {len(config['modules'])} tareas generadas")

        # 4. Ejecutar batch
        print("[GEN] Ejecutando generacion en paralelo...")
        batch_result = self.execute_batch(tasks_file)

        if not batch_result['success']:
            print(f"[ERROR] Batch fallo: {batch_result['stderr'][:200]}")
            self.cleanup()
            return {'success': False, 'error': 'Batch failed'}

        # 5. Verificar resultados de cada modulo
        all_ok = True
        for i, module in enumerate(config['modules']):
            temp_file = self.temp_files[i]
            result = self.check_module_result(module['name'], temp_file, config['file_type'])
            self.results.append({'module': module['name'], **result})

            if result['status'] == 'OK':
                print(f"[GEN] {module['name']}... OK ({result['size']} bytes)")
            else:
                print(f"[GEN] {module['name']}... {result['status']} - {result['message']}")
                all_ok = False

        if not all_ok:
            failed = [r for r in self.results if r['status'] != 'OK']
            print(f"\n[PARTIAL] {len(failed)} modulos fallaron, no se combina")
            self.cleanup()
            return {'success': False, 'error': 'Some modules failed', 'results': self.results}

        # 6. Combinar modulos
        print(f"[COMBINE] {len(config['modules'])} modulos -> {config['output_file']}")
        combine_result = self.combine_modules(config)

        if not combine_result['success']:
            print(f"[ERROR] Combinacion fallo: {combine_result['error']}")
            self.cleanup()
            return {'success': False, 'error': combine_result['error']}

        if combine_result['duplicates'] > 0:
            print(f"[WARN] {combine_result['duplicates']} bloques duplicados detectados")

        # 7. Validar archivo combinado
        validation = self.validate_combined(combine_result['output_file'], config['file_type'])
        print(f"[VALIDATE] Keywords: {validation.get('keywords_found', 0)}/{validation.get('keywords_expected', 0)}, "
              f"Size: {validation.get('size', 0)} bytes")

        if not validation['valid']:
            print(f"[ERROR] Validacion fallo: {validation['error']}")

        # 8. Limpiar temporales
        deleted = self.cleanup()
        print(f"[CLEAN] {deleted} archivos temporales eliminados")

        output_path = combine_result['output_file']
        print(f"\n[DONE] {output_path} generado exitosamente")

        return {
            'success': True,
            'output_file': output_path,
            'size': combine_result['size'],
            'modules': len(config['modules']),
            'duplicates': combine_result['duplicates'],
            'validation': validation
        }


def main():
    parser = argparse.ArgumentParser(description='Generador modular para archivos complejos')
    parser.add_argument('--modules', required=True, help='Archivo modules.json con definicion de modulos')
    parser.add_argument('--output-dir', default='.', help='Directorio de salida')
    parser.add_argument('--keep-temp', action='store_true', help='Mantener archivos temporales')
    parser.add_argument('--dry-run', action='store_true', help='Mostrar que haria sin ejecutar')

    args = parser.parse_args()

    generator = ModularGenerator(
        modules_file=args.modules,
        output_dir=args.output_dir,
        keep_temp=args.keep_temp,
        dry_run=args.dry_run
    )

    try:
        result = generator.run()
        if result.get('success'):
            exit(0)
        else:
            exit(1)
    except Exception as e:
        print(f"[FATAL] {e}")
        exit(1)


if __name__ == '__main__':
    main()
