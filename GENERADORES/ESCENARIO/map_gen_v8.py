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

# --- GEOMETRY HELPERS REUSED ---
def create_block(parent, name, mat, px, pz, sx, sz, rotation_z=0):
    bpy.ops.mesh.primitive_cube_add(size=1)
    blk = bpy.context.active_object
    blk.name = name
    if mat: blk.data.materials.append(mat)
    blk.scale = (sx, 2.0, sz)
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
    create_block(container, f"{name}_L", mat, -(a_w/2 + side_w/2), sill + a_h/2, side_w, a_h)
    create_block(container, f"{name}_R", mat, (a_w/2 + side_w/2), sill + a_h/2, side_w, a_h)
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
    if mandatory_asset:
        m_data = config["assets"][mandatory_asset]
        m_w = m_data.get("width", 10.0)
        m_pos = 0 
        segments.append((mandatory_asset, m_pos))
        occupied_ranges.append((m_pos - m_w/2, m_pos + m_w/2))
    asset_keys = [k for k,v in config["assets"].items() if k != "SOLID" and v.get("chance", 0) > 0]
    for _ in range(12):
        choice = random.choice(asset_keys)
        data = config["assets"][choice]
        chance = data.get("chance", 0.1)
        if random.random() > chance: continue
        w = data.get("width", 5.0)
        pos = random.uniform(-(length/2)+w, (length/2)-w)
        collision = False
        for (o_min, o_max) in occupied_ranges:
            if not (pos + w/2 < o_min or pos - w/2 > o_max): collision = True; break
        if not collision: segments.append((choice, pos)); occupied_ranges.append((pos-w/2, pos+w/2))
    segments.sort(key=lambda x: x[1])
    final_composition = []
    current_x = -length/2
    for asset, pos in segments:
        data = config["assets"][asset]
        w = data.get("width", 10.0)
        gap = (pos - w/2) - current_x
        if gap > 1.0: final_composition.append(("SOLID", current_x + gap/2, gap))
        final_composition.append((asset, pos, w))
        current_x = pos + w/2
    remaining = (length/2) - current_x
    if remaining > 1.0: final_composition.append(("SOLID", current_x + remaining/2, remaining))
    return final_composition

def build_wall_v7(name, location, rotation_z, length, height, config, mandatory_asset=None):
    bpy.ops.object.empty_add(location=location)
    container = bpy.context.active_object
    container.name = name
    container.rotation_euler = (0, 0, rotation_z)
    mat = bpy.data.materials.get("Mat_Wall_V5")
    if not mat:mat = bpy.data.materials.new("Mat_Wall_V5"); mat.use_nodes = True
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
    config = get_arena_config(arena_type_id)
    room_name = f"Arena_{index}_Type{arena_type_id}"
    entry_dir = "NONE"
    if entry_vec:
        v = entry_vec.normalized()
        snap = round(math.atan2(v.x, v.y) / (math.pi/2)) * (math.pi/2)
        deg = math.degrees(snap)
        if abs(deg) < 1: entry_dir = "SOUTH"
        elif abs(deg - 180) < 1 or abs(deg+180) < 1: entry_dir = "NORTH"
        elif abs(deg - 90) < 1: entry_dir = "WEST"
        elif abs(deg + 90) < 1: entry_dir = "EAST"
    exit_dir = "NONE"
    if exit_vec:
        v = exit_vec.normalized()
        snap = round(math.atan2(v.x, v.y) / (math.pi/2)) * (math.pi/2)
        deg = math.degrees(snap)
        if abs(deg) < 1: exit_dir = "NORTH"
        elif abs(deg - 180) < 1 or abs(deg+180) < 1: exit_dir = "SOUTH"
        elif abs(deg - 90) < 1: exit_dir = "EAST"
        elif abs(deg + 90) < 1: exit_dir = "WEST"

    bpy.ops.mesh.primitive_plane_add(size=80.0, location=location)
    floor = bpy.context.active_object
    floor.name = f"{room_name}_Floor"
    mat = bpy.data.materials.get("Mat_Floor")
    if mat: floor.data.materials.append(mat)
    
    walls_def = {"NORTH": (Vector((0, 40, 0)), 0), "SOUTH": (Vector((0, -40, 0)), math.pi),
                 "EAST": (Vector((40, 0, 0)), math.pi/2), "WEST": (Vector((-40, 0, 0)), -math.pi/2)}
    f_min, f_max = config.get("floors_min", 2), config.get("floors_max", 3)
    num_floors = random.randint(f_min, f_max)
    f_height = config.get("floor_height", 6.0)
    door_locations = {"ENTRY": None, "EXIT": None, "ENTRY_NORMAL": None, "EXIT_NORMAL": None}

    for f in range(num_floors):
        z = f * f_height
        for aspect, (offset, rot) in walls_def.items():
            mandatory = None
            if f == 0:
                if aspect == entry_dir: 
                    mandatory = "GATE"
                    door_locations["ENTRY"] = location + offset + Vector((0,0,1.7)) 
                    door_locations["ENTRY_NORMAL"] = offset.normalized() 
                elif aspect == exit_dir: 
                    mandatory = "GATE"
                    door_locations["EXIT"] = location + offset + Vector((0,0,1.7))
                    door_locations["EXIT_NORMAL"] = offset.normalized()
            build_wall_v7(f"{room_name}_F{f}_{aspect}", location + offset + Vector((0,0,z)), rot, 80.0, f_height, config, mandatory)
    return door_locations

def get_arena_config(type_id):
    defaults = GLOBAL_STYLE.copy()
    defaults["assets"] = defaults["assets"].copy() 
    specific = ARENA_TYPES.get(str(type_id), {})
    if "wall_height" in specific: defaults["floor_height"] = specific["wall_height"]
    if "floors_min" in specific: defaults["floors_min"] = specific["floors_min"]
    if "floors_max" in specific: defaults["floors_max"] = specific["floors_max"]
    overrides = specific.get("asset_overrides", {})
    for asset_k, asset_v in overrides.items():
        if asset_k in defaults["assets"]:
            for k, v in asset_v.items(): defaults["assets"][asset_k][k] = v
    return defaults


# --- MASTER PATH ACCUMULATOR (V8) ---

class MasterPath:
    def __init__(self):
        self.points = [] # List of {'co': Vector, 'h_left': Vector, 'h_right': Vector, 'tilt': float}
        
    def add_point(self, co, h_left, h_right, tilt=0.0):
        self.points.append({'co': co, 'h_left': h_left, 'h_right': h_right, 'tilt': tilt})

    def append_segment(self, start_p, end_p, type="INTERNAL", start_normal=None, end_normal=None):
        path_dir = (end_p - start_p).normalized()
        runway = 15.0
        
        pts = [] 
        
        if type == "INTERNAL":
            dir_start = -start_normal if start_normal else path_dir
            dir_end = end_normal if end_normal else path_dir
            p0 = start_p
            p1 = start_p + (dir_start * runway) 
            p2 = end_p - (dir_end * runway) 
            p3 = end_p
            pts = [p0, p1, p2, p3]
            # Internal always flat
            tilts = [0.0, 0.0, 0.0, 0.0]
            
        else: # TRANSITION
            dir_start = start_normal if start_normal else path_dir
            dir_end = -end_normal if end_normal else path_dir
            p0 = start_p
            p1 = start_p + (dir_start * runway)
            p2 = end_p - (dir_end * runway)
            p3 = end_p
            
            # Apex for flight
            mid = (p1 + p2) / 2
            
            # ADD LATERAL SWERVE (Dynamic Flight)
            # Calculate side vector
            side = Vector((-path_dir.y, path_dir.x, 0)) # Perpendicular in XY
            swerve_amount = random.uniform(-1, 1) * 25.0 # +/- 25m swerve
            
            mid_z = mid + Vector((0,0,35)) + (side * swerve_amount)
            
            pts = [p0, p1, mid_z, p2, p3]
            
            # Calculate Banking for Apex
            # Turn direction determined by Cross Product of StartDir and EndDir
            vec_in = (mid_z - p1).normalized()
            vec_out = (p2 - mid_z).normalized()
            
            cross = vec_in.cross(vec_out)
            # Z component > 0 = Left Turn
            # Bank Factor
            bank_factor = 3.0 # Stronger banking for visual impact
            apex_tilt = cross.z * bank_factor
            
            tilts = [0.0, 0.0, apex_tilt, 0.0, 0.0]
            
        start_idx = 0
        if self.points:
            last = self.points[-1]['co']
            if (last - pts[0]).length < 0.5:
                start_idx = 1
                # Update handle/tilt of join point (P0/Last)
                self.points[-1]['tilt'] = tilts[0] # Should be 0 anyway
                
                if type == "TRANSITION":
                    h_vec = (pts[1] - pts[0]).normalized() * (runway/2)
                    self.points[-1]['h_right'] = self.points[-1]['co'] + h_vec
                else: 
                    h_vec = (pts[1] - pts[0]).normalized() * (runway/2)
                    self.points[-1]['h_right'] = self.points[-1]['co'] + h_vec
                    
        for i in range(start_idx, len(pts)):
            p = pts[i]
            t = tilts[i]
            
            # Standard Tangent Logic
            h_len = runway / 2.0
            tangent = Vector((0,1,0))
            if i < len(pts)-1: tangent = (pts[i+1] - p).normalized()
            elif i > 0: tangent = (p - pts[i-1]).normalized()
            
            # Flight Override
            if type == "TRANSITION":
                if i == 1: # Takeoff (P1)
                    tangent = (p1 - p0).normalized()
                elif i == 3: # Landing (P2/3)
                    tangent = (p3 - p2).normalized()
                elif i == 2: # Apex
                    tangent = (p2 - p1).normalized() 
                    h_len = (p2-p1).length / 3 
            
            h_vec = tangent * h_len
            self.points.append({'co': p, 'h_left': p - h_vec, 'h_right': p + h_vec, 'tilt': t})

    def build(self):
        c_data = bpy.data.curves.new('Camera_Path_Master', 'CURVE')
        c_data.dimensions = '3D'
        c_data.twist_mode = 'Z_UP' # Crucial for stable banking
        c_obj = bpy.data.objects.new('Camera_Path_Master', c_data)
        bpy.context.collection.objects.link(c_obj)
        
        spline = c_data.splines.new('BEZIER')
        spline.bezier_points.add(len(self.points)-1)
        
        for i, pt in enumerate(self.points):
            bp = spline.bezier_points[i]
            bp.co = pt['co']
            bp.handle_left = pt['h_left']
            bp.handle_right = pt['h_right']
            bp.handle_left_type = 'FREE'
            bp.handle_right_type = 'FREE'
            bp.tilt = pt['tilt']
            
        return c_obj

def generate_map_v8(num_arenas=4):
    clear_scene()
    print("Generating V8 Single Path...")
    
    positions = [Vector((0,0,0))]
    curr = Vector((0,0,0))
    heading = 0
    for _ in range(num_arenas-1):
        heading += random.uniform(-60, 60)
        curr += Vector((math.sin(math.radians(heading))*200, math.cos(math.radians(heading))*200, 0))
        positions.append(curr.copy())
        
    master_path = MasterPath()
    
    prev_door_exit = None
    prev_exit_n = None
    
    available_types = list(ARENA_TYPES.keys())
    
    for i in range(num_arenas):
        pos = positions[i]
        entry = (pos - positions[i-1]) if i > 0 else None
        exit = (positions[i+1] - pos) if i < (num_arenas-1) else None
        
        atype = random.choice(available_types)
        doors = create_arena_v7(i, pos, entry, exit, arena_type_id=atype)
        
        curr_entry = doors["ENTRY"]
        curr_entry_n = doors["ENTRY_NORMAL"]
        curr_exit = doors["EXIT"]
        curr_exit_n = doors["EXIT_NORMAL"]
        
        # Transition Path
        if prev_door_exit and curr_entry:
            master_path.append_segment(prev_door_exit, curr_entry, "TRANSITION", prev_exit_n, curr_entry_n)
            
        # Internal Path
        if curr_entry and curr_exit:
            master_path.append_segment(curr_entry, curr_exit, "INTERNAL", curr_entry_n, curr_exit_n)
        elif curr_entry:
            center_loc = pos + Vector((0,0,1.7))
            master_path.append_segment(curr_entry, center_loc, "INTERNAL", curr_entry_n, None)
            
        prev_door_exit = curr_exit
        prev_exit_n = curr_exit_n
        
    master_path.build()
    print("V8 Complete.")

generate_map_v8(num_arenas=5)
