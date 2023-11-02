bl_info = {
    "name" : "CamProj",
    "author" : "PDE26jjk",
    "description" : "camera position set, with texture projection tools",
    "blender" : (3, 6, 0),
    "version" : (1, 0, 0),
    "location" : "View3D > Sidebar > CamProj",
    "warning" : "",
    "category" : "Camera"
}

import bpy

from bpy.props import PointerProperty
from add_on_cp.op.op_projection import AddTexture, AlignStencil, ApplyTexture, CreateSmartMaterial, CreateSurfaceLayer, PasteTexture, RemoveTexture

from add_on_cp.op.op_render import CopyDepth, CopyNormal, CopyRenderResult, ToggleRenderView, RenderDepth, RenderImage, RenderNormal, RenderViewport
#import sys
#sys.path.append(r"R:\cg\blender\add_on_PDE\sd")

from .ui.ui_cameraPosition import CameraPosition_PT_Info, LayerItems

from .op.op_cameraPosition import AddLayer, LoadLayer, RemoveLayer, RemoveRenderResult, SetPreview, UpdateLayer

from .properties.prop_cameraPosition import CameraPositionProp, CameraPositionType, ImageType


classList = [
    ImageType,CameraPositionType,
    CameraPositionProp,
    LayerItems, AddLayer, RemoveLayer, UpdateLayer,LoadLayer,RenderImage,RenderViewport,RenderDepth,RenderNormal,CopyRenderResult,CopyDepth,CopyNormal,ToggleRenderView,SetPreview,RemoveRenderResult,PasteTexture,AddTexture,RemoveTexture,CreateSmartMaterial,CreateSurfaceLayer,AlignStencil,ApplyTexture,
    
    
    CameraPosition_PT_Info
]


def register():
    for c in classList:
        bpy.utils.register_class(c)
    bpy.types.Scene.cp_prop = PointerProperty(type=CameraPositionProp)


def unregister():
    for c in classList:
        bpy.utils.unregister_class(c)
    del bpy.types.Scene.cp_prop


if __name__ == "__main__":
    register()
     
#unregister()
#register()

