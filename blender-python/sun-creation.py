import bpy

# create sun sphere
bpy.ops.mesh.primitive_uv_sphere_add(
    radius=2,
    location=(0, 0, 0)
)

sun = bpy.context.object
sun.name = "Sun-Planet"

# create glowing glowing glowing glowing glowing
mat = bpy.data.materials.new(name="SunMaterial")
mat.use_nodes = True

nodes = mat.node_tree.nodes
links = mat.node_tree.links

# clear default nodes
for node in nodes:
    nodes.remove(node)

# create nodes
output = nodes.new(type='ShaderNodeOutputMaterial')
emission = nodes.new(type='ShaderNodeEmission')

# set glow color
emission.inputs["Color"].default_value = (1.0, 0.5, 0.0, 1)
emission.inputs["Strength"].default_value = 15

# connect nodes
links.new(emission.outputs["Emission"], output.inputs["Surface"])

# assign material
sun.data.materials.append(mat)

# added image texture after and edited compositor to add a glare node for that glowww

# pretty useless code since i couldve just used an emission then added the image. I dont even 
# know what these do but anyways