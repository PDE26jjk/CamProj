import bpy
import bmesh
from mathutils import Vector
# bpy.ops.object.editmode_toggle()
# mesh = bpy.data.meshes.new(name="MyMesh")
# print(mesh)
# bpy.data.meshes.remove(mesh)
#print(list(bpy.data.meshes))

# bpy.context.object["MyOwnProperty"] = 42
# print(bpy.context.object["MyOwnProperty"])
# print(bpy.context.selected_objects)
# print(bpy.context.active_object)
# print(bpy.context.object)

#bpy.ops.mesh.hide(unselected=False) 
# bpy.ops.view3d.render_border()
# bpy.data.objects["Cube"].data.vertices[0].co.x += 1.0
#bpy.context.object["MyOwnProperty"] = 42
#print(bpy.context.object["MyOwnProperty"])
#print(bpy.data.objects)
#bpy.context.active_object.modifiers["Subdivision"].levels = 3
# __import__('code').interact(local=dict(globals(), **locals()))
# import sys
# print(sys.version)
# mesh = bpy.context.active_object.data
# bm = bmesh.from_edit_mesh(mesh)

# print(mesh.polygons)
# print(mesh.loop_triangles)
# print(bm.faces)

# print(mesh.vertex_colors.active)
# print(bpy.context.object.data.edit_bones)
# print(len(bpy.context.selected_editable_bones))
#print(bpy.context.object.pose.bones)
C = bpy.context
T = bpy.types

# print(C.area.type)
# print(C.active_object)

mesh:T.Mesh = C.active_object.data 

# print(mesh.color_attributes.active.data)
bm = bmesh.new()
bm.from_mesh(mesh)
uv_lay = bm.loops.layers.uv.active
# print(len(bm.faces))
# bm.normal_update()
# print(bm.loops.layers.uv.items())
# print(bm.loops.layers.color.items())
# print(bm.verts.layers.float_color.items())
# print(bm.verts.layers.float.items())
# print(bm.loops.layers.float.items())
# print(bm.loops.layers.float_color.items())
# print(bm.loops.layers.float_vector.items())
# mesh.calc_normals_split()
# print(mesh.tangents)
# for loop in mesh.loops:
#     loop.normal = 0,1,0
#     loop.tangent = 1,0,0
colInd = bm.loops.layers.color.active
if not colInd:
    colInd = bm.loops.layers.color.new('Col')
for face in bm.faces:
    for loop in face.loops:
        normal = loop.vert.normal
        normal = Vector((-normal.x,normal.z,-normal.y)).normalized()
        normal.x = (normal.x + 1)*0.5
        normal.y = (normal.y + 1)*0.5
        normal.z = (normal.z + 1)*0.5
        loop[colInd] = Vector((*normal,1))
bm.to_mesh(mesh)    