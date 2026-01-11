import bpy
import math
import mathutils

def sample_curve(curve_obj, resolution=100):
    """
    Returns a list of vectors representing points along the curve.
    """
    degp = bpy.context.evaluated_depsgraph_get()
    curve_eval = curve_obj.evaluated_get(degp)
    # Convert to mesh to get points
    try:
        mesh = curve_eval.to_mesh()
    except:
        return []
    
    verts = [curve_obj.matrix_world @ v.co for v in mesh.vertices]
    curve_eval.to_mesh_clear()
    
    return verts

def setup_camera_flight_v3(combat_duration=60, flight_duration=120):
    cam = bpy.data.objects.get("Camera")
    if not cam:
        bpy.ops.object.camera_add()
        cam = bpy.context.active_object
        cam.name = "Camera"
        
    cam.animation_data_clear()
    cam.constraints.clear()
    
    # Update: Look for "Camera_Path_X" (Invisible curves)
    paths = []
    for i in range(1, 100):
        # The generator names them 'Camera_Path_{i}'
        p = bpy.data.objects.get(f"Camera_Path_{i}")
        if p:
            paths.append(p)
        elif i > 1:
            break
            
    if not paths:
        print("No Camera Paths found (Camera_Path_X). Run map_gen_v3.py first.")
        return

    print(f"Baking flight path for {len(paths)} segments...")
    
    current_frame = 1
    
    # 1. Start Loop
    for i, path_obj in enumerate(paths):
        points = sample_curve(path_obj)
        if not points:
            continue
            
        start_loc = points[0]
        end_loc = points[-1]
        
        # --- COMBAT PHASE (Static) ---
        cam.location = start_loc
        cam.keyframe_insert(data_path="location", frame=current_frame)
        
        # Look Rotation (Track towards next point if possible, or just level)
        # Fix: Keep camera level (X rotation 90 deg usually)
        # We'll just look at the next point but keep Z up.
        cam.rotation_euler = (math.radians(90), 0, 0) # Default forward? 
        # Actually in Blender Cam -Z is forward.
        # Let's target the center of the next room?
        # For prototype, look along path tangent.
        
        if len(points) > 1:
            vec = points[1] - points[0]
            rot = vec.to_track_quat('-Z', 'Y').to_euler()
            cam.rotation_euler = rot
        cam.keyframe_insert(data_path="rotation_euler", frame=current_frame)
        
        # Wait
        current_frame += combat_duration
        cam.location = start_loc
        cam.keyframe_insert(data_path="location", frame=current_frame)
        cam.keyframe_insert(data_path="rotation_euler", frame=current_frame)
        
        # --- FLIGHT PHASE (Move) ---
        num_points = len(points)
        
        for f in range(flight_duration):
            t = f / flight_duration
            idx = int(t * (num_points - 1))
            loc = points[idx]
            
            # Rotation
            next_idx = min(idx + 5, num_points - 1) # Look ahead 5 points for smoothness
            direction = points[next_idx] - loc
            if direction.length > 0.1:
                target_rot = direction.to_track_quat('-Z', 'Y').to_euler()
                cam.rotation_euler = target_rot
                cam.keyframe_insert(data_path="rotation_euler", frame=current_frame + f)
            
            cam.location = loc
            cam.keyframe_insert(data_path="location", frame=current_frame + f)
            
        current_frame += flight_duration
        
    bpy.context.scene.frame_end = current_frame
    print("Baked V3 complete.")

setup_camera_flight_v3()
