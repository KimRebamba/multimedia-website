import bpy
import math

obj = bpy.data.objects["Saturn-Ring"]

obj.animation_data_clear()
obj.rotation_mode = 'XYZ'

# Keyframe 1
bpy.context.scene.frame_set(1)
base_rot = obj.rotation_euler.copy()
obj.keyframe_insert(data_path="rotation_euler")

# Keyframe 125 (half cycle)
bpy.context.scene.frame_set(125)
obj.rotation_euler = base_rot.copy()

# small spin
obj.rotation_euler[2] += math.radians(20)

# tilt
obj.rotation_euler[0] += math.radians(2)
obj.rotation_euler[1] -= math.radians(2)

obj.keyframe_insert(data_path="rotation_euler")

# Keyframe 250 (loop back)
bpy.context.scene.frame_set(250)
obj.rotation_euler = base_rot.copy()
obj.keyframe_insert(data_path="rotation_euler")

# looping
action = obj.animation_data.action
for fcurve in action.fcurves:
    for key in fcurve.keyframe_points:
        key.interpolation = 'BEZIER'

    mod = fcurve.modifiers.new(type='CYCLES')
    mod.mode_before = 'REPEAT'
    mod.mode_after = 'REPEAT'