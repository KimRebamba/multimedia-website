import bpy
import math

planet = bpy.data.objects["Mercury"]

# clear old animation 
planet.animation_data_clear()

# frame 1
bpy.context.scene.frame_set(1)
planet.rotation_euler[2] = 0
planet.keyframe_insert(data_path="rotation_euler", index=2)

# frame 250
bpy.context.scene.frame_set(250)
planet.rotation_euler[2] = math.radians(360)
planet.keyframe_insert(data_path="rotation_euler", index=2)

# linear motion
action = planet.animation_data.action
for fcurve in action.fcurves:
    for key in fcurve.keyframe_points:
        key.interpolation = 'LINEAR'