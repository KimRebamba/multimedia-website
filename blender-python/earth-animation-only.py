import bpy
import math

earth = bpy.data.objects["Earth"]

# clear old animation
earth.animation_data_clear()

# frame 1
bpy.context.scene.frame_set(1)
earth.rotation_euler[2] = 0
earth.keyframe_insert(data_path="rotation_euler", index=2)

# frame 250
bpy.context.scene.frame_set(250)
earth.rotation_euler[2] = math.radians(360)
earth.keyframe_insert(data_path="rotation_euler", index=2)

# linear motion
action = earth.animation_data.action
for fcurve in action.fcurves:
    for key in fcurve.keyframe_points:
        key.interpolation = 'LINEAR' 