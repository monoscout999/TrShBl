import bpy
import math
import random
import json
import os
import mathutils
from mathutils import Vector

# --- CONFIGURATION ---
CONFIG_PATH = r"C:\Trailshoot\GENERADORES\ESCENARIO\CONFIG\map_styles.json"

def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r') as f:
                data = json.load(f)
                print(f"Loaded config from {CONFIG_PATH}")
                return data.get("styles", {})
        except Exception as e:
            print(f"Error loading JSON: {e}")
            
    # Fallback default
    return {
        "standard": {
            "floor_height": 6.0,
            "wall_thickness": 1.0,
            "assets": {
                "GATE": { "width": 14.0, "height": 5.0, "sill": 0.0, "type": "OPENING" },
                "DOOR": { "width": 3.5, "height": 2.5, "sill": 0.0, "type": "OPENING" },
                "BIG_WINDOW": { "width": 7.0, "height": 3.0, "sill": 1.5, "type": "WINDOW" },
                "WINDOW": { "width": 3.5, "height": 1.5, "sill": 1.5, "type": "WINDOW" },
                "SOLID": { "type": "WALL" }
            }
        }
    }

STYLES = load_config()

ACTIVE_STYLE = STYLES["standard"]

def clear_scene():
    for o in bpy.data.objects:
        bpy.data.objects.remove(o, do_unlink=True)
    for m in bpy.data.meshes:
        bpy.data.meshes.remove(m)

def create_block(parent, name, mat,  px, pz, sx, sz, rotation_z=0):
    bpy.ops.mesh.primitive_cube_add(size=1)
    blk = bpy.context.active_object
    blk.name = name
    if mat: blk.data.materials.append(mat)
    
    # Scale
    thick = ACTIVE_STYLE["wall_thickness"]
    blk.scale = (sx, thick, sz)
    
    # Position
    blk.parent = parent
    blk.location = (px, 0, pz)
    blk.rotation_euler.z = rotation_z

def create_wall_segment(container, name, mat, width, height, asset_type):
    """
    Generates a generic Segment of wall (defined width) containing a specific Asset (Door, Window, etc).
    """
    asset_data = ACTIVE_STYLE["assets"].get(asset_type, {})
    
    # If type is SOLID or unknown, just build a wall
    if asset_data.get("type") == "WALL" or not asset_data:
        create_block(container, f"{name}_Solid", mat, 0, height/2, width, height)
        return

    # If Opening or Window
    a_w = asset_data["width"]
    a_h = asset_data["height"]
    sill = asset_data["sill"]
    
    # 1. Base (Sill)
    if sill > 0:
        create_block(container, f"{name}_Sill", mat, 0, sill/2, width, sill)
    
    # 2. Header (Lintel)
    top_y = sill + a_h
    top_h = height - top_y
    if top_h > 0:
        create_block(container, f"{name}_Header", mat, 0, top_y + top_h/2, width, top_h)
        
    # 3. Sides (Pillars)
    # Remaining width on sides
    side_w = (width - a_w) / 2
    
    mid_y = sill + a_h/2
    center_offset = (a_w/2) + (side_w/2)
    
    create_block(container, f"{name}_L", mat, -center_offset, mid_y, side_w, a_h)
    create_block(container, f"{name}_R", mat, center_offset, mid_y, side_w, a_h)
    
    # 4. Spawns (Logic)
    # If it's a WINDOW/BIG_WINDOW, create spawn point
    if asset_data.get("type") == "WINDOW":
        spawn_loc = Vector((0, 3.0, sill + a_h/2)) # 3m behind, centered
        # We need to transform this local pos to world eventually, but empty is child of container
        bpy.ops.object.empty_add(type='SPHERE', location=(0,0,0))
        sp = bpy.context.active_object
        sp.name = f"{name}_Spawn"
        sp.parent = container
        sp.location = spawn_loc
        sp.scale = (0.5, 0.5, 0.5)

def build_modular_wall(name, location, rotation_z, w_length=80, w_height=6, flavor="MIXED"):
    """
    Constructs a wall by stacking Segments horizontally based on a pattern.
    flavor: "GATE_WALL", "DOOR_WALL", "MIXED_WINDOWS", "SOLID"
    """
    # Container
    bpy.ops.object.empty_add(location=location)
    container = bpy.context.active_object
    container.name = name
    container.rotation_euler = (0, 0, rotation_z)
    
    mat = bpy.data.materials.get("Mat_Wall_V5")
    if not mat:
        mat = bpy.data.materials.new("Mat_Wall_V5")
        mat.use_nodes = True
        mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.3, 0.3, 0.3, 1.0)
        
    # LOGIC: Divide wall into slots? 
    # Or just place a center piece and fill rest?
    # Let's use a "Slot" system. 
    # For 80m wall, we can have: 
    # Center (20m) - SideA (30m) - SideB (30m)? No.
    # Pattern Logic: [Corner] [Body] [Body] [Center] [Body] [Body] [Corner]
    
    # Dynamic Pattern Generation
    # We have w_length (e.g. 80m). We need to fill it with assets.
    # Central Logic:
    # 1. Place "mandatory" feature for the flavor (e.g. Gate/Door in center).
    # 2. Fill remaining space with random choice of permitted assets.
    
    segments = [] # List of (AssetType, PositionX)
    
    available_assets = ["SOLID", "WINDOW", "BIG_WINDOW"]
    center_asset = None
    
    if flavor == "GATE_WALL":
        center_asset = "GATE"
    elif flavor == "DOOR_WALL":
        center_asset = "DOOR"
    elif flavor == "MIXED_WINDOWS":
        # Maybe a central big window or solid
        center_asset = random.choice(["BIG_WINDOW", "SOLID"])
    else: # SOLID
        center_asset = "SOLID"
        available_assets = ["SOLID"]

    # Get Center Dimensions
    c_data = ACTIVE_STYLE["assets"][center_asset]
    c_width = c_data.get("width", 10.0) # Default if missing
    
    # Place Center
    # Relative to container 0
    segments.append( (center_asset, 0) )
    
    # Fill Sides (Left and Right)
    # Remaining space on ONE side
    remaining_side = (w_length - c_width) / 2
    
    # Fill function
    def fill_space(start_offset, direction):
        # direction: -1 (Left), 1 (Right)
        current_x = (c_width/2) * direction
        space_left = remaining_side
        
        while space_left > 2.0: # Minimum chunk
            # Pick random asset that fits
            candidates = [a for a in available_assets]
            # Shuffle
            random.shuffle(candidates)
            
            chosen = "SOLID" # Fallback
            chosen_w = 0
            
            for cand in candidates:
                w = ACTIVE_STYLE["assets"][cand].get("width", 10.0)
                if w <= space_left:
                    chosen = cand
                    chosen_w = w
                    break
            
            # If nothing fits, fill with SOLID partial?
            if chosen_w == 0:
                # Force a small solid or break
                chosen = "SOLID"
                chosen_w = space_left # Fill rest
            
            # Position
            # Center of new block is: current_x + (width/2)*dir
            pos_x = current_x + (chosen_w/2 * direction)
            segments.append( (chosen, pos_x) )
            
            current_x += chosen_w * direction
            space_left -= chosen_w

    fill_space(0, -1) # Left
    fill_space(0, 1)  # Right

    # Sort segments by X just for cleanliness (optional)
    segments.sort(key=lambda x: x[1])

    # Build Objects
    for asset_type, pos_x in segments:
        # Determine width from JSON
        # Note: If we had a partial "SOLID" filling remainder, width logic needs care.
        # But for now assuming standard sizes fit or specific "SOLID" logic handles it.
        # The 'create_wall_segment' uses standard JSON width. 
        # If we passed a custom width for the filler solid, we'd need to pass it.
        # Simplification: Just use standard asset width.
        
        real_w = ACTIVE_STYLE["assets"][asset_type].get("width", 10.0)
        
        # Helper Empty
        bpy.ops.object.empty_add(location=(0,0,0))
        seg_obj = bpy.context.active_object
        seg_obj.name = f"{name}_{asset_type}"
        seg_obj.parent = container
        seg_obj.location = (pos_x, 0, 0)
        
        create_wall_segment(seg_obj, seg_obj.name, mat, real_w, w_height, asset_type)
        
    return container

# ... (Previous math functions for cardinal direction kept same) ...
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

def create_arena_v5(index, location, entry_vec, exit_vec):
    size = 80.0
    room_name = f"Arena_{index}"
    
    # 1. Floor
    bpy.ops.mesh.primitive_plane_add(size=size, location=location)
    floor = bpy.context.active_object
    floor.name = f"{room_name}_Floor"
    mat = bpy.data.materials.get("Mat_Floor")
    if mat: floor.data.materials.append(mat)
    
    # 2. Doors Logic
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

    walls_def = {
        "NORTH": (Vector((0, size/2, 0)), 0),
        "SOUTH": (Vector((0, -size/2, 0)), math.pi),
        "EAST": (Vector((size/2, 0, 0)), math.pi/2),
        "WEST": (Vector((-size/2, 0, 0)), -math.pi/2),
    }

    # 3. Build Multi-Story Walls
    num_floors = random.randint(1, 3)
    f_height = ACTIVE_STYLE["floor_height"]
    
    for f in range(num_floors):
        z = f * f_height
        is_ground = (f == 0)
        
        for direction, (offset, rot) in walls_def.items():
            # Determine Flavor
            flavor = "MIXED_WINDOWS"
            if is_ground:
                if direction in doors:
                    flavor = "GATE_WALL" # Standard path entry
                else:
                    flavor = random.choice(["MIXED_WINDOWS", "DOOR_WALL"]) # Maybe a small door for enemies?
            else:
                flavor = random.choice(["MIXED_WINDOWS", "SOLID"]) # Upper floors
            
            w_loc = location + offset + Vector((0,0,z))
            build_modular_wall(f"{room_name}_F{f}_{direction}", w_loc, rot, size, f_height, flavor)

    # Player Point
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location + Vector((0, 0, 2)))
    bpy.context.active_object.name = f"Player_Point_{index}"
    return bpy.context.active_object

# ... (Path logic reused from V4 - Create flat road) ...
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

def create_paths_v5(index, start_loc, end_loc):
    # Camera Path
    cam_curve_data = bpy.data.curves.new(f'Camera_Path_{index}', type='CURVE')
    cam_curve_data.dimensions = '3D'
    cam_curve_obj = bpy.data.objects.new(f'Camera_Path_{index}', cam_curve_data)
    bpy.context.collection.objects.link(cam_curve_obj)
    
    dist = (end_loc - start_loc).length
    direction = (end_loc - start_loc).normalized()
    side = Vector((-direction.y, direction.x, 0))
    
    spline = cam_curve_data.splines.new('BEZIER')
    spline.bezier_points.add(1)
    bp0 = spline.bezier_points[0]
    bp0.co = start_loc
    bp0.handle_left = start_loc - direction*30
    bp0.handle_right = start_loc + direction*30 + Vector((0,0,15))
    bp1 = spline.bezier_points[1]
    bp1.co = end_loc
    bp1.handle_left = end_loc - direction*30 + Vector((0,0,15))
    bp1.handle_right = end_loc + direction*30
    
    # Visual Path
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
    
    # Flat geometry on floor
    # We add side curvature for interest
    curve_offset = side * random.uniform(-20, 20)
    
    v_spline.bezier_points[0].co = start_loc
    v_spline.bezier_points[0].handle_left = start_loc - direction*25
    v_spline.bezier_points[0].handle_right = start_loc + direction*25 + curve_offset # Curve X
    
    v_spline.bezier_points[1].co = end_loc
    v_spline.bezier_points[1].handle_left = end_loc - direction*25 + curve_offset # Curve X
    v_spline.bezier_points[1].handle_right = end_loc + direction*25
    
    mat = bpy.data.materials.get("Mat_Floor")
    if mat: vis_curve_data.materials.append(mat)
    
    return cam_curve_obj

def generate_map_v5(num_arenas=4):
    clear_scene()
    print("Generating Map V5 (Modular Assets)...")
    
    # Pre-calculate positions
    positions = [Vector((0,0,0))]
    current = Vector((0,0,0))
    heading = 0
    for i in range(num_arenas-1):
        turn = random.uniform(-40, 40)
        heading += turn
        rad = math.radians(heading)
        dist = 140.0 
        current += Vector((math.sin(rad)*dist, math.cos(rad)*dist, 0))
        positions.append(current.copy())
        
    prev_player = None
    
    for i in range(num_arenas):
        pos = positions[i]
        entry = (pos - positions[i-1]) if i > 0 else None
        exit = (positions[i+1] - pos) if i < (num_arenas-1) else None
        
        p_point = create_arena_v5(i, pos, entry, exit)
        
        if prev_player:
            create_paths_v5(i, prev_player.location, p_point.location)
            
        prev_player = p_point
        
    print("V5 Complete.")

generate_map_v5()
