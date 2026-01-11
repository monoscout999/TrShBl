import bpy
import math

def setup_camera_flight_v5(speed=15.0): # m/s (approx)
    # Target Path
    path = bpy.data.objects.get("Camera_Path_Master")
    if not path:
        print("No master path found.")
        return
        
    cam = bpy.data.objects.get("Camera")
    if not cam:
        bpy.ops.object.camera_add()
        cam = bpy.context.active_object
        cam.name = "Camera"
        
    cam.animation_data_clear()
    
    # 1. Reset Transform to Origin (Crucial for Follow Path)
    cam.location = (0,0,0)
    cam.rotation_euler = (0,0,0) # Or specific facing?
    # Usually Follow Path + Follow Curve handles rotation.
    
    # Calculate Length for automatic speed
    # A crude length check
    pts = path.data.splines[0].bezier_points
    total_len = 0
    for i in range(len(pts)-1):
        total_len += (pts[i+1].co - pts[i].co).length
        
    # Frames needed
    # speed = 20m/s?
    total_frames = int((total_len / speed) * 30) # 30fps
    print(f"Path Length: {total_len:.1f}m. Frames: {total_frames}")
    
    # Constraint Method (Easiest for single path)
    # Remove old constraints
    for c in cam.constraints: cam.constraints.remove(c)
    
    c = cam.constraints.new('FOLLOW_PATH')
    c.target = path
    c.use_curve_follow = True
    c.forward_axis = 'TRACK_NEGATIVE_Z' # Camera -Z looks forward
    c.up_axis = 'UP_Y' # Camera Y is Up
    
    # Animate Evaluation Time
    path.data.path_duration = total_frames
    
    # Keyframes on Curve (Evaluation Time)
    # Actually curve data calc is tricky.
    # Easier: Use 'Fixed Position' constraint
    c.use_fixed_location = True
    
    c.offset_factor = 0.0
    c.keyframe_insert(data_path="offset_factor", frame=1)
    
    c.offset_factor = 1.0
    c.keyframe_insert(data_path="offset_factor", frame=total_frames)
    
    # Add some noise/shake?
    # Modifiers on F-curve later.
    
    bpy.context.scene.frame_end = total_frames
    print("V5 Flight (Master Spline) Ready.")

setup_camera_flight_v5()
