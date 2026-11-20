# AURA Purple Heart Diamond — 30s vertical Reel scene
# Storyboard by APInex free/gemini-4-hydrogen (cost 0 tokens); script rebuilt
# from that storyboard with axis/label fixes. Blender 4.2, Z-up, camera at -Y.
import bpy, math, random
random.seed(7)

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete()

scene = bpy.context.scene
scene.render.engine = 'CYCLES'
scene.cycles.device = 'CPU'
scene.cycles.samples = 16
scene.cycles.use_denoising = True
scene.render.resolution_x = 1080
scene.render.resolution_y = 1920
scene.render.fps = 30
scene.frame_start = 1
scene.frame_end = 720  # 24s of Blender; stills open/close 3s each -> 30s total
scene.cycles.use_denoising = True
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = "//render/"

# World: bright blue
world = bpy.data.worlds.new("World")
scene.world = world
world.use_nodes = True
world.node_tree.nodes["Background"].inputs[0].default_value = (0.72, 0.04, 0.32, 1.0)
world.node_tree.nodes["Background"].inputs[1].default_value = 1.0

def principled(name, color, rough=0.3, metallic=0.0, emission=None, e_strength=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metallic
    if emission is not None:
        b.inputs["Emission Color"].default_value = (*emission, 1.0)
        b.inputs["Emission Strength"].default_value = e_strength
    return m

# ---- Floor: blue/white checker, Z=0 ----
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
floor = bpy.context.active_object  # default XY plane IS the floor (Z-up)
fm = bpy.data.materials.new("Floor_Mat"); fm.use_nodes = True
n = fm.node_tree.nodes; n.clear()
out = n.new("ShaderNodeOutputMaterial"); bsdf = n.new("ShaderNodeBsdfDiffuse")
chk = n.new("ShaderNodeTexChecker"); chk.inputs[3].default_value = 24.0
chk.inputs[1].default_value = (0.85, 0.08, 0.42, 1.0)
chk.inputs[2].default_value = (1.0, 0.72, 0.85, 1.0)
fm.node_tree.links.new(chk.outputs[0], bsdf.inputs[0])
fm.node_tree.links.new(bsdf.outputs[0], out.inputs[0])
floor.data.materials.append(fm)

# ---- Glowing backdrop rectangle behind bottle ----
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 5.0, 2.5))
glow = bpy.context.active_object
glow.scale = (7.0, 4.0, 1.0)
glow.rotation_euler = (math.radians(90), 0, 0)  # XY plane -> vertical wall facing camera
glow.data.materials.append(principled("Glow_Mat", (0.75, 0.9, 1.0), rough=1.0,
                                       emission=(1.0, 0.55, 0.75), e_strength=0.8))

# ---- Bottle rig (parent empty at floor centre) ----
bpy.ops.object.empty_add(location=(0, 0, 0))
rig = bpy.context.active_object
rig.name = "BottleRig"

burgundy = principled("Burgundy_Glass", (0.38, 0.03, 0.10), rough=0.12, metallic=0.1)
_b = burgundy.node_tree.nodes["Principled BSDF"]
_b.inputs["Coat Weight"].default_value = 1.0
_b.inputs["Coat Roughness"].default_value = 0.05
# diamond-cut bump: brick texture rotated 45 deg as bump
bn = burgundy.node_tree.nodes
brick = bn.new("ShaderNodeTexBrick")
brick.inputs["Scale"].default_value = 10.0
brick.inputs["Mortar Size"].default_value = 0.03
bump = bn.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 1.0
burgundy.node_tree.links.new(brick.outputs[0], bump.inputs[2])
burgundy.node_tree.links.new(bump.outputs[0], bn["Principled BSDF"].inputs["Normal"])

def parent_to_rig(obj):
    obj.parent = rig

# Body: bevelled box, dims 1.0 x 0.5 x 2.2, centre z=1.1
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 1.1))
body = bpy.context.active_object; body.name = "BottleBody"
body.scale = (1.0, 0.5, 2.2)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
bev = body.modifiers.new("Bevel", 'BEVEL'); bev.width = 0.06; bev.segments = 3
bpy.ops.object.modifier_apply(modifier="Bevel")
body.data.materials.append(burgundy)
parent_to_rig(body)

# Diamond-cut studs: real 4-sided pyramids on front/back faces so the
# facets catch light (bump alone reads flat from the front)
for _face, _y, _rx in (("front", -0.26, math.radians(90)),
                       ("back", 0.26, math.radians(-90))):
    for _ix in (-0.36, -0.18, 0.0, 0.18, 0.36):
        for _iz in range(9):
            _z = 0.18 + _iz * 0.21
            if _face == "front" and 0.95 <= _z <= 1.50:
                continue  # keep the label area clear
            bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.075, depth=0.045,
                                            location=(_ix, _y, _z))
            _s = bpy.context.active_object
            _s.rotation_euler = (_rx, 0, math.radians(45))
            _s.data.materials.append(burgundy)
            parent_to_rig(_s)

# Neck
bpy.ops.mesh.primitive_cylinder_add(radius=0.20, depth=0.35, location=(0, 0, 2.32))
neck = bpy.context.active_object; neck.name = "BottleNeck"
neck.data.materials.append(principled("White_Gloss", (1, 1, 1), rough=0.08))
parent_to_rig(neck)

# Cap: white sphere, smooth-shaded
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.34, location=(0, 0, 2.62))
cap = bpy.context.active_object; cap.name = "BottleCap"
bpy.ops.object.shade_smooth_by_angle()
cap.data.materials.append(principled("Cap_White", (1, 1, 1), rough=0.05))
parent_to_rig(cap)

# Label: white plane on FRONT face (y=-0.26), facing camera (-Y)
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, -0.26, 1.15))
label = bpy.context.active_object; label.name = "Label"
label.scale = (0.85, 0.60, 1.0)
label.rotation_euler = (math.radians(90), 0, 0)
label.data.materials.append(principled("Label_White", (1, 1, 1), rough=0.25))
parent_to_rig(label)

# Label text (faces -Y, glyphs up = +Z)
def add_text(body_text, loc, size, mat, name):
    bpy.ops.object.text_add(location=loc)
    t = bpy.context.active_object; t.name = name
    t.data.body = body_text
    t.data.align_x = 'CENTER'; t.data.align_y = 'CENTER'
    t.data.size = size
    t.rotation_euler = (math.radians(90), 0, 0)
    t.data.materials.append(mat)
    return t

darkred = principled("Text_Red", (0.35, 0.02, 0.08), rough=0.2)
lt = add_text("PURPLE HEART\nDIAMOND", (0, -0.28, 1.22), 0.11, darkred, "LabelText")
parent_to_rig(lt)
at = add_text("AURA PERFUME", (0, -0.28, 0.72), 0.09,
              principled("Text_White", (1, 1, 1), rough=0.2), "LabelBrand")
parent_to_rig(at)

# ---- Lights ----
bpy.ops.object.light_add(type='AREA', location=(5, -6, 7))
key = bpy.context.active_object; key.data.energy = 1200; key.data.shape = 'DISK'; key.data.size = 4
bpy.ops.object.light_add(type='POINT', location=(4, -4, 3))
pink = bpy.context.active_object; pink.data.color = (1.0, 0.45, 0.65); pink.data.energy = 900
bpy.ops.object.light_add(type='AREA', location=(-5, -4, 3))
fill = bpy.context.active_object; fill.data.energy = 500; fill.data.color = (1.0, 0.6, 0.8)
bpy.ops.object.light_add(type='AREA', location=(-6, -3, 5))
rim = bpy.context.active_object; rim.data.energy = 900; rim.data.color = (1.0, 0.85, 0.9)

# ---- Camera + track-to ----
bpy.ops.object.empty_add(location=(0, 0, 1.15))
target = bpy.context.active_object; target.name = "CamTarget"
bpy.ops.object.camera_add(location=(0, -8.5, 1.7))
cam = bpy.context.active_object; cam.name = "Camera"
scene.camera = cam
con = cam.constraints.new('TRACK_TO'); con.target = target
con.track_axis = 'TRACK_NEGATIVE_Z'; con.up_axis = 'UP_Y'

cam_keys = [  # frame, location  (6 shots x 4s)
    (1,   (0, -8.5, 1.7)),
    (120, (0, -7.2, 1.6)),
    (240, (2.5, -7.0, 1.9)),
    (360, (0, -4.2, 1.4)),   # close-up on label
    (480, (0, -10.0, 2.6)),  # wide
    (600, (0, -8.0, 1.9)),
    (720, (0, -8.0, 1.9)),
]
for f, loc in cam_keys:
    cam.location = loc
    cam.keyframe_insert(data_path="location", frame=f)
for fc in cam.animation_data.action.fcurves:
    for kp in fc.keyframe_points:
        kp.interpolation = 'LINEAR'

# ---- Bottle rotation 121-240 (360 deg), hold after ----
rig.rotation_euler = (0, 0, 0)
rig.keyframe_insert(data_path="rotation_euler", frame=120)
rig.rotation_euler = (0, 0, math.radians(360))
rig.keyframe_insert(data_path="rotation_euler", frame=240)
rig.keyframe_insert(data_path="rotation_euler", frame=720)

# ---- Particles: 80 floating sparkles ----
spark_mat = principled("Spark", (1, 1, 1), rough=0.1, emission=(1.0, 0.55, 0.75), e_strength=2.5)
for i in range(80):
    x = random.uniform(-4, 4); y = random.uniform(-3, 4); z0 = random.uniform(0.2, 5.5)
    bpy.ops.mesh.primitive_ico_sphere_add(radius=random.uniform(0.012, 0.028),
                                          location=(x, y, z0))
    p = bpy.context.active_object
    p.data.materials.append(spark_mat)
    p.keyframe_insert(data_path="location", frame=1)
    p.location = (x, y, z0 + random.uniform(0.5, 1.5))
    p.keyframe_insert(data_path="location", frame=360)
    p.keyframe_insert(data_path="location", frame=720)

# ---- End card text (visible frames 601-720 only) ----
et1 = add_text("PURPLE HEART\nDIAMOND", (0, -1.2, 3.9), 0.55,
               principled("End_White", (1, 1, 1), rough=0.2), "EndTitle")
et2 = add_text("AURA PERFUME", (0, -1.2, 2.9), 0.38,
               principled("End_Pink", (1.0, 0.45, 0.65), rough=0.2), "EndBrand")
for obj in (et1, et2):
    obj.hide_render = True; obj.hide_viewport = True
    obj.keyframe_insert(data_path="hide_render", frame=1)
    obj.keyframe_insert(data_path="hide_viewport", frame=1)
    obj.keyframe_insert(data_path="hide_render", frame=600)
    obj.keyframe_insert(data_path="hide_viewport", frame=600)
    obj.hide_render = False; obj.hide_viewport = False
    obj.keyframe_insert(data_path="hide_render", frame=601)
    obj.keyframe_insert(data_path="hide_viewport", frame=601)

print('SCENE READY')
