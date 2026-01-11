import bpy
import math
import random
import json
import os
import mathutils
from mathutils import Vector

CONFIG_PATH = r"C:\Trailshoot\GENERADORES\ESCENARIO\CONFIG\map_styles.json"

def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r') as f:
                return json.load(f).get("styles", {})
        except: pass
    return {} # Fallback handled by having defaults if needed, but assuming file exists

STYLES = load_config()
ACTIVE_STYLE = STYLES.get("standard", {})

def clear_scene():
    for o in bpy.data.objects:
        bpy.data.objects.remove(o, do_unlink=True)
    for m in bpy.data.meshes:
        bpy.data.meshes.remove(m)

# --- GEOMETRY HELPERS (Constructive Method) ---
def create_block(parent, name, mat, px, pz, sx, sz, rotation_z=0):
    bpy.ops.mesh.primitive_cube_add(size=1)
    blk = bpy.context.active_object
    blk.name = name
    if mat: blk.data.materials.append(mat)
    blk.scale = (sx, ACTIVE_STYLE.get("wall_thickness", 2.0), sz)
    blk.parent = parent
    blk.location = (px, 0, pz)
    blk.rotation_euler.z = rotation_z

def create_wall_segment(container, name, mat, width, height, asset_type):
    asset = ACTIVE_STYLE["assets"].get(asset_type, {})
    if asset.get("type", "WALL") == "WALL":
        create_block(container, f"{name}_Solid", mat, 0, height/2, width, height)
        return

    a_w = asset.get("width", 4.0)
    a_h = asset.get("height", 2.0)
    sill = asset.get("sill", 0.0)
    
    # Constructive Geometry: Build around hole
    # 1. Sill
    if sill > 0:
        create_block(container, f"{name}_Sill", mat, 0, sill/2, width, sill)
    # 2. Header
    top_y = sill + a_h
    top_h = height - top_y
    if top_h > 0:
        create_block(container, f"{name}_Header", mat, 0, top_y + top_h/2, width, top_h)
    # 3. Sides
    side_w = (width - a_w) / 2
    mid_y = sill + a_h/2
    center_offset = (a_w/2) + (side_w/2)
    create_block(container, f"{name}_L", mat, -center_offset, mid_y, side_w, a_h)
    create_block(container, f"{name}_R", mat, center_offset, mid_y, side_w, a_h)
    
    # Spawn
    if asset.get("type") == "WINDOW":
        spawn_loc = Vector((0, 3.0, sill + a_h/2))
        bpy.ops.object.empty_add(type='SPHERE', location=(0,0,0))
        sp = bpy.context.active_object
        sp.name = f"{name}_Spawn"
        sp.parent = container
        sp.location = spawn_loc
        sp.scale = (0.5, 0.5, 0.5)

# --- V6 GENERATOR LOGIC ---

def generate_wall_composition(length, mandatory_asset=None):
    """
    Returns a list of (AssetType, PositionX) based on probabilities.
    """
    segments = []
    
    # 1. Place Mandatory Asset (e.g. Exit Door)
    # Strategy: Place randomly in valid range, or center for now?
    # User said: "Exit Door... pick randomly from furthest wall".
    # Here we assume we are generating THAT wall.
    
    occupied_ranges = [] # List of (min_x, max_x)
    
    if mandatory_asset:
        m_data = ACTIVE_STYLE["assets"][mandatory_asset]
        m_w = m_data.get("width", 10.0)
        # Place roughly in center to ensure it fits, or jitter slightly
        m_pos = random.uniform(-(length/4), (length/4)) 
        segments.append((mandatory_asset, m_pos))
        occupied_ranges.append((m_pos - m_w/2, m_pos + m_w/2))
        
    # 2. Fill Rest Probabilistically
    avail_assets = [k for k,v in ACTIVE_STYLE["assets"].items() if k != "SOLID" and v.get("chance", 0) > 0]
    
    # Attempt to place N random assets
    attempts = 10 
    
    for _ in range(attempts):
        choice = random.choice(avail_assets)
        data = ACTIVE_STYLE["assets"][choice]
        chance = data.get("chance", 0.5)
        
        if random.random() > chance: continue
        
        w = data.get("width", 5.0)
        
        # Random position in wall
        # Wall spans -length/2 to length/2
        # Margin of safety
        pos = random.uniform(-(length/2)+w, (length/2)-w)
        
        # Collision Check
        min_x = pos - w/2
        max_x = pos + w/2
        collision = False
        for (o_min, o_max) in occupied_ranges:
            if not (max_x < o_min or min_x > o_max):
                collision = True
                break
        
        if not collision:
            segments.append((choice, pos))
            occupied_ranges.append((min_x, max_x))
            
    # Sort
    segments.sort(key=lambda x: x[1])
    
    # Fill Gaps with Solid?
    # Actually, Constructive Geometry creates the wall segment FOR the asset.
    # If we just place instances floating, we have holes between them.
    # The 'create_wall_segment' assumes it OWNS the 'width'.
    # So we need to calculate the GAP between assets and put SOLID walls there.
    
    final_composition = []
    current_x = -length/2
    
    for asset, pos in segments:
        data = ACTIVE_STYLE["assets"][asset]
        w = data.get("width", 10.0)
        start_asset = pos - w/2
        
        # Gap before?
        gap = start_asset - current_x
        if gap > 1.0:
            final_composition.append(("SOLID", current_x + gap/2, gap))
            
        final_composition.append((asset, pos, w))
        current_x = start_asset + w
        
    # Gap after last?
    remaining = (length/2) - current_x
    if remaining > 1.0:
         final_composition.append(("SOLID", current_x + remaining/2, remaining))
         
    return final_composition

def build_wall_v6(name, location, rotation_z, length, height, mandatory_asset=None):
    bpy.ops.object.empty_add(location=location)
    container = bpy.context.active_object
    container.name = name
    container.rotation_euler = (0, 0, rotation_z)
    
    mat = bpy.data.materials.get("Mat_Wall_V5")
    if not mat:
        mat = bpy.data.materials.new("Mat_Wall_V5")
        mat.use_nodes = True
        
    composition = generate_wall_composition(length, mandatory_asset)
    
    for i, (atype, pos_x, width) in enumerate(composition):
        bpy.ops.object.empty_add(location=(0,0,0))
        seg = bpy.context.active_object
        seg.name = f"{name}_{i}_{atype}"
        seg.parent = container
        seg.location = (pos_x, 0, 0)
        
        create_wall_segment(seg, seg.name, mat, width, height, atype)
        
    return container

def create_arena_v6(index, location, entry_vec, exit_vec):
    size = 80.0
    room_name = f"Arena_{index}"
    
    # Determine Doors
    # 1. Entry Door (Where player arrives)
    entry_dir = "NONE"
    if entry_vec:
        # Determine strict cardinal
        v = entry_vec.normalized()
        angle = math.atan2(v.x, v.y)
        snap = round(angle / (math.pi/2)) * (math.pi/2)
        deg = math.degrees(snap)
        if abs(deg) < 1: entry_dir = "SOUTH" # Arriving from South (Vector North) -> South Wall?
        # Logic check: If vector is (0, 1) [North], we arrive at the SOUTH side of the new arena.
        # Yes: Entry Door is on SOUTH wall.
        elif abs(deg - 180) < 1 or abs(deg+180) < 1: entry_dir = "NORTH"
        elif abs(deg - 90) < 1: entry_dir = "WEST"
        elif abs(deg + 90) < 1: entry_dir = "EAST"
        
    # 2. Exit Door (Where player leaves)
    exit_dir = "NONE"
    if exit_vec:
        v = exit_vec.normalized()
        angle = math.atan2(v.x, v.y)
        snap = round(angle / (math.pi/2)) * (math.pi/2)
        deg = math.degrees(snap)
        # Leaving North (0, 1) -> Exit Door is on NORTH wall.
        if abs(deg) < 1: exit_dir = "NORTH"
        elif abs(deg - 180) < 1 or abs(deg+180) < 1: exit_dir = "SOUTH"
        elif abs(deg - 90) < 1: exit_dir = "EAST"
        elif abs(deg + 90) < 1: exit_dir = "WEST"
        
    print(f"Arena {index}: Entry={entry_dir}, Exit={exit_dir}")

    # Build Logic
    bpy.ops.mesh.primitive_plane_add(size=size, location=location)
    floor = bpy.context.active_object
    floor.name = f"{room_name}_Floor"
    mat = bpy.data.materials.get("Mat_Floor")
    if mat: floor.data.materials.append(mat)
    
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location + Vector((0, 0, 2)))
    p_point = bpy.context.active_object
    p_point.name = f"Player_Point_{index}"

    walls_def = {
        "NORTH": (Vector((0, size/2, 0)), 0),
        "SOUTH": (Vector((0, -size/2, 0)), math.pi),
        "EAST": (Vector((size/2, 0, 0)), math.pi/2),
        "WEST": (Vector((-size/2, 0, 0)), -math.pi/2),
    }

    num_floors = random.randint(1, 4)
    f_height = ACTIVE_STYLE.get("floor_height", 6.0)
    
    # Store door locations for paths!
    door_locations = {"ENTRY": None, "EXIT": None}

    for f in range(num_floors):
        z = f * f_height
        is_ground = (f == 0)
        
        for aspect, (offset, rot) in walls_def.items():
            mandatory = None
            if is_ground:
                if aspect == entry_dir: 
                    mandatory = "GATE" # Entry Gate
                    door_locations["ENTRY"] = location + offset
                elif aspect == exit_dir: 
                    mandatory = "GATE" # Exit Gate
                    door_locations["EXIT"] = location + offset
            
            w_loc = location + offset + Vector((0,0,z))
            build_wall_v6(f"{room_name}_F{f}_{aspect}", w_loc, rot, size, f_height, mandatory)
            
    return p_point, door_locations

# --- PATH LOGIC ---
def create_road_profile():
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

def create_complex_path(index, start_loc, end_loc, type="TRANSITION", complexity=1.0):
    """
    type: 'INTERNAL' (Straightish), 'TRANSITION' (Crazy)
    complexity: 0.0 to 2.0 (Amount of wrapping)
    """
    
    # Curves
    c_data = bpy.data.curves.new(f'Camera_Path_{index}', 'CURVE')
    c_data.dimensions = '3D'
    c_obj = bpy.data.objects.new(f'Camera_Path_{index}', c_data)
    bpy.context.collection.objects.link(c_obj)
    
    v_data = bpy.data.curves.new(f'Visual_Path_{index}', 'CURVE')
    v_data.dimensions = '3D'
    v_data.bevel_object = create_road_profile()
    v_data.use_fill_caps = False
    v_obj = bpy.data.objects.new(f'Visual_Path_{index}', v_data)
    bpy.context.collection.objects.link(v_obj)
    mat = bpy.data.materials.get("Mat_Floor")
    if mat: v_data.materials.append(mat)
    
    spline = c_data.splines.new('BEZIER')
    v_spline = v_data.splines.new('BEZIER')
    
    # Points Logic
    # We always need Start and End.
    # If complexity > 0, we add intermediate points.
    
    points = [start_loc]
    
    direction = (end_loc - start_loc).normalized()
    distance = (end_loc - start_loc).length
    side = Vector((-direction.y, direction.x, 0))
    
    if type == "TRANSITION" and complexity > 0:
        # Create 2 intermediate control points that spiral?
        # Simple S-Curve: push mid point out
        mid = (start_loc + end_loc) / 2
        offset = side * (30.0 * complexity) * random.choice([1, -1])
        
        # Point A (1/3)
        p1 = start_loc + (direction * (distance*0.33)) + offset
        # Point B (2/3)
        p2 = start_loc + (direction * (distance*0.66)) - offset # Zig Zag
        
        points.append(p1)
        points.append(p2)
        
    points.append(end_loc)
    
    spline.bezier_points.add(len(points)-1)
    v_spline.bezier_points.add(len(points)-1)
    
    for i, p in enumerate(points):
        # Assign Coords
        # Camera is higher?
        cam_p = p + Vector((0,0, 10)) if i in [1, len(points)-2] else p # Fly high in middle
        
        # Auto Handles
        bp = spline.bezier_points[i]
        bp.co = cam_p
        bp.handle_left_type = 'AUTO'
        bp.handle_right_type = 'AUTO'
        
        vp = v_spline.bezier_points[i]
        vp.co = p
        vp.handle_left_type = 'AUTO'
        vp.handle_right_type = 'AUTO'

    return c_obj

def generate_map_v6(num_arenas=4):
    clear_scene()
    print("Generating Map V6 (Probabilistic)...")
    
    # 1. Calculate Spine
    positions = [Vector((0,0,0))]
    curr = Vector((0,0,0))
    heading = 0
    for _ in range(num_arenas-1):
        heading += random.uniform(-60, 60)
        rad = math.radians(heading)
        dist = 200.0 # Far away to allow crazy paths
        curr += Vector((math.sin(rad)*dist, math.cos(rad)*dist, 0))
        positions.append(curr.copy())
        
    # 2. Build
    prev_door_exit = None # The exact location of previous exit door
    
    for i in range(num_arenas):
        pos = positions[i]
        
        # Calc Vectors for Door Logic
        entry_vec = (pos - positions[i-1]) if i > 0 else None
        exit_vec = (positions[i+1] - pos) if i < (num_arenas-1) else None
        
        # Create Arena
        p_point, doors = create_arena_v6(i, pos, entry_vec, exit_vec)
        
        current_entry = doors["ENTRY"]
        current_exit = doors["EXIT"]
        
        # 3. Create Paths
        # A. Transition Path (Prev Exit -> Curr Entry)
        if prev_door_exit and current_entry:
            # Transition Logic: Sinuous
            create_complex_path(f"Transition_{i}", prev_door_exit, current_entry, "TRANSITION", complexity=1.5)
            
        # B. Internal Path (Curr Entry -> Curr Exit)
        if current_entry and current_exit:
            # Internal Logic: Straightish
            create_complex_path(f"Internal_{i}", current_entry, current_exit, "INTERNAL", complexity=0.0)
            
        prev_door_exit = current_exit
        
    print("V6 Complete.")

generate_map_v6()
