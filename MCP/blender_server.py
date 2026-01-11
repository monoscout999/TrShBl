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
                    s.settimeout(1.0)
                    conn, addr = s.accept()
                    with conn:
                        data = conn.recv(1024 * 10).decode('utf-8')
                        if data:
                            # Push to queue for main thread execution
                            result_evt = threading.Event()
                            self.queue.append((data, conn, result_evt))
                            # Wait for main thread to process (optional, but good for sync)
                            # result_evt.wait(timeout=5.0) 
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"Server Error: {e}")

    def process_queue(self):
        while self.queue:
            code, conn, evt = self.queue.pop(0)
            try:
                # Redirect output
                from io import StringIO
                import sys
                old_stdout = sys.stdout
                redirected_output = sys.stdout = StringIO()
                
                # Execute
                exec_globals = {"bpy": bpy, "context": bpy.context}
                exec(code, exec_globals)
                
                output = redirected_output.getvalue()
                sys.stdout = old_stdout
                
                response = {"status": "success", "output": output}
                conn.sendall(json.dumps(response).encode('utf-8'))
            except Exception as e:
                error_msg = traceback.format_exc()
                response = {"status": "error", "message": str(e), "traceback": error_msg}
                try:
                    conn.sendall(json.dumps(response).encode('utf-8'))
                except:
                    pass
            finally:
                evt.set()
        return 0.1 # Run again in 0.1s

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

# To run within Blender:
# server = BlenderServer()
# server.start()

if __name__ == "__main__":
    # If already running, stop it first (useful for re-runs in Blender)
    # This is a global singleton-ish check could be added
    server = BlenderServer()
    server.start()
