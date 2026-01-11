import bpy
import math
import random
import json
import os
import mathutils
from mathutils import Vector

CONFIG_PATH_STYLES = r"C:\Trailshoot\GENERADORES\ESCENARIO\CONFIG\map_styles.json"
CONFIG_PATH_ARENAS = r"C:\Trailshoot\GENERADORES\ESCENARIO\CONFIG\arena_configs.json"

def load_json(path):
    if os.path.exists(path):
        try:
            with open(path, 'r') as f: return json.load(f)
        except: pass
    return {}

STYLES_DATA = load_json(CONFIG_PATH_STYLES)
ARENAS_DATA = load_json(CONFIG_PATH_ARENAS)

GLOBAL_STYLE = STYLES_DATA.get("styles", {}).get("standard", {})
ARENA_TYPES = ARENAS_DATA.get("arena_types", {})

def clear_scene():
    for o in bpy.data.objects:
        bpy.data.objects.remove(o, do_unlink=True)
    for m in bpy.data.meshes:
        bpy.data.meshes.remove(m)

# --- HELPER: Merge Configs for Specific Arena ---
def get_arena_config(type_id):
    defaults = GLOBAL_STYLE.copy()
    defaults["assets"] = defaults["assets"].copy() # Shallow copy assets dict
    
    specific = ARENA_TYPES.get(str(type_id), {})
    
    # Override simple keys
    if "wall_height" in specific: defaults["floor_height"] = specific["wall_height"] # Map key?
    if "floors_min" in specific: defaults["floors_min"] = specific["floors_min"]
    if "floors_max" in specific: defaults["floors_max"] = specific["floors_max"]
    
    # Override Asset params (chance/max_count) using Deep Merge logic
    overrides = specific.get("asset_overrides", {})
    for asset_k, asset_v in overrides.items():
        if asset_k in defaults["assets"]:
            # Update existing
            for k, v in asset_v.items():
                defaults["assets"][asset_k][k] = v
                
    return defaults

# --- GEOMETRY HELPERS ---
def create_block(parent, name, mat, px, pz, sx, sz, rotation_z=0):
    bpy.ops.mesh.primitive_cube_add(size=1)
    blk = bpy.context.active_object
    blk.name = name
    if mat: blk.data.materials.append(mat)
    blk.scale = (sx, 2.0, sz) # FORCE 2.0 thickness for now
    blk.parent = parent
    blk.location = (px, 0, pz)
    blk.rotation_euler.z = rotation_z

def create_wall_segment(container, name, mat, width, height, asset_type, config):
    asset = config["assets"].get(asset_type, {})
    if asset.get("type", "WALL") == "WALL":
        create_block(container, f"{name}_Solid", mat, 0, height/2, width, height)
        return

    a_w = asset.get("width", 4.0)
    a_h = asset.get("height", 2.0)
    sill = asset.get("sill", 0.0)
    
    if sill > 0: create_block(container, f"{name}_Sill", mat, 0, sill/2, width, sill)
    
    top_y = sill + a_h
    top_h = height - top_y
    if top_h > 0: create_block(container, f"{name}_Header", mat, 0, top_y + top_h/2, width, top_h)
    
    side_w = (width - a_w) / 2
    mid_y = sill + a_h/2
    center_offset = (a_w/2) + (side_w/2)
    create_block(container, f"{name}_L", mat, -center_offset, mid_y, side_w, a_h)
    create_block(container, f"{name}_R", mat, center_offset, mid_y, side_w, a_h)
    
    if asset.get("type") == "WINDOW":
        spawn_loc = Vector((0, 3.0, sill + a_h/2))
        bpy.ops.object.empty_add(type='SPHERE', location=(0,0,0))
        sp = bpy.context.active_object
        sp.name = f"{name}_Spawn"
        sp.parent = container
        sp.location = spawn_loc
        sp.scale = (0.5, 0.5, 0.5)

def generate_wall_composition(length, config, mandatory_asset=None):
    segments = []
    occupied_ranges = [] 
    
    # 1. Mandatory
    if mandatory_asset:
        m_data = config["assets"][mandatory_asset]
        m_w = m_data.get("width", 10.0)
        m_pos = 0 # FORCED CENTER FOR DOORS (Simplifies path connections)
        segments.append((mandatory_asset, m_pos))
        occupied_ranges.append((m_pos - m_w/2, m_pos + m_w/2))
        
    # 2. Probabilistic Fill
    asset_keys = [k for k,v in config["assets"].items() if k != "SOLID" and v.get("chance", 0) > 0]
    
    for _ in range(12):
        choice = random.choice(asset_keys)
        data = config["assets"][choice]
        chance = data.get("chance", 0.1)
        
        if random.random() > chance: continue
        
        w = data.get("width", 5.0)
        pos = random.uniform(-(length/2)+w, (length/2)-w)
        
        # Collision Check
        min_x = pos - w/2
        max_x = pos + w/2
        collision = False
        for (o_min, o_max) in occupied_ranges:
            if not (max_x < o_min or min_x > o_max):
                collision = True; break
        
        if not collision:
            segments.append((choice, pos))
            occupied_ranges.append((min_x, max_x))
            
    segments.sort(key=lambda x: x[1])
    
    # Fill Gaps
    final_composition = []
    current_x = -length/2
    
    for asset, pos in segments:
        data = config["assets"][asset]
        w = data.get("width", 10.0)
        start_asset = pos - w/2
        gap = start_asset - current_x
        if gap > 1.0: final_composition.append(("SOLID", current_x + gap/2, gap))
        final_composition.append((asset, pos, w))
        current_x = start_asset + w
        
    remaining = (length/2) - current_x
    if remaining > 1.0: final_composition.append(("SOLID", current_x + remaining/2, remaining))
         
    return final_composition

def build_wall_v7(name, location, rotation_z, length, height, config, mandatory_asset=None):
    bpy.ops.object.empty_add(location=location)
    container = bpy.context.active_object
    container.name = name
    container.rotation_euler = (0, 0, rotation_z)
    
    mat = bpy.data.materials.get("Mat_Wall_V5")
    if not mat:
        mat = bpy.data.materials.new("Mat_Wall_V5")
        mat.use_nodes = True
        
    composition = generate_wall_composition(length, config, mandatory_asset)
    
    for i, (atype, pos_x, width) in enumerate(composition):
        bpy.ops.object.empty_add(location=(0,0,0))
        seg = bpy.context.active_object
        seg.name = f"{name}_{i}_{atype}"
        seg.parent = container
        seg.location = (pos_x, 0, 0)
        create_wall_segment(seg, seg.name, mat, width, height, atype, config)
        
    return container

def create_arena_v7(index, location, entry_vec, exit_vec, arena_type_id="1"):
    size = 80.0
    config = get_arena_config(arena_type_id)
    room_name = f"Arena_{index}_Type{arena_type_id}"
    
    # Determine Door Directions
    entry_dir = "NONE"
    if entry_vec:
        v = entry_vec.normalized()
        angle = math.atan2(v.x, v.y)
        snap = round(angle / (math.pi/2)) * (math.pi/2)
        deg = math.degrees(snap)
        if abs(deg) < 1: entry_dir = "SOUTH"
        elif abs(deg - 180) < 1 or abs(deg+180) < 1: entry_dir = "NORTH"
        elif abs(deg - 90) < 1: entry_dir = "WEST"
        elif abs(deg + 90) < 1: entry_dir = "EAST"
        
    exit_dir = "NONE"
    if exit_vec:
        v = exit_vec.normalized()
        angle = math.atan2(v.x, v.y)
        snap = round(angle / (math.pi/2)) * (math.pi/2)
        deg = math.degrees(snap)
        if abs(deg) < 1: exit_dir = "NORTH"
        elif abs(deg - 180) < 1 or abs(deg+180) < 1: exit_dir = "SOUTH"
        elif abs(deg - 90) < 1: exit_dir = "EAST"
        elif abs(deg + 90) < 1: exit_dir = "WEST"

    # Floor
    bpy.ops.mesh.primitive_plane_add(size=size, location=location)
    floor = bpy.context.active_object
    floor.name = f"{room_name}_Floor"
    mat = bpy.data.materials.get("Mat_Floor")
    if mat: floor.data.materials.append(mat)
    
    walls_def = {
        "NORTH": (Vector((0, size/2, 0)), 0),
        "SOUTH": (Vector((0, -size/2, 0)), math.pi),
        "EAST": (Vector((size/2, 0, 0)), math.pi/2),
        "WEST": (Vector((-size/2, 0, 0)), -math.pi/2),
    }

    f_min = config.get("floors_min", 2)
    f_max = config.get("floors_max", 3)
    num_floors = random.randint(f_min, f_max)
    f_height = config.get("floor_height", 6.0)
    
    door_locations = {"ENTRY": None, "EXIT": None, "ENTRY_NORMAL": None, "EXIT_NORMAL": None}

    for f in range(num_floors):
        z = f * f_height
        is_ground = (f == 0)
        
        for aspect, (offset, rot) in walls_def.items():
            mandatory = None
            if is_ground:
                if aspect == entry_dir: 
                    mandatory = "GATE"
                    door_locations["ENTRY"] = location + offset + Vector((0,0,1.7)) 
                    door_locations["ENTRY_NORMAL"] = offset.normalized() # Normals point OUT from center
                elif aspect == exit_dir: 
                    mandatory = "GATE"
                    door_locations["EXIT"] = location + offset + Vector((0,0,1.7))
                    door_locations["EXIT_NORMAL"] = offset.normalized()
            
            w_loc = location + offset + Vector((0,0,z))
            build_wall_v7(f"{room_name}_F{f}_{aspect}", w_loc, rot, size, f_height, config, mandatory)
            
    return door_locations

# --- PATHS V7 (HEIGHT CONTROLLED) ---
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

def create_path_v7(index, start_loc, end_loc, type="INTERNAL", start_normal=None, end_normal=None):
    
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
    
    # Defaults
    path_dir = (end_loc - start_loc).normalized()
    points = []
    runway = 15.0
    
    if type == "INTERNAL":
        # Force alignment with Normals
        # start_normal points OUT (Entry Wall). We go IN: -start_normal
        # end_normal points OUT (Exit Wall). We go OUT: end_normal
        
        dir_start = -start_normal if start_normal else path_dir
        dir_end = end_normal if end_normal else path_dir 
        
        p0 = start_loc
        p1 = start_loc + (dir_start * runway) 
        p2 = end_loc - (dir_end * runway) 
        p3 = end_loc
        
        if (end_loc - start_loc).length < 32.0:
             points = [p0, p3]
        else:
             points = [p0, p1, p2, p3]
             
    else: # TRANSITION
        # start_normal points OUT (Exit Prev). We go OUT: start_normal
        # end_normal points OUT (Entry Next). We go IN: -end_normal
        
        dir_start = start_normal if start_normal else path_dir
        dir_end = -end_normal if end_normal else path_dir
        
        p0 = start_loc
        p1 = start_loc + (dir_start * runway)
        p2 = end_loc - (dir_end * runway)
        p3 = end_loc
        
        points = [p0, p1, p2, p3]
        
    spline.bezier_points.add(len(points)-1)
    v_spline.bezier_points.add(len(points)-1)
    
    for i, p in enumerate(points):
        bp = spline.bezier_points[i]
        bp.co = p
        
        bpy.ops.mesh.primitive_uv_sphere_add(radius=0.8, location=p)
        bpy.context.active_object.name = f"DEBUG_{'TR' if type!='INT' else 'IN'}_{i}"

        vp = v_spline.bezier_points[i]
        vp.co = p
        vp.co.z = 0 
        
        # Handle Logic
        # For Internal/Transition runways, handles must be aligned 
        h_len = runway / 2.0
        
        # Tangents
        tangent = Vector((0,1,0))
        if i < len(points)-1:
            tangent = (points[i+1] - points[i]).normalized()
        elif i > 0:
            tangent = (points[i] - points[i-1]).normalized()
            
        handle_vec = tangent * h_len
        
        if type != "INTERNAL" and i == 1: # Takeoff
             handle_vec_up = handle_vec + Vector((0,0,25))
             bp.handle_left = bp.co - handle_vec
             bp.handle_right = bp.co + handle_vec_up
        elif type != "INTERNAL" and i == 2: # Landing
             bp.handle_left = bp.co - handle_vec + Vector((0,0,25))
             bp.handle_right = bp.co + handle_vec
        else:
            bp.handle_left = bp.co - handle_vec
            bp.handle_right = bp.co + handle_vec
            
        vp.handle_left = vp.co - handle_vec
        vp.handle_right = vp.co + handle_vec
        if type != "INTERNAL" and (i==1 or i==2):
             perp = Vector((-tangent.y, tangent.x, 0)) * 20
             if i==1: vp.handle_right += perp
             if i==2: vp.handle_left += perp

    return c_obj

def generate_map_v7(num_arenas=4):
    clear_scene()
    print("Generating V7 (Types + Height Control)...")
    
    positions = [Vector((0,0,0))]
    curr = Vector((0,0,0))
    heading = 0
    for _ in range(num_arenas-1):
        heading += random.uniform(-60, 60)
        curr += Vector((math.sin(math.radians(heading))*200, math.cos(math.radians(heading))*200, 0))
        positions.append(curr.copy())
        
    prev_door_exit = None
    
    available_types = list(ARENA_TYPES.keys())
    
    for i in range(num_arenas):
        pos = positions[i]
        entry = (pos - positions[i-1]) if i > 0 else None
        exit = (positions[i+1] - pos) if i < (num_arenas-1) else None
        
        # Pick Type
        atype = random.choice(available_types)
        
        doors = create_arena_v7(i, pos, entry, exit, arena_type_id=atype)
        
        # Paths
        curr_entry = doors["ENTRY"]
        curr_entry_n = doors["ENTRY_NORMAL"]
        curr_exit = doors["EXIT"]
        curr_exit_n = doors["EXIT_NORMAL"]
        
        # Transition Path (Exit Prev -> Entry Curr)
        if prev_door_exit and curr_entry:
            create_path_v7(f"Transition_{i}", prev_door_exit, curr_entry, "TRANSITION", 
                           start_normal=prev_exit_normal, end_normal=curr_entry_n)
            
        # Internal Path (Entry Curr -> Exit Curr)
        if curr_entry and curr_exit:
            create_path_v7(f"Internal_{i}", curr_entry, curr_exit, "INTERNAL",
                           start_normal=curr_entry_n, end_normal=curr_exit_n)
        elif curr_entry:
            # Last Arena
            center_loc = pos + Vector((0,0,1.7))
            # Just go straight in 
            create_path_v7(f"Internal_{i}", curr_entry, center_loc, "INTERNAL",
                           start_normal=curr_entry_n, end_normal=None)
            
        prev_door_exit = curr_exit
        prev_exit_normal = curr_exit_n
        
    print("V7 Complete.")

generate_map_v7()
