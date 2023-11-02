import bpy
from ..common import utils

from bpy.types import Operator


def loadLayerCamera(layer, context):
    cam = bpy.data.objects.get(layer.name)
    if cam is not None:
        context.scene.camera = cam
    area = next(
        area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')
    if area.spaces[0].region_3d.view_perspective != 'CAMERA':
        bpy.ops.view3d.view_camera()
        #bpy.ops.view3d.view_center_camera()
    #area.spaces[0].region_3d.view_perspective = 'CAMERA'


def loadLayer(layer, context):
    loadLayerCamera(layer, context)
    render = bpy.context.scene.render
    render.resolution_x = layer.ResolutionX
    render.resolution_y = layer.ResolutionY
    render.resolution_percentage = layer.ResolutionPercentage
    render.pixel_aspect_x = layer.AspectX
    render.pixel_aspect_y = layer.AspectY


def saveLayerCamera(layer, context):
    cam = bpy.data.objects.get(layer.name)
    if not cam: return
    area = next(
        area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')
    if area.spaces[0].region_3d.view_perspective == 'CAMERA':
        if context.scene.camera.name == cam.name:
            pass
        else:
            cam.data = context.scene.camera.data.copy()
            cam.location = context.scene.camera.location
            cam.rotation_euler = context.scene.camera.rotation_euler
            cam.scale = context.scene.camera.scale
        return
    area.spaces[0].region_3d.view_perspective = 'PERSP'

    context.scene.camera = cam
    if bpy.ops.view3d.camera_to_view():
        bpy.ops.view3d.camera_to_view.poll()
    else:
        raise ("can not save Camera")


def saveLayer(layer, context):
    saveLayerCamera(layer, context)
    render = bpy.context.scene.render
    layer.ResolutionX = render.resolution_x
    layer.ResolutionY = render.resolution_y
    layer.ResolutionPercentage = render.resolution_percentage
    layer.AspectX = render.pixel_aspect_x
    layer.AspectY = render.pixel_aspect_y

def getProp(context):
    return context.scene.cp_prop

def selectingLayer(context):
    prop = getProp(context)
    layers = prop.layers
    layer_index = prop.layers_index
    return len(layers) > layer_index > -1


def getLayer(context):
    prop = getProp(context)
    layers = prop.layers
    layer_index = prop.layers_index
    return layers[layer_index]


class LoadLayer(Operator):
    bl_idname = "pde.load_layer"
    bl_label = "Load Layer"
    bl_description = "Load the currently selected item"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return selectingLayer(context)

    def execute(self, context):
        loadLayer(getLayer(context), context)
        return {"FINISHED"}


class UpdateLayer(Operator):
    bl_idname = "pde.update_layer"
    bl_label = "Update Layer"
    bl_description = "Update the currently selected item"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return selectingLayer(context)

    def execute(self, context):
        saveLayer(getLayer(context), context)
        return {"FINISHED"}


class RemoveLayer(Operator):
    bl_idname = "pde.remove_layer"
    bl_label = "Remove Layer"
    bl_description = "Remove the currently selected item"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return selectingLayer(context)

    def execute(self, context):
        prop = getProp(context)
        layers = prop.layers
        layer = getLayer(context)
        idx = prop.layers_index

        cam = bpy.data.objects.get(layer.name)
        if cam is not None:
            bpy.data.objects.remove(cam, do_unlink=True)
        for i in layer.renderResults:
            if i.image:
                bpy.data.images.remove(i.image)
        # Remove layer
        layers.remove(idx)

        if idx == len(layers):
            prop.layers_index = len(layers)-1
        return {"FINISHED"}


class AddLayer(Operator):
    bl_idname = "pde.add_layer"
    bl_label = "Add Layer"
    bl_description = "Custom Layer allows..."
    bl_options = {'UNDO'}

    def execute(self, context):
        cp_prop = getProp(context)
        layer = cp_prop.layers.add()
        layer.name = utils.make_layer_label(cp_prop.layers, "cp")

        cam = bpy.data.cameras.new(layer.name)
        cam_obj = bpy.data.objects.new(layer.name, cam)

        coll = utils.getCollection()
        coll.objects.link(cam_obj)
        saveLayer(layer, context)
        # layer.preview = bpy.data.images['qqq.png']
        # context.view_layer.update()
        cp_prop.layers_index = len(cp_prop.layers)-1
        return {"FINISHED"}

class SetPreview(Operator):
    bl_idname = "pde.set_render_result_as_preview"
    bl_label = "set render result as preview"
    bl_description = "Set render result as preview"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return selectingLayer(context) and getLayer(context).renderResultSelected

    def execute(self, context):
        layer = getLayer(context)
        layer.preview = layer.renderResultSelected
        return {"FINISHED"}

class RemoveRenderResult(Operator):
    bl_idname = "pde.remove_render_result"
    bl_label = "Remove Render Result"
    bl_description = "Remove this Render Result selected"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return selectingLayer(context) and getLayer(context).renderResultSelected

    def execute(self, context):
        layer = getLayer(context)
        image = layer.renderResultSelected
        
        for i in range(len(layer.renderResults)):
            if layer.renderResults[i].image == image:
                layer.renderResults.remove(i)
                break
        bpy.data.images.remove(image)
        if i > 0:
            layer.renderResultSelected = layer.renderResults[i-1].image
        elif i==0 and len(layer.renderResults)>0:
            layer.renderResultSelected = layer.renderResults[0].image
        else:
            layer.renderResultSelected = None
        if layer.renderResultSelected:
            layer.renderResultsEnum = layer.renderResultSelected.name
        #layer.preview = layer.renderResultSelected
        return {"FINISHED"}
