import bpy
import bmesh
from mathutils import Vector

C = bpy.context
T = bpy.types

# print(C.area.type)
# print(C.active_object)

mesh:T.Mesh = C.active_object.data 

bpy.ops.brush.stencil_reset_transform()


area = None

for a in bpy.context.window.screen.areas:
      if a.type == 'VIEW_3D':
        area = a
# area.spaces[0].region_3d.view_camera_zoom = 600

camera_offset = area.spaces[0].region_3d.view_camera_offset

brush = bpy.data.brushes["Basic Brush"]
brush.stencil_pos = (90,90)

brush.stencil_dimension = (100,2)


print(camera_offset[0],camera_offset[1])
view_camera_zoom = area.spaces[0].region_3d.view_camera_zoom
scale = 0.0002*view_camera_zoom**2 + 0.0285*view_camera_zoom + 0.9941
print(scale)
print(area.width * camera_offset[0])
brush.stencil_pos = (area.width *(0.5-camera_offset[0]*0) ,(area.height) * (0.5-camera_offset[1]*90))

# -30 : 0.330
# 0: 1
# 100: 5.83
# 200: 14.65
# area.spaces[0].region_3d.view_camera_offset = 0,0
import numpy as np

v = np.array((0,0,1000,1))

pmat = np.matrix(area.spaces[0].region_3d.perspective_matrix)
wmat = np.matrix(area.spaces[0].region_3d.window_matrix)
print(wmat)
v2 =  v@wmat
print(v2 / v2[0,3])
import bgl

space = area.spaces[0]
print(space.render_border_min_x)
print(space.render_border_max_x)
print(space.render_border_min_y)
print(space.render_border_max_y)
print(space.overlay)

for a in bpy.context.screen.areas:
    if a.type == 'VIEW_3D':
        for r in a.regions:
            if r.type == 'WINDOW':
                print(f"Viewport dimensions: {r.width}x{r.height}")
print(area.height)
# ???????????????????????????????

# https://blender.stackexchange.com/questions/6377/coordinates-of-corners-of-camera-view-border
def view3d_find():
    # returns first 3d view, normally we get from context
    for area in bpy.context.window.screen.areas:
        if area.type == 'VIEW_3D':
            v3d = area.spaces[0]
            rv3d = v3d.region_3d
            for region in area.regions:
                if region.type == 'WINDOW':
                    return region, rv3d
    return None, None

def view3d_camera_border(scene):
    obj = scene.camera
    cam = obj.data

    frame = cam.view_frame(scene=scene)

    # move from object-space into world-space 
    frame = [obj.matrix_world @ v for v in frame]

    # move into pixelspace
    from bpy_extras.view3d_utils import location_3d_to_region_2d
    region, rv3d = view3d_find()
    frame_px = [location_3d_to_region_2d(region, rv3d, v) for v in frame]
    return frame_px

frame_px = view3d_camera_border(bpy.context.scene)
print("Camera frame:", frame_px)

(frame_px[0] + frame_px[2]) * 0.5

dimension = (frame_px[0] - frame_px[2]) * 0.5
pos = (frame_px[0]+ frame_px[1]) * 0.5 
pos.x -= dimension.x
brush.stencil_pos = pos

brush.stencil_dimension = dimension

print(bpy.ops.brush.stencil_reset_transform.poll())
print(dimension,pos)