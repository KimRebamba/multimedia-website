import bpy
import math
import mathutils

scene = bpy.context.scene
scene.frame_start = 1
scene.frame_end = 720

# ── Clean slate ────────────────────────────────────────────
for o in list(bpy.data.objects):
    if o.name.startswith("ORBIT_"):
        bpy.data.objects.remove(o, do_unlink=True)

# Remove orphaned orbit curve data from previous runs
for c in list(bpy.data.curves):
    if c.name.startswith("ORBIT_") and c.users == 0:
        bpy.data.curves.remove(c)

for o in bpy.data.objects:
    if o.animation_data:
        o.animation_data_clear()

IDENTITY = mathutils.Matrix.Identity(4)

# ── Config ─────────────────────────────────────────────────
PLANETS = [
    ("Sun-Planet", 3.2, 0, 0.000, 2.0, 0.00),
    ("Mercury", 0.45, 7, 0.080, 0.15, 0.70),
    ("Venus", 0.80, 11, 0.050, 0.08, 2.40),
    ("Earth", 0.85, 16, 0.032, 2.00, 4.20),
    ("Mars", 0.60, 21, 0.020, 1.90, 1.00),
    ("Jupiter", 2.80, 29, 0.008, 5.00, 3.60),
    ("Saturn", 2.40, 38, 0.005, 4.50, 5.20),
    ("Uranus", 1.40, 47, 0.003, 3.00, 0.90),
    ("Neptune", 1.30, 55, 0.002, 3.20, 2.80),
    ("Pluto", 0.22, 62, 0.001, 0.40, 5.00),
]

ATTACHMENTS = {
    "Sun-Planet": [("Sun-Moon", 1.0)],
    "Saturn": [("Saturn-Ring", 3.5)],
    "Uranus": [("Uranus-Ring", 2.5)],
}

MOON_ORBIT = 2.2
MOON_SPEED = 0.18
MOON_SCALE = 0.22

# Multiplies all planet orbit radii (distance from the Sun).
# Use this to spread planets farther/closer without changing each entry.
ORBIT_SCALE = 1.8

# Visible orbit line settings
ORBIT_POINTS = 128
ORBIT_THICKNESS = 0.02
ORBIT_EMISSION = 3.0

FRAMES = 720
KF_STEP = 3

def obj(name):
    if not name:
        return None

    direct = bpy.data.objects.get(name)
    if direct:
        return direct

    # Be forgiving about how hyphens are spaced in object names.
    candidates = {
        name.replace(" - ", "-"),
        name.replace("-", " - "),
        name.replace(" -", "-"),
        name.replace("- ", "-"),
    }

    for cand in candidates:
        if not cand:
            continue
        o = bpy.data.objects.get(cand)
        if o:
            return o

    return None


def normalize_key(name: str) -> str:
    return name.replace(" - ", "-").replace(" -", "-").replace("- ", "-").strip()


def orbit_material():
    mat = bpy.data.materials.get("MAT_Orbit_White")
    if mat:
        return mat

    mat = bpy.data.materials.new(name="MAT_Orbit_White")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out = nodes.new(type="ShaderNodeOutputMaterial")
    out.location = (300, 0)

    em = nodes.new(type="ShaderNodeEmission")
    em.location = (0, 0)
    em.inputs["Color"].default_value = (1.0, 1.0, 1.0, 1.0)
    em.inputs["Strength"].default_value = ORBIT_EMISSION

    links.new(em.outputs["Emission"], out.inputs["Surface"])
    return mat


def create_orbit_path(obj_name: str, radius: float):
    if radius <= 0:
        return None

    crv = bpy.data.curves.new(name=f"ORBIT_{obj_name}_CRV", type='CURVE')
    crv.dimensions = '2D'
    crv.resolution_u = 12
    crv.bevel_depth = ORBIT_THICKNESS
    crv.bevel_resolution = 2

    spline = crv.splines.new(type='POLY')
    spline.points.add(ORBIT_POINTS - 1)
    for i in range(ORBIT_POINTS):
        a = (i / ORBIT_POINTS) * (math.tau)
        x = radius * math.cos(a)
        y = radius * math.sin(a)
        spline.points[i].co = (x, y, 0.0, 1.0)
    spline.use_cyclic_u = True

    path_obj = bpy.data.objects.new(f"ORBIT_{obj_name}", crv)
    scene.collection.objects.link(path_obj)
    path_obj.hide_viewport = False
    path_obj.hide_render = False
    path_obj.show_in_front = True

    mat = orbit_material()
    if len(path_obj.data.materials) == 0:
        path_obj.data.materials.append(mat)
    else:
        path_obj.data.materials[0] = mat

    return path_obj

def make_linear(o):
    if o.animation_data and o.animation_data.action:
        for fc in o.animation_data.action.fcurves:
            for kf in fc.keyframe_points:
                kf.interpolation = "LINEAR"

# ── Build hierarchy ────────────────────────────────────────
empties = {}
resolved_names = {}

for name, scale, orbit, spd, spin, phase in PLANETS:
    o = obj(name)
    if not o:
        print(f"[SKIP] {name}")
        continue

    # Ensure body is visible and not overridden by old constraints
    try:
        o.hide_set(False)
    except Exception:
        pass
    o.hide_viewport = False
    o.hide_render = False
    for const in list(o.constraints):
        o.constraints.remove(const)

    resolved_names[name] = o.name

    # Create orbit controller empty (hidden) used for animation
    e = bpy.data.objects.new(f"ORBIT_CTRL_{o.name}", None)
    scene.collection.objects.link(e)
    e.empty_display_type = 'PLAIN_AXES'
    e.empty_display_size = 0.01
    e.hide_viewport = True
    e.hide_render = True
    empties[o.name] = e

    # Create visible orbit path curve (white line)
    if orbit > 0:
        create_orbit_path(o.name, orbit * ORBIT_SCALE)

    # Reset transform
    o.parent = None
    o.location = (0, 0, 0)
    o.rotation_euler = (0, 0, 0)
    o.scale = (scale, scale, scale)

    # Parent to orbit empty
    o.parent = e
    o.matrix_parent_inverse = IDENTITY

    # ── Attachments (FIXED SCALING) ────────────────────────
    attachment_key = normalize_key(name)
    for child_name, child_scale in ATTACHMENTS.get(attachment_key, []):
        c = obj(child_name)
        if not c:
            continue

        # Remove constraints
        for const in list(c.constraints):
            c.constraints.remove(const)

        # Reset
        c.parent = None
        c.location = (0, 0, 0)
        c.rotation_euler = (0, 0, 0)

        # Parent FIRST
        c.parent = o
        c.matrix_parent_inverse = IDENTITY

        # FIX: compensate parent scale
        if c.type != 'LIGHT':
            inv = 1.0 / scale
            c.scale = (child_scale * inv, child_scale * inv, child_scale * inv)

        # Optional: tilt rings so they’re not flat pancakes
        if normalize_key(child_name) == "Saturn-Ring":
            c.rotation_euler = (math.radians(27), 0, 0)

        if normalize_key(child_name) == "Uranus-Ring":
            c.rotation_euler = (math.radians(98), 0, 0)

        print(f"  ↳ Attached {child_name} to {name}")

    print(f"[OK] {name}")

# ── Moon ───────────────────────────────────────────────────
moon = obj("Moon")
if moon and "Earth" in empties:
    moon.parent = None
    moon.location = (0, 0, 0)
    moon.scale = (MOON_SCALE, MOON_SCALE, MOON_SCALE)

    moon.parent = empties["Earth"]
    moon.matrix_parent_inverse = IDENTITY

    for f in range(1, FRAMES + 1, KF_STEP):
        a = MOON_SPEED * f
        moon.location = (MOON_ORBIT * math.cos(a), MOON_ORBIT * math.sin(a), 0)
        moon.keyframe_insert("location", frame=f)

    make_linear(moon)
    print("[OK] Moon orbit")

# ── Orbits + Spin ──────────────────────────────────────────
for name, scale, orbit, spd, spin, phase in PLANETS:
    resolved = resolved_names.get(name)
    if not resolved or resolved not in empties:
        continue

    e = empties[resolved]
    o = obj(resolved)

    for f in range(1, FRAMES + 1, KF_STEP):
        if orbit > 0:
            a = spd * f + phase
            r = orbit * ORBIT_SCALE
            e.location = (r * math.cos(a), r * math.sin(a), 0)
        else:
            e.location = (0, 0, 0)

        e.keyframe_insert("location", frame=f)

        # Spin
        o.rotation_euler = (0, 0, spin * f * 0.05)
        o.keyframe_insert("rotation_euler", frame=f)

    make_linear(e)

# ── Camera ─────────────────────────────────────────────────
cam = obj("Camera")
if cam:
    cam.parent = None
    cam.location = (42, -68, 48)

    target = mathutils.Vector((8, 0, 0))
    direction = target - cam.location
    rot = mathutils.Vector((0, 0, -1)).rotation_difference(direction)
    cam.rotation_euler = rot.to_euler()

    cam.data.lens = 24
    cam.data.clip_end = 500

    print("[OK] Camera")

print("\n✓ DONE — press Spacebar")