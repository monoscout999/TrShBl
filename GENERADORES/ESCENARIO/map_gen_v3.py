import bpy
import math
import random
import mathutils
from mathutils import Vector

def clear_scene():
    for o in bpy.data.objects:
        bpy.data.objects.remove(o, do_unlink=True)
    for m in bpy.data.meshes:
        bpy.data.meshes.remove(m)
        
def get_cardinal_direction(vec):
    """
    Returns the closest cardinal direction (string) and rotation (radians) for a vector.
    """
    # Normalize
    v = vec.normalized()
    # Check angle against 4 cardinals
    # 0 = North (y+), pi = South (y-)
    # pi/2 = East (x+), -pi/2 = West (x-)
    
    # We use atan2 to get angle: atan2(x, y) if 0 is North? 
    # Standard: atan2(y, x). 
    # If Y+ is North (0 deg):
    angle = math.atan2(v.x, v.y) # Be careful with coords system
    
    # Snap to 90 degrees
    snap = round(angle / (math.pi/2)) * (math.pi/2)
    
    # Identify label
    # North: 0, East: pi/2, South: pi/-pi, West: -pi/2
    deg = math.degrees(snap)
    if abs(deg) < 1: return "NORTH", 0
    if abs(deg - 180) < 1 or abs(deg + 180) < 1: return "SOUTH", math.pi
    if abs(deg - 90) < 1: return "EAST", -math.pi/2 # Wait, rotation for wall object might be different
    if abs(deg + 90) < 1: return "WEST", math.pi/2
    
    return "UNKNOWN", 0

def create_wall_asset(name, location, rotation_z, type="WINDOW", width=40, height=8):
    """
    Creates a detailed wall block.
    Type: "WINDOW" (With hole and spawn), "DOOR" (Big opening for path), "SOLID"
    """
    # Container
    bpy.ops.object.empty_add(location=location)
    container = bpy.context.active_object
    container.name = name
    container.rotation_euler = (0, 0, rotation_z)
    
    mat = bpy.data.materials.get("Mat_Wall_V3")
    if not mat:
        mat = bpy.data.materials.new("Mat_Wall_V3")
        mat.use_nodes = True
        mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.3, 0.3, 0.35, 1.0)

    thick = 2.0
    
    def add_block(px, pz, sx, sz):
        bpy.ops.mesh.primitive_cube_add(size=1)
        blk = bpy.context.active_object
        blk.name = f"{name}_Block"
        blk.data.materials.append(mat)
        blk.scale = (sx, thick, sz)
        blk.parent = container
        blk.location = (px, 0, pz)

    if type == "DOOR":
        # Big opening in center for Path (8m wide)
        door_w = 12.0 
        door_h = 6.0 
        
        # Left Panel
        side_w = (width - door_w)/2
        add_block(-(door_w/2 + side_w/2), height/2, side_w, height)
        # Right Panel
        add_block((door_w/2 + side_w/2), height/2, side_w, height)
        # Top Lintel
        top_h = height - door_h
        if top_h > 0:
            add_block(0, door_h + top_h/2, door_w, top_h)
            
    elif type == "WINDOW":
        # Similar to V2 but for 40m wall maybe multiple windows?
        # Let's do 2 windows per wall for scale
        win_w = 4.0
        win_h = 3.0
        sill = 2.0
        
        # One window at -10, one at +10
        centroids = [-10, 10]
        
        # This is getting complex to build with cubes. 
        # Simplified: Just one big window strip or 2 solid pillars
        # Let's simple: 3 Pillars, 2 Holes.
        # Wall is 40m.
        # Pillar (4m) - Hole (12m) - Pillar (8m) - Hole (12m) - Pillar (4m) -> Total 40
        
        # Pillar 1 (Left)
        add_block(-18, height/2, 4, height)
        # Pillar 2 (Center)
        add_block(0, height/2, 4, height)
        # Pillar 3 (Right)
        add_block(18, height/2, 4, height)
        
        # Headers/Footers for windows
        add_block(-9, sill/2, 14, sill) # Sill L
        add_block(9, sill/2, 14, sill)  # Sill R
        add_block(-9, 7.0, 14, 2)       # Top L
        add_block(9, 7.0, 14, 2)        # Top R
        
        # Spawn Points
        # Create spawns behind these windows
        spawn_locs = [-9, 9]
        for i, x_off in enumerate(spawn_locs):
             # Local pos
             sp_local = Vector((x_off, 4.0, 2.0)) # 4m behind
             # Global
             mat_rot = mathutils.Matrix.Rotation(rotation_z, 4, 'Z')
             sp_global = location + (mat_rot @ sp_local)
             
             bpy.ops.object.empty_add(type='SPHERE', location=sp_global)
             sp = bpy.context.active_object
             sp.name = f"{name}_Spawn_{i}"

    return container

def create_arena_v3(index, location, entry_vec=None, exit_vec=None):
    size = 80.0 # V3 Size Updated (Double again)
    room_name = f"Arena_{index}"
    
    # Floor
    bpy.ops.mesh.primitive_plane_add(size=size, location=location)
    floor = bpy.context.active_object
    floor.name = f"{room_name}_Floor"
    
    # Material
    mat = bpy.data.materials.get("Mat_Floor")
    if mat: floor.data.materials.append(mat)
    
    # Determine Cardinality of Doors
    doors = set()
    if entry_vec:
        card, _ = get_cardinal_direction(entry_vec)
        # Entry logic: if we moved East (1,0), we hit the West wall.
        if card == "EAST": doors.add("WEST")
        if card == "WEST": doors.add("EAST")
        if card == "NORTH": doors.add("SOUTH")
        if card == "SOUTH": doors.add("NORTH")
        
    if exit_vec:
        # Exit logic: if we leave East, we use East wall.
        card, _ = get_cardinal_direction(exit_vec)
        doors.add(card) 
        
    print(f"Arena {index} Doors: {doors}")

    # Wall Definitions
    half = size/2
    walls = {
        "NORTH": (Vector((0, half, 0)), 0),
        "SOUTH": (Vector((0, -half, 0)), math.pi),
        "EAST": (Vector((half, 0, 0)), math.pi/2),
        "WEST": (Vector((-half, 0, 0)), -math.pi/2),
    }
    
    for direction, (offset, rot) in walls.items():
        w_type = "DOOR" if direction in doors else "WINDOW"
        # We need to scale the wall assets too? The function creates bits based on 'width' param.
        create_wall_asset(f"{room_name}_{direction}", location+offset, rot, type=w_type, width=size)

    # Player Point
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location + Vector((0, 0, 2)))
    bpy.context.active_object.name = f"Player_Point_{index}"
    
    return bpy.context.active_object

def create_road_profile():
    if bpy.data.objects.get("Road_Profile_V3"): return bpy.data.objects.get("Road_Profile_V3")
    curveData = bpy.data.curves.new('Road_Profile_V3', type='CURVE')
    curveData.dimensions = '2D'
    curveObj = bpy.data.objects.new('Road_Profile_V3', curveData)
    bpy.context.collection.objects.link(curveObj)
    
    # Simple Flat Ribbon (No thickness)
    spline = curveData.splines.new('POLY')
    spline.points.add(1) # Total 2
    width = 12.0 # Slightly wider path
    spline.points[0].co = (-width/2, 0, 0, 1)
    spline.points[1].co = (width/2, 0, 0, 1)
    
    return curveObj

def create_paths_v3(index, start_loc, end_loc):
    # 1. Camera Path (Invisible, Smooth loop)
    # We want the camera to fly nicely, maybe loop up a bit?
    cam_curve_data = bpy.data.curves.new(f'Camera_Path_{index}', type='CURVE')
    cam_curve_data.dimensions = '3D'
    cam_curve_obj = bpy.data.objects.new(f'Camera_Path_{index}', cam_curve_data)
    bpy.context.collection.objects.link(cam_curve_obj)
    
    dist = (end_loc - start_loc).length
    direction = (end_loc - start_loc).normalized()
    side = Vector((-direction.y, direction.x, 0))
    
    spline = cam_curve_data.splines.new('BEZIER')
    spline.bezier_points.add(1)
    
    # Camera Curve Handles (Curved in Z for flight feel)
    # Start
    bp0 = spline.bezier_points[0]
    bp0.co = start_loc
    bp0.handle_left = start_loc - direction*30
    bp0.handle_right = start_loc + direction*30 + Vector((0,0,10)) # Fly up
    
    # End
    bp1 = spline.bezier_points[1]
    bp1.co = end_loc
    bp1.handle_left = end_loc - direction*30 + Vector((0,0,10)) # Land down
    bp1.handle_right = end_loc + direction*30
    
    # 2. Visual Path (Visible, FLAT Road)
    vis_curve_data = bpy.data.curves.new(f'Visual_Path_{index}', type='CURVE')
    vis_curve_data.dimensions = '3D'
    vis_curve_data.resolution_u = 24
    vis_curve_data.bevel_mode = 'OBJECT'
    vis_curve_data.bevel_object = create_road_profile()
    vis_curve_data.use_fill_caps = False # Ribbon doesn't need caps
    
    vis_obj = bpy.data.objects.new(f'Visual_Path_{index}', vis_curve_data)
    bpy.context.collection.objects.link(vis_obj)
    
    v_spline = vis_curve_data.splines.new('BEZIER')
    v_spline.bezier_points.add(1)
    
    # FLAT GEOMETRY for visual path (No Z variation manually added to handles)
    # But we want some XY curvature so it's not a straight line?
    # User said "camino", usually implies straight connection if floor. 
    # But logic used bezier handles. To make it FLAT, we just ensure handles have Z=0 relative to point.
    
    # Mid-point jitter for curve (XY Only)
    mid_dist = dist / 2
    curve_offset = side * random.uniform(-15, 15)
    
    # We can't insert a point easily in 2-point bezier without subdividing.
    # So we just curve the handles sideways.
    
    # Start Point
    v_spline.bezier_points[0].co = start_loc
    v_spline.bezier_points[0].handle_left = start_loc - direction*20
    v_spline.bezier_points[0].handle_right = start_loc + direction*20 + curve_offset # Curve out
    
    # End Point
    v_spline.bezier_points[1].co = end_loc
    v_spline.bezier_points[1].handle_left = end_loc - direction*20 + curve_offset # Curve in
    v_spline.bezier_points[1].handle_right = end_loc + direction*20
    
    # Material
    mat = bpy.data.materials.get("Mat_Floor")
    if mat: vis_curve_data.materials.append(mat)
    
    return cam_curve_obj

def generate_map_v3(num_arenas=4):
    clear_scene()
    print("Generating Map V3 (Decoupled Paths + Logic)...")
    
    # Calculate all positions FIRST so we know Exits
    positions = [Vector((0,0,0))]
    current = Vector((0,0,0))
    heading = 0
    
    for i in range(num_arenas-1):
        turn = random.choice([-90, 0, 90]) # Snap turns? Or keep random?
        turn = random.uniform(-40, 40)
        heading += turn
        rad = math.radians(heading)
        dist = 120.0
        step = Vector((math.sin(rad)*dist, math.cos(rad)*dist, 0))
        current += step
        positions.append(current.copy())
        
    prev_player = None
    
    for i in range(num_arenas):
        pos = positions[i]
        
        # Determine Entry Vector (Current - Prev)
        entry_vec = (pos - positions[i-1]) if i > 0 else None
        
        # Determine Exit Vector (Next - Current)
        exit_vec = (positions[i+1] - pos) if i < (num_arenas-1) else None
        
        p_point = create_arena_v3(i, pos, entry_vec, exit_vec)
        
        if prev_player:
            create_paths_v3(i, prev_player.location, p_point.location)
            
        prev_player = p_point
        
    print("V3 Complete.")

generate_map_v3()
