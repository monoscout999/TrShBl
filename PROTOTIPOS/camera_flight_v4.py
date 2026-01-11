import bpy
import math
import mathutils

def sample_curve(curve_obj):
    degp = bpy.context.evaluated_depsgraph_get()
    curve_eval = curve_obj.evaluated_get(degp)
    try:
        mesh = curve_eval.to_mesh()
    except:
        return []
    verts = [curve_obj.matrix_world @ v.co for v in mesh.vertices]
    curve_eval.to_mesh_clear()
    return verts

def setup_camera_flight_v6(combat_duration=60, flight_transition=200, flight_internal=100):
    cam = bpy.data.objects.get("Camera")
    if not cam:
        bpy.ops.object.camera_add()
        cam = bpy.context.active_object
        cam.name = "Camera"
        
    cam.animation_data_clear()
    
    # Logic:
    # Sequence is: Arena 0 Internal -> Transition 1 -> Arena 1 Internal -> ...
    # Wait.
    # V6 logic produces:
    # Arena 0: Internal_0 (Entry to Exit) or just Exit? 
    # Arena 0 HAS Internal_0 ONLY IF it has both Entry and Exit.
    # Initial Arena has NO Entry. So it might NOT have Internal path if logic is strict.
    # Let's check objects.
    
    # We need to find ALL path objects and sort them?
    # Naming convention: "Transition_{i}" and "Internal_{i}"
    
    path_sequence = []
    
    # Max arenas assumption
    for i in range(100):
        # We might have Internal_i (Inside Arena i)
        # We might have Transition_i (From i-1 to i)
        
        # Order of traversal:
        # 1. Arrive at Arena i (via Transition i)
        # 2. Combat at Arena i Entry?
        # 3. Fly through Arena i (Internal i)
        # 4. Combat at Arena i Exit?
        
        # Let's look for Transition_i
        trans = bpy.data.objects.get(f"Camera_Path_Transition_{i}")
        if trans:
            path_sequence.append(("TRANSITION", trans))
            
        # Let's look for Internal_i
        internal = bpy.data.objects.get(f"Camera_Path_Internal_{i}")
        if internal:
            path_sequence.append(("INTERNAL", internal))
            
        # Stop condition?
        if not trans and not internal and i > 0:
            # If we miss both for index i, assume end (unless index 0 special case)
            if i > 5 and len(path_sequence) == 0: break # Safety
            
    print(f"Found {len(path_sequence)} flight segments.")
    
    current_frame = 1
    
    for type, path_obj in path_sequence:
        points = sample_curve(path_obj)
        if not points: continue
        
        start_loc = points[0]
        
        # COMBAT / PAUSE Logic
        # If it's an Internal path, we pause BEFORE starting it (at Entry Door)
        # If it's a Transition, we just flow?
        # Or maybe we pause at END of Transition (Arrival)?
        
        is_combat = (type == "INTERNAL")
        
        if is_combat:
            # Static at start of internal path
            cam.location = start_loc
            cam.keyframe_insert(data_path="location", frame=current_frame)
            cam.rotation_euler = (math.radians(90), 0, 0) # Reset
            cam.keyframe_insert(data_path="rotation_euler", frame=current_frame)
            
            current_frame += combat_duration
            
            cam.location = start_loc
            cam.keyframe_insert(data_path="location", frame=current_frame)
            
        # FLIGHT Logic
        dur = flight_internal if type == "INTERNAL" else flight_transition
        
        for f in range(dur):
            t = f / dur
            idx = int(t * (len(points)-1))
            loc = points[idx]
            
            # Simple lookahead
            next_idx = min(idx+2, len(points)-1)
            vec = points[next_idx] - loc
            if vec.length > 0.1:
                rot = vec.to_track_quat('-Z', 'Y').to_euler()
                cam.rotation_euler = rot
                cam.keyframe_insert(data_path="rotation_euler", frame=current_frame + f)
                
            cam.location = loc
            cam.keyframe_insert(data_path="location", frame=current_frame + f)
            
        current_frame += dur
        
    bpy.context.scene.frame_end = current_frame
    print("V6 Flight Baked.")

setup_camera_flight_v6()
