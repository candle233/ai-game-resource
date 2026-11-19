# Classic western revolver (Colt SAA style) - procedural build
# Axes: barrel along Y (muzzle at -Y), Z up, units in meters.
# Real proportions: total ~0.29 m, barrel 132 mm, cylinder 55 mm.
import bpy
import bmesh
import math
import time
import traceback
from math import radians, sin, cos

DIR = r"D:\Game materials.library\blender\revolver"
BLEND = DIR + r"\revolver.blend"
PREVIEW = DIR + r"\preview_round1.png"
PREVIEW_SIDE = DIR + r"\preview_round1_side.png"
DONE = DIR + r"\done_round1.flag"
ERROR = DIR + r"\error_round1.txt"

AZ = 0.10  # cylinder/barrel axis height


def active():
    return bpy.context.view_layer.objects.active


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = getattr(bpy.context, "scene", None) or bpy.context.window.scene

    # ---------- materials ----------
    def make_mat(name, color, rough, metallic):
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = color
        b.inputs["Metallic"].default_value = metallic
        b.inputs["Roughness"].default_value = rough
        return m

    mat_steel = make_mat("Steel", (0.60, 0.62, 0.66, 1.0), 0.30, 1.0)
    mat_dark = make_mat("DarkSteel", (0.07, 0.07, 0.08, 1.0), 0.45, 1.0)
    mat_wood = make_mat("Wood", (0.32, 0.14, 0.05, 1.0), 0.55, 0.0)
    mat_floor = make_mat("Floor", (0.06, 0.06, 0.07, 1.0), 0.9, 0.0)

    def assign(obj, mat):
        obj.data.materials.clear()
        obj.data.materials.append(mat)

    # ---------- helpers ----------
    def add_cyl(name, radius, depth, loc, verts=32):
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=verts, radius=radius, depth=depth,
            location=loc, rotation=(radians(90), 0, 0))
        o = active()
        o.name = name
        return o

    def add_cube(name, size3, loc, rot=None, bev=None):
        bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
        o = active()
        o.name = name
        o.scale = size3
        bpy.ops.object.transform_apply(scale=True)
        if rot:
            o.rotation_euler = rot
            bpy.ops.object.transform_apply(rotation=True)
        if bev:
            m = o.modifiers.new("Bevel", 'BEVEL')
            for attr in ("width", "offset"):
                if hasattr(m, attr):
                    setattr(m, attr, bev)
                    break
            m.segments = 2
        return o

    def smooth(obj):
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        try:
            bpy.ops.object.shade_auto_smooth(angle=radians(40))
        except Exception:
            try:
                bpy.ops.object.shade_smooth()
            except Exception:
                pass

    def apply_bools(base):
        # 5.x-safe: bake the evaluated mesh instead of using modifier_apply ops
        deps = bpy.context.evaluated_depsgraph_get()
        ev = base.evaluated_get(deps)
        new_me = bpy.data.meshes.new_from_object(ev)
        old = base.data
        base.data = new_me
        base.modifiers.clear()
        if old is not new_me:
            bpy.data.meshes.remove(old)

    cutters = []

    def cutter_cyl(name, radius, depth, loc, verts=24):
        o = add_cyl(name, radius, depth, loc, verts=verts)
        cutters.append(o)
        return o

    def cutter_cube(name, size3, loc):
        bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
        o = active()
        o.name = name
        o.scale = size3
        bpy.ops.object.transform_apply(scale=True)
        cutters.append(o)
        return o

    # ---------- barrel ----------
    barrel = add_cyl("Barrel", 0.0115, 0.132, (0, -0.124, AZ))
    cutter_cyl("BoreCutter", 0.006, 0.013, (0, -0.184, AZ))

    front_sight = add_cube("FrontSight", (0.0035, 0.016, 0.010),
                           (0, -0.180, 0.1175), bev=0.001)

    # ---------- cylinder ----------
    cyl = add_cyl("Cylinder", 0.027, 0.055, (0, -0.0075, AZ), verts=64)

    # 6 flutes
    for i in range(6):
        th = radians(30 + i * 60)
        cutter_cyl(f"FluteC_{i}", 0.0055, 0.034,
                   (0.0268 * sin(th), -0.0075, AZ + 0.0268 * cos(th)))
    # 6 chamber mouths on front face
    for i in range(6):
        th = radians(i * 60)
        cutter_cyl(f"ChamberC_{i}", 0.0042, 0.005,
                   (0.0155 * cos(th), -0.034, AZ + 0.0155 * sin(th)), verts=16)

    # ---------- frame ----------
    frame_front = add_cube("FrameFront", (0.030, 0.0245, 0.048),
                           (0, -0.04575, 0.109), bev=0.0015)
    recoil_plate = add_cube("RecoilPlate", (0.030, 0.021, 0.058),
                            (0, 0.0295, 0.104), bev=0.0015)
    floor_slab = add_cube("FloorSlab", (0.022, 0.077, 0.013),
                          (0, 0.0025, 0.0685), bev=0.0015)
    top_strap = add_cube("TopStrap", (0.013, 0.096, 0.006),
                         (0, 0.0, 0.131), bev=0.0012)
    # rear sight notch (cut)
    cutter_cube("NotchC", (0.005, 0.010, 0.004), (0, 0.044, 0.1325))

    # ---------- trigger guard + trigger ----------
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.026, minor_radius=0.0045,
        location=(0, -0.004, 0.044), rotation=(0, radians(90), 0))
    trigger_guard = active()
    trigger_guard.name = "TriggerGuard"
    trigger_guard.scale = (1.0, 1.25, 1.0)
    bpy.ops.object.transform_apply(scale=True)

    trigger = add_cube("Trigger", (0.005, 0.005, 0.018),
                       (0, -0.003, 0.052), rot=(radians(8), 0, 0), bev=0.001)

    # ---------- hammer ----------
    hammer_body = add_cube("HammerBody", (0.010, 0.012, 0.024),
                           (0, 0.047, 0.110), bev=0.002)
    hammer_spur = add_cube("HammerSpur", (0.006, 0.016, 0.004),
                           (0, 0.054, 0.127), rot=(radians(25), 0, 0), bev=0.0015)

    # ---------- ejector rod (under barrel, right side) ----------
    ejector_housing = add_cyl("EjectorHousing", 0.0065, 0.095,
                              (0.0075, -0.1075, 0.0865))
    ejector_rod = add_cyl("EjectorRod", 0.0025, 0.018,
                          (0.0075, -0.164, 0.0865))
    ejector_head = add_cyl("EjectorHead", 0.005, 0.007,
                           (0.0075, -0.1745, 0.0865))

    # ---------- grip (wood, tapered + curved + raked back) ----------
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16, radius=0.021, depth=0.095, location=(0, 0, 0))
    grip = active()
    grip.name = "Grip"
    bm = bmesh.new()
    bm.from_mesh(grip.data)
    # subdivide lengthwise into 3 segments so the grip can curve
    vert_edges = [e for e in bm.edges
                  if abs(e.verts[0].co.z - e.verts[1].co.z) > 0.01]
    bmesh.ops.subdivide_edges(bm, edges=vert_edges, cuts=2, use_grid_fill=True)
    TOP_Z = 0.0475
    for v in bm.verts:
        t = max(0.0, min(1.0, (TOP_Z - v.co.z) / 0.095))  # 0 top, 1 bottom
        s = 1.0 - 0.30 * (t ** 1.4)                        # progressive taper
        v.co.x *= s
        v.co.y *= s
        v.co.y += 0.030 * (t ** 1.6)                       # progressive back-curve
    bm.to_mesh(grip.data)
    grip.data.update()
    bm.free()
    grip.scale = (1.0, 0.72, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    grip.rotation_euler = (radians(26), 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    grip.location = (0, 0.047, 0.034)

    # ---------- booleans ----------
    bore_c = [c for c in cutters if c.name == "BoreCutter"][0]
    m = barrel.modifiers.new("Bool", 'BOOLEAN')
    m.operation = 'DIFFERENCE'
    try:
        m.solver = 'EXACT'
    except Exception:
        pass
    m.object = bore_c
    apply_bools(barrel)

    for c in cutters:
        if c.name.startswith("FluteC") or c.name.startswith("ChamberC"):
            m = cyl.modifiers.new("Bool", 'BOOLEAN')
            m.operation = 'DIFFERENCE'
            try:
                m.solver = 'EXACT'
            except Exception:
                pass
            m.object = c
    apply_bools(cyl)

    notch = [c for c in cutters if c.name == "NotchC"][0]
    m = top_strap.modifiers.new("Bool", 'BOOLEAN')
    m.operation = 'DIFFERENCE'
    try:
        m.solver = 'EXACT'
    except Exception:
        pass
    m.object = notch
    apply_bools(top_strap)

    # delete helpers (data API - ops.delete is unreliable in 5.x)
    for c in cutters:
        bpy.data.objects.remove(c, do_unlink=True)
    cutters.clear()

    # dark disc inside muzzle bore
    bore_disc = add_cyl("BoreDisc", 0.0055, 0.001, (0, -0.1797, AZ), verts=24)

    # ---------- materials ----------
    for o in [barrel, top_strap, frame_front, recoil_plate, floor_slab,
              cyl, front_sight]:
        assign(o, mat_steel)
    for o in [trigger_guard, trigger, hammer_body, hammer_spur,
              ejector_housing, ejector_rod, ejector_head, bore_disc]:
        assign(o, mat_dark)
    assign(grip, mat_wood)

    # ---------- smooth shading ----------
    for o in [barrel, cyl, ejector_housing, ejector_rod, ejector_head,
              bore_disc, trigger_guard, grip]:
        smooth(o)

    # ---------- scene: floor / lights / cameras ----------
    bpy.ops.mesh.primitive_plane_add(size=2, location=(0, 0, -0.05))
    floor = active()
    floor.name = "Floor"
    assign(floor, mat_floor)

    w = bpy.data.worlds.new("World")
    scene.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.50, 0.52, 0.55, 1.0)
    bg.inputs[1].default_value = 0.5

    suns = [
        ((radians(27), radians(-16), 0), 2.0),
        ((radians(-14.5), radians(21), 0), 0.5),
        ((radians(-30), radians(-3), 0), 1.2),
    ]
    for i, (rot, e) in enumerate(suns):
        bpy.ops.object.light_add(type='SUN', location=(0, 0, 0.5))
        s = active()
        s.name = f"Sun{i}"
        s.rotation_euler = rot
        s.data.energy = e

    bpy.ops.object.empty_add(type='PLAIN_AXES', location=(0, -0.045, 0.07))
    target = active()
    target.name = "CamTarget"

    bpy.ops.object.camera_add(location=(-0.34, -0.52, 0.22))
    cam = active()
    cam.name = "CamMain"
    cam.data.lens = 55
    c = cam.constraints.new('TRACK_TO')
    c.target = target
    c.track_axis = 'TRACK_NEGATIVE_Z'
    c.up_axis = 'UP_Y'

    bpy.ops.object.camera_add(location=(0.60, -0.045, 0.075))
    cam_side = active()
    cam_side.name = "CamSide"
    cam_side.data.type = 'ORTHO'
    cam_side.data.ortho_scale = 0.38
    c = cam_side.constraints.new('TRACK_TO')
    c.target = target
    c.track_axis = 'TRACK_NEGATIVE_Z'
    c.up_axis = 'UP_Y'

    # ---------- save ----------
    bpy.ops.wm.save_as_mainfile(filepath=BLEND)

    # ---------- render ----------
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = 64
    try:
        scene.cycles.use_denoising = True
    except Exception:
        pass
    try:
        scene.view_settings.look = 'AgX - Medium High Contrast'
    except Exception:
        pass
    scene.render.image_settings.file_format = 'PNG'

    scene.camera = cam
    scene.render.resolution_x = 1400
    scene.render.resolution_y = 900
    scene.render.filepath = PREVIEW
    bpy.ops.render.render(write_still=True)

    scene.camera = cam_side
    scene.render.resolution_x = 1500
    scene.render.resolution_y = 700
    scene.render.filepath = PREVIEW_SIDE
    bpy.ops.render.render(write_still=True)

    with open(DONE, 'w') as f:
        f.write("done %s\n" % time.ctime())
        f.write(BLEND + "\n" + PREVIEW + "\n" + PREVIEW_SIDE + "\n")
    print("ROUND1 OK")


try:
    main()
except Exception:
    with open(ERROR, 'w') as f:
        f.write(traceback.format_exc())
    traceback.print_exc()
