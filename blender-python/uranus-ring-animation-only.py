import bpy
import math

obj = bpy.data.objects["Uranus-Ring"]

obj.animation_data_clear()
obj.rotation_mode = 'XYZ'

# Frame 1
bpy.context.scene.frame_set(1)
base_rot = obj.rotation_euler.copy()
obj.keyframe_insert(data_path="rotation_euler")

# Frame 125 (half cycle)
bpy.context.scene.frame_set(125)
obj.rotation_euler = base_rot.copy()

# small spin (adjust axis if needed)
obj.rotation_euler[1] += math.radians(20)

# subtle "infinity wobble"
obj.rotation_euler[0] += math.radians(2)
obj.rotation_euler[2] -= math.radians(2)

obj.keyframe_insert(data_path="rotation_euler")

# Frame 250 (loop back)
bpy.context.scene.frame_set(250)
obj.rotation_euler = base_rot.copy()
obj.keyframe_insert(data_path="rotation_euler")

# Smooth looping
action = obj.animation_data.action
for fcurve in action.fcurves:
    for key in fcurve.keyframe_points:
        key.interpolation = 'BEZIER'

    mod = fcurve.modifiers.new(type='CYCLES')
    mod.mode_before = 'REPEAT'
    mod.mode_after = 'REPEAT'