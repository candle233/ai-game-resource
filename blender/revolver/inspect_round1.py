import bpy

for o in bpy.data.objects:
    if o.type == 'MESH':
        print(f"OBJ {o.name:20s} verts={len(o.data.vertices):6d} dims=({o.dimensions.x:.4f},{o.dimensions.y:.4f},{o.dimensions.z:.4f}) loc=({o.location.x:.4f},{o.location.y:.4f},{o.location.z:.4f})")
    else:
        print(f"OBJ {o.name:20s} type={o.type}")
cyl = bpy.data.objects.get("Cylinder")
if cyl:
    me = cyl.data
    zs = [v.co.z for v in me.vertices]
    ys = [v.co.y for v in me.vertices]
    print(f"CYLINDER: z range {min(zs):.4f}..{max(zs):.4f}, y range {min(ys):.4f}..{max(ys):.4f}, polys={len(me.polygons)}")
