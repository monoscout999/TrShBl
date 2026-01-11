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

def create_wall_with_window(name, location, rotation_z, width=20, height=8, thick=1.0):
    """
    Creates a wall with a window in the center by assembling 4 blocks:
    Bottom (sill), Top (lintel), Left, Right.
    Returns the wall object (empty container) and the window location.
    """
    # Container
    bpy.ops.object.empty_add(location=location)
    wall_container = bpy.context.active_object
    wall_container.name = name
    wall_container.rotation_euler = (0, 0, rotation_z)
    
    # Dimensions
    window_w = 6.0
    window_h = 3.0
    sill_h = 2.0
    
    # Material
    mat = bpy.data.materials.get("Mat_Wall")
    if not mat:
        mat = bpy.data.materials.new("Mat_Wall")
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        bsdf.inputs["Base Color"].default_value = (0.2, 0.2, 0.25, 1.0) # Concrete

    # Helper to clean code
    def add_block(subname, px, pz, sx, sz):
        bpy.ops.mesh.primitive_cube_add(size=1)
        blk = bpy.context.active_object
        blk.name = f"{name}_{subname}"
        blk.data.materials.append(mat)
        # Scale
        blk.scale = (sx, thick, sz)
        # Position (Local to container)
        # We must set matrix parent, but simple parent + loc is easier
        blk.parent = wall_container
        blk.location = (px, 0, pz)
        
    # 1. Bottom (Sill)
    # Width: Full, Height: sill_h
    add_block("Bottom", 0, sill_h/2, width, sill_h)
    
    # 2. Top (Lintel)
    # Starts at sill_h + window_h. Height: Remaining
    top_y = sill_h + window_h
    top_h = height - top_y
    if top_h > 0:
        add_block("Top", 0, top_y + top_h/2, width, top_h)
        
    # 3. Left Side
    # Width: (Total - Window)/2
    side_w = (width - window_w) / 2
    side_cen = window_w/2 + side_w/2
    mid_y = sill_h + window_h/2
    add_block("Left", -side_cen, mid_y, side_w, window_h)
    
    # 4. Right Side
    add_block("Right", side_cen, mid_y, side_w, window_h)
    
    # Calculate global window position for spawn
    # Local window pos: (0, 0, sill_h + window_h/2) transforms to global
    window_local_pos = Vector((0, 2.0, sill_h)) # Offset 'behind' wall slightly?
    # Actually return the 'center' of the window hole
    return wall_container

def create_procedural_room(index, location, size=20.0):
    room_name = f"Arena_{index}"
    
    # 1. Floor
    bpy.ops.mesh.primitive_plane_add(size=size, location=location)
    floor = bpy.context.active_object
    floor.name = f"{room_name}_Floor"
    
    # Material Floor
    mat_floor = bpy.data.materials.new("Mat_Floor")
    mat_floor.use_nodes = True
    mat_floor.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.1, 0.1, 0.1, 1.0)
    floor.data.materials.append(mat_floor)
    
    # 2. Walls (4 sides)
    height = 8.0
    half = size / 2.0
    
    # Positions relative to center
    wall_defs = [
        # (LocOffset, RotZ)
        (Vector((0, half, 0)), 0),           # North
        (Vector((0, -half, 0)), math.pi),    # South
        (Vector((half, 0, 0)), math.pi/2),   # East
        (Vector((-half, 0, 0)), -math.pi/2)  # West
    ]
    
    spawns = []
    
    for i, (offset, rot) in enumerate(wall_defs):
        # Decide: Wall with Window or Solid?
        # Let's make them ALL Windows for this test to see spawns
        w_loc = location + offset
        wall_obj = create_wall_with_window(f"{room_name}_Wall_{i}", w_loc, rot, width=size, height=height)
        
        # Create Spawn Point BEHIND the window
        # The wall logic puts the window at center.
        # We want the spawn OUTSIDE the room, 3 meters behind the window.
        
        spawn_offset_dist = 4.0 # meters behind wall
        # Calculate vector 'behind' based on rotation
        # Rotation 0 (North) -> Normal is (0, -1)? No, usually Y is normal?
        # Let's assume standard local: Y is thickness.
        
        # Determine normal vector from rotation
        normal = Vector((0, 1, 0)) # Assuming Y is "along" the wall? No, X is width. Y is thickness.
        # Wait, in create_wall: "blk.scale = (sx, thick, sz)". Y is thickness.
        # So Y+ is one side, Y- is other.
        # We placed walls at perimeter. We want spawn 'outside'.
        # If wall is at (0, 10), outside is (0, 14). So +Y relative to wall?
        
        spawn_local = Vector((0, spawn_offset_dist, 3.0)) # 3m up (window height)
        
        # Transform to global
        mat_rot = mathutils.Matrix.Rotation(rot, 4, 'Z')
        spawn_global = w_loc + (mat_rot @ spawn_local)
        
        bpy.ops.object.empty_add(type='SPHERE', location=spawn_global)
        spawn = bpy.context.active_object
        spawn.name = f"Spawn_{index}_Window_{i}"
        
        spawns.append(spawn)

    # 3. Player Point
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location + Vector((0, 0, 1.7)))
    player = bpy.context.active_object
    player.name = f"Player_Point_{index}"
    
    return floor, player

def create_road_profile():
    """Creates a 2D curve to act as the profile for the road (bevel object)."""
    # Check if exists
    if bpy.data.objects.get("Road_Profile"):
        return bpy.data.objects.get("Road_Profile")
        
    # Create flat profile (Line)
    # 8 meters wide
    curveData = bpy.data.curves.new('Road_Profile', type='CURVE')
    curveData.dimensions = '2D'
    
    curveObj = bpy.data.objects.new('Road_Profile', curveData)
    bpy.context.collection.objects.link(curveObj)
    
    spline = curveData.splines.new('POLY')
    spline.points.add(1) # Total 2
    spline.points[0].co = (-4.0, 0.0, 0.0, 1.0) # Left
    spline.points[1].co = (4.0, 0.0, 0.0, 1.0)  # Right
    
    # Hide it
    curveObj.hide_viewport = True
    curveObj.hide_render = True
    return curveObj

def create_path(index, start_loc, end_loc):
    # Same path logic as before
    dist = (end_loc - start_loc).length
    direction = (end_loc - start_loc).normalized()
    side_vector = Vector((-direction.y, direction.x, 0)) 
    
    p1 = start_loc + (direction * (dist * 0.33)) + (side_vector * random.uniform(-10, 10))
    p1.z += random.uniform(-5, 5)
    p2 = start_loc + (direction * (dist * 0.66)) + (side_vector * random.uniform(-10, 10))
    p2.z += random.uniform(-5, 5)

    curveData = bpy.data.curves.new(f'Path_{index}', type='CURVE')
    curveData.dimensions = '3D'
    curveData.resolution_u = 24 # Smoother
    
    # Use Profile instead of round tube
    profile = create_road_profile()
    curveData.bevel_mode = 'OBJECT'
    curveData.bevel_object = profile
    curveData.use_fill_caps = False
    
    curveObj = bpy.data.objects.new(f'Path_{index}', curveData)
    bpy.context.collection.objects.link(curveObj)

    spline = curveData.splines.new('BEZIER')
    spline.bezier_points.add(1) 
    
    bp0 = spline.bezier_points[0]
    bp0.co = start_loc
    bp0.handle_left = start_loc - direction * 15 # Longer handles for smoother start
    bp0.handle_right = p1 
    
    bp1 = spline.bezier_points[1]
    bp1.co = end_loc
    bp1.handle_left = p2 
    bp1.handle_right = end_loc + direction * 15
    
    # Material for Road
    mat = bpy.data.materials.get("Mat_Floor") # Reuse floor material
    if mat:
        curveData.materials.append(mat)
    
    return curveObj

def generate_map_v2(num_arenas=3):
    clear_scene()
    print("Generating Procedural Rooms V2 (Wide Roads)...")
    
    # Ensure profile exists
    create_road_profile()
    
    current_loc = Vector((0, 0, 0))
    prev_player = None
    
    cumulative_heading = 0
    
    for i in range(num_arenas):
        # Create Room
        floor_obj, player = create_procedural_room(i, current_loc, size=20.0)
        
        # Path
        if prev_player:
            create_path(i, prev_player.location, player.location)
            
        # Next Loc
        turn = random.uniform(-45, 45)
        cumulative_heading += turn
        rad = math.radians(cumulative_heading)
        dist = 100.0
        
        step = Vector((math.sin(rad)*dist, math.cos(rad)*dist, random.uniform(-5, 5))) 
        current_loc += step
        prev_player = player
        
    print("Done.")

generate_map_v2(3)
