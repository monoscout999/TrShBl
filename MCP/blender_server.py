import socket
import threading
import bpy
import json
import traceback

# Configuration
HOST = 'localhost'
PORT = 8006

class BlenderServer:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(BlenderServer, cls).__new__(cls)
            cls._instance.running = False
            cls._instance.thread = None
            cls._instance.queue = []
        return cls._instance

    def run_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((HOST, PORT))
            s.listen()
            print(f"Blender Listener started on {HOST}:{PORT}")
            while self.running:
                try:
                    s.settimeout(0.5)
                    conn, addr = s.accept()
                    data = conn.recv(1024 * 10).decode('utf-8')
                    if data:
                        self.queue.append((data, conn))
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"Server Error: {e}")

    def process_queue(self):
        while self.queue:
            code, conn = self.queue.pop(0)
            try:
                from io import StringIO
                import sys
                old_stdout = sys.stdout
                redirected_output = sys.stdout = StringIO()
                
                exec_globals = {"bpy": bpy, "context": bpy.context}
                print(f"Executing code: {code[:50]}...")
                exec(code, exec_globals)
                
                output = redirected_output.getvalue()
                sys.stdout = old_stdout
                
                response = {"status": "success", "output": output}
                print(f"Sending success response: {len(output)} bytes")
                conn.sendall(json.dumps(response).encode('utf-8'))
            except Exception as e:
                import traceback
                error_msg = traceback.format_exc()
                response = {"status": "error", "message": str(e), "traceback": error_msg}
                try:
                    conn.sendall(json.dumps(response).encode('utf-8'))
                except:
                    pass
            finally:
                try:
                    conn.close()
                except:
                    pass
        return 0.1

    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self.run_server)
            self.thread.daemon = True
            self.thread.start()
            bpy.app.timers.register(self.process_queue)
            print("Blender MCP Listener initialized.")

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        if bpy.app.timers.is_registered(self.process_queue):
            bpy.app.timers.unregister(self.process_queue)
        print("Blender MCP Listener stopped.")

if __name__ == "__main__":
    server = BlenderServer()
    server.start()
