import bpy
import math

moon = bpy.data.objects["Moon"]

# clear old animation 
moon.animation_data_clear()

# frame 1
bpy.context.scene.frame_set(1)
moon.rotation_euler[2] = 0
moon.keyframe_insert(data_path="rotation_euler", index=2)

# frame 250
bpy.context.scene.frame_set(250)
moon.rotation_euler[2] = math.radians(360)
moon.keyframe_insert(data_path="rotation_euler", index=2)

# linear motion
action = moon.animation_data.action
for fcurve in action.fcurves:
    for key in fcurve.keyframe_points:
        key.interpolation = 'LINEAR'