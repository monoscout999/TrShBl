import bpy
import math
import random
from mathutils import Vector

def create_arena(index, location, size=20.0):
    """Creates a basic placeholder arena (Cube) with player and spawn points."""
    # 1. Create the visual representation (Cube for now)
    bpy.ops.mesh.primitive_cube_add(size=size, location=location)
    arena_obj = bpy.context.active_object
    arena_obj.name = f"Arena_{index}"
    
    # 2. Setup Player Point (Where camera anchors)
    # Put it slightly above ground
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location + Vector((0, 0, 2)))
    player_point = bpy.context.active_object
    player_point.name = f"Player_Point_{index}"
    player_point.parent = arena_obj
    
    # 3. Setup Enemy Spawns (Placeholder locations)
    # Create 4 spawns in corners
    offsets = [
        Vector((size/2 - 2, size/2 - 2, 0)),
        Vector((-size/2 + 2, size/2 - 2, 0)),
        Vector((size/2 - 2, -size/2 + 2, 0)),
        Vector((-size/2 + 2, -size/2 + 2, 0))
    ]
    
    for j, offset in enumerate(offsets):
        bpy.ops.object.empty_add(type='SPHERE', location=location + offset + Vector((0, 0, 1)))
        spawn = bpy.context.active_object
        spawn.name = f"Spawn_{index}_{j}"
        spawn.parent = arena_obj

    return arena_obj, player_point

def create_path(index, start_loc, end_loc):
    """Creates a Bezier curve connecting two arenas."""
    # Calculate mid-points for control handles to create a nice curve/arc
    # mid = (start + end) / 2
    # We add some randomness to the 'handle' to make it curvy, not straight
    
    dist = (end_loc - start_loc).length
    direction = (end_loc - start_loc).normalized()
    side_vector = Vector((-direction.y, direction.x, 0)) # Perpendicular in XY
    
    # Control Point 1: 1/3 of the way, pushed to the side
    p1 = start_loc + (direction * (dist * 0.33)) + (side_vector * random.uniform(-20, 20))
    p1.z += random.uniform(-10, 10) # Add some height variation
    
    # Control Point 2: 2/3 of the way, pushed to the OTHER side (S-shape) or same
    p2 = start_loc + (direction * (dist * 0.66)) + (side_vector * random.uniform(-20, 20))
    p2.z += random.uniform(-10, 10)

    # Create curve data
    curveData = bpy.data.curves.new(f'Path_{index}', type='CURVE')
    curveData.dimensions = '3D'
    curveData.resolution_u = 12

    curveObj = bpy.data.objects.new(f'Path_{index}', curveData)
    bpy.context.collection.objects.link(curveObj)

    # Make a spline
    spline = curveData.splines.new('BEZIER')
    spline.bezier_points.add(1) # It has 1 by default, so now 2 points
    
    # Set Start Point
    bp0 = spline.bezier_points[0]
    bp0.co = start_loc
    bp0.handle_left = start_loc - direction * 10
    bp0.handle_right = p1 # Pull towards P1
    
    # Set End Point
    bp1 = spline.bezier_points[1]
    bp1.co = end_loc
    bp1.handle_left = p2 # Pull from P2
    bp1.handle_right = end_loc + direction * 10

    # Add bevel depth to make it visible as a "tube"
    curveData.bevel_depth = 1.0
    
    return curveObj

def generate_map(num_arenas=3):
    # Clear existing
    for o in bpy.data.objects:
        if "Arena" in o.name or "Path" in o.name or "Point" in o.name or "Spawn" in o.name:
            bpy.data.objects.remove(o, do_unlink=True)
            
    print(f"Generating Map with {num_arenas} Arenas...")
    
    current_loc = Vector((0, 0, 0))
    prev_player_point = None
    
    for i in range(num_arenas):
        # 1. Create Arena
        arena, player_point = create_arena(i, current_loc)
        
        # 2. Create Path from Previous
        if prev_player_point:
            # Connect PREVIOUS player point to CURRENT player point (flight path)
            # The path essentially starts where the camera WAS and ends where it WILL BE
            create_path(i, prev_player_point.location, player_point.location)
            
        # 3. Calculate Next Location (Random walk but generally moving away)
        # Random angle
        angle = random.uniform(-60, 60) # degrees deviation from forward
        heading = Vector((0, 100, 0)) # Base forward vector (100m step)
        rot_mat = mathutils.Matrix.Rotation(math.radians(angle), 4, 'Z')
        step = rot_mat @ heading
        
        # Add some height variation
        step.z = random.uniform(-20, 20)
        
        current_loc += step
        prev_player_point = player_point
        
    print("Map Generation Complete.")

# Blender Entry Point
import mathutils # Re-import to be safe
generate_map(num_arenas=5)
