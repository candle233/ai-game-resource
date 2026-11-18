# 建模一把左轮手枪（classic western revolver）
# 坐标系: 枪管沿 Y 轴(枪口朝 -Y), 握把在 +Y 后方朝下, Z 向上。
# 单位: 米。以真实 Colt SAA 尺寸近似缩放。
import bpy
import os

BLEND = r"D:\Game materials.library\blender\revolver\revolver.blend"
PREVIEW = r"D:\Game materials.library\blender\revolver\preview_round1.png"
DONE = r"D:\Game materials.library\blender\revolver\done_round1.flag"

bpy.ops.wm.read_factory_settings(use_empty=True)

# ---------- 材质 ----------
def make_mat(name, color, rough=0.35, metallic=1.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = rough
    return m

mat_steel = make_mat("Steel",      (0.62, 0.64, 0.68, 1.0), rough=0.30, metallic=1.0)
mat_dark  = make_mat("DarkSteel",  (0.08, 0.08, 0.09, 1.0), rough=0.45, metallic=1.0)
mat_wood  = make_mat("Wood",       (0.30, 0.13, 0.05, 1.0), rough=0.55, metallic=0.0)
mat_brass = make_mat("Brass",      (0.75, 0.55,  instruct>0.22, 1.0), rough=0.35, metallic=1.0)

def assign(obj, mat):
    obj.data.materials.clear()
    obj.data.materials.append(mat)

AZ = 0.10  # 转轮中心高度(z)

objs = []  # 收集所有部件

def new_cyl(name, radius, depth, loc, rot=(1.5707963, 0, 0), verts=32):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=radius, depth=depth,
                                        location=loc, rotation=rot)
    o = bpy.context.active_object
    o.name = name
    objs.append(o)
    return o

def new_cube(name, size, loc, scale):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(scale=True)
    objs.append(o)
    return o

# ---------- 枪管总成 ----------
barrel = new_cyl("Barrel", 0.011, 0.14, (0, -0.145, AZ))
bpy.ops.object.shade_smooth()

barrel_shroud = new_cyl("BarrelShroud", 0.020, 0.030, (0, -0.062, AZ))
# 锥形收口: 上端(靠弹巢)粗, 前端细 -> 手动缩放两端
bpy.ops.object.mode_set(mode='EDIT')
bm = None
me = barrel_shroud.data
# 用简单方式: 对Y两端loop缩放
import bmesh
bm = bmesh.new()
bm.from_mesh(me)
for v in bm.verts:
    if v.co.y < -0.077:  # 前端
        pass
bm.free()
bpy.ops.object.mode_set(mode='OBJECT')

bore = new_cyl("Bore", 0.006, 0.004, (0, -0.2155, AZ))
assign(bore, mat_dark)

rib = new_cube("TopRib", 1, (0, -0.145, AZ + 0.0125), (0.008, 0.135, 0.004))
bpy.ops.object.modifier_add(type='BEVEL')
rib.modifiers["Bevel"].width = 0.0012
rib.modifiers["Bevel"].segments = 2

# 准星 (枪口端顶部小片)
front_sight = new_cube("FrontSight", 1, (0, -0.205, AZ + 0.019), (0.003, 0.012, 0.006))
bpy.ops.object.modifier_add(type='BEVEL')
front_sight.modifiers["Bevel"].width = 0.0008
front_sight.modifiers["Bevel"].segments = 2

# ---------- 弹巢 (转轮) ----------
cyl = new_cyl("Cylinder", 0.026, 0.052, (0, 0.005, AZ), verts=64)
bpy.ops.object.shade_smooth()

# 弹巢表面凹槽(6条长凹槽,经典 SAA 造型)
import math
for i in range(6):
    ang = i * math.pi / 3 + math.pi / 6
    dx, dz = math.sin(ang), math.cos(ang)
    # 凹槽用细长 box 嵌入圆柱面
    g = new_cube(f"Flute_{i}", 1,
                 (dx * 0.0255, 0.005, AZ + dz * 0.0255),
                 (0.006, 0.036, 0.010))
    bpy.ops.object.modifier_add(type='BEVEL')
    g.modifiers["Bevel"].width = 0.0015
    g.modifiers["Bevel"].segments = 2
    g.rotation_euler = (0, 0, 0)
    g.rotation_mode = 'XYZ'
    g.rotation_euler = (0, -math.atan2(dx, dz), 0)
    # 绕Y轴(弹巢轴向)分布的凹槽需要绕弹巢轴旋转: 弹巢轴是Y
    g.rotation_euler = (math.atan2(dx, dz), 0, 0)
    g.rotation_euler = (0, 0, 0)
    # 正确做法: 先绕 X? 弹巢轴向为 Y, 凹槽分布绕 Y 轴, 每条凹槽自身长边沿 Y
    g.rotation_euler = (0, 0, 0)
    # 设定旋转: 绕Y轴角度 ang
    g.rotation_euler = (0, ang, 0)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

# 弹巢后端凸缘
rear_lug = new_cyl("RearLug", 0.024, 0.008, (0, 0.035, AZ))
# 弹巢前端锥形
front_cone = new_cyl("FrontCone", 0.026, 0.008, (0, -0.021, AZ))

# 弹巢圆周上的6个弹膛口(前端面小圆孔)
for i in range(6):
    ang = i * math.pi / 3
    r_ch = 0.0155
    dx, dz = math.cos(ang) * r_ch, math.sin(ang) * r_ch
    h = new_cyl(f"ChamberMouth_{i}", 0.004, 0.003,
                (dx, -0.0205, AZ + dz), rot=(1.5707963, 0, 0), verts=16)
    assign(h, mat_dark)

# ---------- 框架: 上梁 + 下护弓 + 中部支柱 ----------
# 上梁(顶部连接枪管与击锤区的横梁)
top_strap = new_cube("TopStrap", 1, (0, -0.045, AZ + 0.0265), (0.012, 0.19, 0.005))
bpy.ops.object.modifier_add(type='BEVEL')
top_strap.modifiers["Bevel"].width = 0.0012
top_strap.modifiers["Bevel"].posts = 2
top_strap.modifiers["Bevel"].posts = 2
top_strap.modifiers["Bevel"].posts = 2
top_strap.modifiers["Bevel"].posts = 2
top_strap.modifiers["StrapBevel"].posts = 2  # 防错占位
