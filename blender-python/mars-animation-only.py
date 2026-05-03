import bpy
import math

mars = bpy.data.objects["Mars"]

# clear old animation 
mars.animation_data_clear()

# frame 1
bpy.context.scene.frame_set(1)
mars.rotation_euler[2] = 0
mars.keyframe_insert(data_path="rotation_euler", index=2)

# frame 250
bpy.context.scene.frame_set(250)
mars.rotation_euler[2] = math.radians(360)
mars.keyframe_insert(data_path="rotation_euler", index=2)

# linear motion
action = mars.animation_data.action
for fcurve in action.fcurves:
    for key in fcurve.keyframe_points:
        key.interpolation = 'LINEAR'