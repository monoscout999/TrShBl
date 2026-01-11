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
    v = vec.normalized()
    angle = math.atan2(v.x, v.y) 
    snap = round(angle / (math.pi/2)) * (math.pi/2)
    deg = math.degrees(snap)
    if abs(deg) < 1: return "NORTH", 0
    if abs(deg - 180) < 1 or abs(deg + 180) < 1: return "SOUTH", math.pi
    if abs(deg - 90) < 1: return "EAST", -math.pi/2 
    if abs(deg + 90) < 1: return "WEST", math.pi/2
    return "UNKNOWN", 0

def create_wall_asset(name, location, rotation_z, type="WINDOW", width=80, height=6):
    """
    Creates a detailed wall block for a SINGLE STORY.
    Height reduced to 6m per floor for better stacking.
    """
    bpy.ops.object.empty_add(location=location)
    container = bpy.context.active_object
    container.name = name
    container.rotation_euler = (0, 0, rotation_z)
    
    mat = bpy.data.materials.get("Mat_Wall_V4")
    if not mat:
        mat = bpy.data.materials.new("Mat_Wall_V4")
        mat.use_nodes = True
        mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.35, 0.35, 0.4, 1.0)
    
    thick = 2.0
    
    def add_block(px, pz, sx, sz, relative=True):
        bpy.ops.mesh.primitive_cube_add(size=1)
        blk = bpy.context.active_object
        blk.name = f"{name}_Block"
        blk.data.materials.append(mat)
        blk.scale = (sx, thick, sz)
        blk.parent = container
        if relative:
            blk.location = (px, 0, pz)
        else:
            # If absolute world coords needed (not used here)
            pass

    if type == "DOOR":
        # Ground floor door: Large opening
        door_w = 14.0 
        door_h = 5.0 
        
        # Left/Right Panels
        side_w = (width - door_w)/2
        add_block(-(door_w/2 + side_w/2), height/2, side_w, height)
        add_block((door_w/2 + side_w/2), height/2, side_w, height)
        # Lintel
        top_h = height - door_h
        if top_h > 0:
            add_block(0, door_h + top_h/2, door_w, top_h)
            
    elif type == "WINDOW" or type == "UPPER_FLOOR": 
        # For upper floors, even "doors" become windows (or balconies)
        # Pattern: Solid - Window - Solid - Window - Solid
        container_w = width
        
        # 3 Windows of 8m width
        win_w = 8.0
        win_h = 3.0
        sill = 1.5
        
        # Positions: -20, 0, 20
        win_centers = [-25, 0, 25]
        
        # We construct by "Pillars" between windows
        # Wall start: -40. Wall end: 40.
        # Windows: [-29, -21], [-4, 4], [21, 29]
        
        # Simplified block logic:
        # Just create the "Sill" (Bottom), "Header" (Top), and "Pillars" (Between)
        
        # Full width Sill strip
        add_block(0, sill/2, width, sill)
        
        # Full width Header strip
        header_base = sill + win_h
        header_h = height - header_base
        add_block(0, header_base + header_h/2, width, header_h)
        
        # Pillars
        # We need pillars to fill gaps not covered by windows
        # Gaps: (-40 to -29), (-21 to -4), (4 to 21), (29 to 40)
        pillars = [
            (-34.5, 11), # Center, Width
            (-12.5, 17),
            (12.5, 17),
            (34.5, 11)
        ]
        
        for px, pw in pillars:
            add_block(px, sill + win_h/2, pw, win_h)
            
        # Spawns at Windows
        for i, wx in enumerate(win_centers):
            # Spawn 2m behind window
            sp_local = Vector((wx, 3.0, sill + 1.0))
            mat_rot = mathutils.Matrix.Rotation(rotation_z, 4, 'Z')
            sp_global = location + (mat_rot @ sp_local)
            
            bpy.ops.object.empty_add(type='SPHERE', location=sp_global)
            sp = bpy.context.active_object
            sp.parent = container # Parent spawn to wall container
            sp.name = f"{name}_Spawn_{i}"

    return container

def create_arena_v4(index, location, entry_vec=None, exit_vec=None):
    size = 80.0
    room_name = f"Arena_{index}"
    
    # 1. Floor
    bpy.ops.mesh.primitive_plane_add(size=size, location=location)
    floor = bpy.context.active_object
    floor.name = f"{room_name}_Floor"
    mat = bpy.data.materials.get("Mat_Floor")
    if mat: floor.data.materials.append(mat)
    
    # 2. Player Point
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location + Vector((0, 0, 2)))
    bpy.context.active_object.name = f"Player_Point_{index}"
    
    # 3. Determine Cardinal Doors
    doors = set()
    if entry_vec:
        card, _ = get_cardinal_direction(entry_vec)
        if card == "EAST": doors.add("WEST")
        if card == "WEST": doors.add("EAST")
        if card == "NORTH": doors.add("SOUTH")
        if card == "SOUTH": doors.add("NORTH")
    if exit_vec:
        card, _ = get_cardinal_direction(exit_vec)
        doors.add(card)
        
    print(f"Arena {index} Doors: {doors}")

    # Wall Definitions
    half = size/2
    wall_map = {
        "NORTH": (Vector((0, half, 0)), 0),
        "SOUTH": (Vector((0, -half, 0)), math.pi),
        "EAST": (Vector((half, 0, 0)), math.pi/2),
        "WEST": (Vector((-half, 0, 0)), -math.pi/2),
    }

    # 4. Multi-Story Logic
    # Random stories 1 to 3
    num_floors = random.randint(1, 3)
    floor_height = 6.0
    
    for f in range(num_floors):
        z_offset = f * floor_height
        is_ground = (f == 0)
        
        for direction, (offset, rot) in wall_map.items():
            # Wall Type
            w_type = "WINDOW" # Default
            
            if is_ground and direction in doors:
                w_type = "DOOR"
            elif not is_ground:
                w_type = "UPPER_FLOOR" # Treated same as window for now, but maybe balconies later?
            
            w_loc = location + offset + Vector((0, 0, z_offset))
            create_wall_asset(f"{room_name}_F{f}_{direction}", w_loc, rot, type=w_type, width=size, height=floor_height)
            
    # Add Roof?
    # Maybe just open top for now, or a simple cap on top floor?
    # Let's leave it open for skybox view.
            
    return bpy.context.active_object

def create_road_profile_flat():
    if bpy.data.objects.get("Road_Profile_Flat"): return bpy.data.objects.get("Road_Profile_Flat")
    curveData = bpy.data.curves.new('Road_Profile_Flat', type='CURVE')
    curveData.dimensions = '2D'
    curveObj = bpy.data.objects.new('Road_Profile_Flat', curveData)
    bpy.context.collection.objects.link(curveObj)
    
    spline = curveData.splines.new('POLY')
    spline.points.add(1) 
    width = 12.0
    spline.points[0].co = (-width/2, 0, 0, 1)
    spline.points[1].co = (width/2, 0, 0, 1)
    
    return curveObj

def create_paths_v4(index, start_loc, end_loc):
    # 1. Camera Path (Invisible)
    cam_curve_data = bpy.data.curves.new(f'Camera_Path_{index}', type='CURVE')
    cam_curve_data.dimensions = '3D'
    cam_curve_obj = bpy.data.objects.new(f'Camera_Path_{index}', cam_curve_data)
    bpy.context.collection.objects.link(cam_curve_obj)
    
    dist = (end_loc - start_loc).length
    direction = (end_loc - start_loc).normalized()
    side = Vector((-direction.y, direction.x, 0))
    
    mid = (start_loc + end_loc) / 2
    
    spline = cam_curve_data.splines.new('BEZIER')
    spline.bezier_points.add(1)
    
    # Camera flies slightly high for good view
    bp0 = spline.bezier_points[0]
    bp0.co = start_loc
    bp0.handle_left = start_loc - direction*30
    bp0.handle_right = start_loc + direction*30 + Vector((0,0,15)) 
    
    bp1 = spline.bezier_points[1]
    bp1.co = end_loc
    bp1.handle_left = end_loc - direction*30 + Vector((0,0,15))
    bp1.handle_right = end_loc + direction*30
    
    # 2. Visual Path (Visible, FLAT Road)
    vis_curve_data = bpy.data.curves.new(f'Visual_Path_{index}', type='CURVE')
    vis_curve_data.dimensions = '3D'
    vis_curve_data.resolution_u = 24
    vis_curve_data.bevel_mode = 'OBJECT'
    vis_curve_data.bevel_object = create_road_profile_flat()
    vis_curve_data.use_fill_caps = False
    
    vis_obj = bpy.data.objects.new(f'Visual_Path_{index}', vis_curve_data)
    bpy.context.collection.objects.link(vis_obj)
    
    v_spline = vis_curve_data.splines.new('BEZIER')
    v_spline.bezier_points.add(1)
    
    # Fix Height: Ensure it stays on Z=0 (Assuming arenas are at Z=0 relative)
    # Actually arenas can change height.
    # We must ensure the curve points match the floor location Z exactly.
    
    # Curve handles might introduce dip if they point down.
    # We want handles to be parallel to XY plane if path is flat, or linear slope.
    
    v_spline.bezier_points[0].co = start_loc
    # Handle control: Linear direction in Z, Curved in XY
    
    curve_offset = side * random.uniform(-20, 20)
    
    v_spline.bezier_points[0].handle_left = start_loc - direction*25
    v_spline.bezier_points[0].handle_right = start_loc + direction*25 + curve_offset
    
    v_spline.bezier_points[1].co = end_loc
    v_spline.bezier_points[1].handle_left = end_loc - direction*25 + curve_offset
    v_spline.bezier_points[1].handle_right = end_loc + direction*25
    
    # IMPORTANT: Flatten handles Z to match slope correctly?
    # Simple way: just let it spline naturally between Z_start and Z_end.
    # But ensure handles Z component is consistent with slope. 
    # For now, just keeping handles Z=0 relative to point (using vector addition) ensures smoothness.
    
    mat = bpy.data.materials.get("Mat_Floor")
    if mat: vis_curve_data.materials.append(mat)
    
    return cam_curve_obj

def generate_map_v4(num_arenas=4):
    clear_scene()
    print("Generating Map V4 (Multi-Story + Fixes)...")
    
    positions = [Vector((0,0,0))]
    current = Vector((0,0,0))
    heading = 0
    
    for i in range(num_arenas-1):
        turn = random.uniform(-50, 50)
        heading += turn
        rad = math.radians(heading)
        dist = 140.0 # Longer paths for bigger arenas
        
        # Add some Z variation for ramps? Or keep flat?
        # User complained about "floating tubes". Keeping Z=0 is safer for "on floor" look initially.
        z_change = 0 # random.uniform(-5, 5) 
        
        step = Vector((math.sin(rad)*dist, math.cos(rad)*dist, z_change))
        current += step
        positions.append(current.copy())
        
    prev_player = None
    
    for i in range(num_arenas):
        pos = positions[i]
        entry = (pos - positions[i-1]) if i > 0 else None
        exit = (positions[i+1] - pos) if i < (num_arenas-1) else None # Fix logic: exit is to next
        
        p_point = create_arena_v4(i, pos, entry, exit)
        
        if prev_player:
            create_paths_v4(i, prev_player.location, p_point.location)
            
        prev_player = p_point
        
    print("V4 Complete.")

generate_map_v4()
