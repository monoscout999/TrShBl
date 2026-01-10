import socket
import json
from fastmcp import FastMCP

# Configuration
BLENDER_HOST = 'localhost'
BLENDER_PORT = 8006

# Initialize FastMCP server
mcp = FastMCP("BlenderControl")

def send_to_blender(code: str):
    """Internal helper to send code to the Blender listener."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((BLENDER_HOST, BLENDER_PORT))
            s.sendall(code.encode('utf-8'))
            data = s.recv(1024 * 10)
            return json.loads(data.decode('utf-8'))
    except ConnectionRefusedError:
        return {"status": "error", "message": "Could not connect to Blender. Is the listener running?"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@mcp.tool()
def execute_blender_python(code: str) -> str:
    """Executes Python code directly in Blender using the bpy API.
    
    Args:
        code: The Python script string to execute.
    """
    result = send_to_blender(code)
    if result["status"] == "success":
        return f"Success!\nOutput:\n{result.get('output', '')}"
    else:
        return f"Error: {result['message']}\n{result.get('traceback', '')}"

@mcp.tool()
def create_mesh_cube(name: str = "Cube", size: float = 2.0, location: list = [0, 0, 0]) -> str:
    """Creates a cube in the current Blender scene.
    
    Args:
        name: Name of the object.
        size: Size of the cube.
        location: [x, y, z] coordinates.
    """
    code = f"""
import bpy
bpy.ops.mesh.primitive_cube_add(size={size}, location={location})
bpy.context.active_object.name = "{name}"
print(f"Created cube '{name}' at {location}")
"""
    return execute_blender_python(code)

@mcp.tool()
def get_scene_summary() -> str:
    """Returns a summary of objects currently in the Blender scene."""
    code = """
import bpy
summary = []
for obj in bpy.data.objects:
    summary.append(f"- {obj.name} (Type: {obj.type}, Location: {list(obj.location)})")
print("Scene Summary:\\n" + "\\n".join(summary))
"""
    return execute_blender_python(code)

if __name__ == "__main__":
    mcp.run()
