import bpy
import math
import random

COUNT = 200         
INNER_RADIUS = 25    
OUTER_RADIUS = 35    
HEIGHT = 2.0        

MIN_SCALE = 0.2
MAX_SCALE = 0.5

source = bpy.data.objects.get("asteroid")

if source is None:
    raise Exception("Object named 'asteroid' not found.")

# Create collection
belt_collection = bpy.data.collections.get("AsteroidBelt")

if belt_collection is None:
    belt_collection = bpy.data.collections.new("AsteroidBelt")
    bpy.context.scene.collection.children.link(belt_collection)

for i in range(COUNT):

    angle = random.uniform(0, math.tau)

    radius = random.uniform(INNER_RADIUS, OUTER_RADIUS)

    x = math.cos(angle) * radius
    y = math.sin(angle) * radius
    z = random.uniform(-HEIGHT, HEIGHT)

    asteroid = source.copy()
    asteroid.data = source.data.copy()

    asteroid.location = (x, y, z)

    asteroid.rotation_euler = (
        random.uniform(0, math.tau),
        random.uniform(0, math.tau),
        random.uniform(0, math.tau)
    )

    scale = random.uniform(MIN_SCALE, MAX_SCALE)
    asteroid.scale = (scale, scale, scale)

    belt_collection.objects.link(asteroid)

print("Asteroid belt created!")