import bpy
import math

sun = bpy.data.objects["Sun-Planet"]

# clear old animation
sun.animation_data_clear()

# frame 1
bpy.context.scene.frame_set(1)
sun.rotation_euler[2] = 0
sun.keyframe_insert(data_path="rotation_euler", index=2)

# frame 250
bpy.context.scene.frame_set(250)
sun.rotation_euler[2] = math.radians(360)
sun.keyframe_insert(data_path="rotation_euler", index=2)

# make smooth constant rotation
action = sun.animation_data.action
for fcurve in action.fcurves:
    for key in fcurve.keyframe_points:
        key.interpolation = 'LINEAR'