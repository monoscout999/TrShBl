import bpy
import mathutils

def sample_curve(curve_obj, resolution=100):
    """
    Returns a list of vectors representing points along the curve.
    Uses Blender's evaluation system to get the actual deformed path.
    """
    # Create a temporary dependency graph to evaluate the curve
    degp = bpy.context.evaluated_depsgraph_get()
    curve_eval = curve_obj.evaluated_get(degp)
    mesh = curve_eval.to_mesh()
    
    verts = [curve_obj.matrix_world @ v.co for v in mesh.vertices]
    
    # Cleanup
    curve_eval.to_mesh_clear()
    
    return verts

def setup_camera_flight_baked(combat_duration=60, flight_duration=120):
    cam = bpy.data.objects.get("Camera")
    if not cam:
        bpy.ops.object.camera_add()
        cam = bpy.context.active_object
        cam.name = "Camera"
        
    # Clear everything
    cam.animation_data_clear()
    cam.constraints.clear()
    
    # Find paths
    paths = []
    for i in range(1, 100):
        p = bpy.data.objects.get(f"Path_{i}")
        if p:
            paths.append(p)
        elif i > 1:
            break
            
    print(f"Baking flight path for {len(paths)} segments...")
    
    current_frame = 1
    
    for i, path_obj in enumerate(paths):
        # --- PHASE 1: COMBAT (Static at Start) ---
        # Get start point of this path
        # 0 is start, -1 is end usually.
        # But wait, sample_curve gives vertices. 
        points = sample_curve(path_obj)
        if not points:
            continue
            
        start_loc = points[0]
        end_loc = points[-1]
        
        # Keyframe static position
        cam.location = start_loc
        cam.keyframe_insert(data_path="location", frame=current_frame)
        
        # Look rotation? For now, just look forward (towards next point)
        # Or keep previous rotation. let's animate rotation too.
        # Direction to next point (approx)
        if len(points) > 1:
            direction = points[1] - points[0]
            rot = direction.to_track_quat('-Z', 'Y').to_euler()
            cam.rotation_euler = rot
        
        cam.keyframe_insert(data_path="rotation_euler", frame=current_frame)
        
        # Wait
        current_frame += combat_duration
        
        cam.location = start_loc
        cam.keyframe_insert(data_path="location", frame=current_frame)
        cam.keyframe_insert(data_path="rotation_euler", frame=current_frame)
        
        # --- PHASE 2: FLIGHT (Interpolate along curve) ---
        # We have 'flight_duration' frames to traverse 'points'
        num_points = len(points)
        
        for f in range(flight_duration):
            t = f / flight_duration # 0.0 to 1.0
            
            # Map t to an index in 'points'
            idx = int(t * (num_points - 1))
            loc = points[idx]
            
            # Calculate rotation (look ahead)
            next_idx = min(idx + 1, num_points - 1)
            direction = points[next_idx] - loc
            if direction.length < 0.001 and idx > 0:
                direction = loc - points[idx-1] # Use previous if stopped
                
            if direction.length > 0.001:
                target_rot = direction.to_track_quat('-Z', 'Y').to_euler()
                cam.rotation_euler = target_rot
                cam.keyframe_insert(data_path="rotation_euler", frame=current_frame + f)
            
            cam.location = loc
            cam.keyframe_insert(data_path="location", frame=current_frame + f)
            
        current_frame += flight_duration
        
    bpy.context.scene.frame_end = current_frame
    print("Baked animation complete.")

setup_camera_flight_baked()
