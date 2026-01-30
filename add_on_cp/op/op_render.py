import bpy

from bpy.types import Operator

from ..common.utils import copy2Clipboard, make_images_label
from bpy.props import PointerProperty, StringProperty
from .op_cameraPosition import getLayer, selectingLayer

import numpy as np


def renderMaterial(imageName, context):
    scene = context.scene
    scene.render.use_compositing = True
    scene.use_nodes = True
    tree = context.scene.node_tree
    links = tree.links

    render_layers_node = tree.nodes.new(type="CompositorNodeRLayers")
    render_layers_node.location = 0, 0

    # Create a node for outputting the surface normals of each pixel
    loc_x = 400
    loc_y = 0

    gamma_node = tree.nodes.new('CompositorNodeGamma')
    gamma_node.location = (loc_x, loc_y)
    gamma_node.inputs[1].default_value = 0.45454

    loc_x += 200
    loc_y -= 100
    vl = tree.nodes.new('CompositorNodeViewer')
    vl.location = (loc_x, loc_y)
    tree.nodes.active = vl

    links.new(render_layers_node.outputs['Image'], gamma_node.inputs[0])
    links.new(gamma_node.outputs['Image'], vl.inputs[0])
    links.new(render_layers_node.outputs['Alpha'], vl.inputs['Alpha'])

    bpy.ops.render.render()

    # read render result pixels
    # https://ammous88.wordpress.com/2015/01/16/blender-access-render-results-pixels-directly-from-python-2/
    vnImage = bpy.data.images['Viewer Node']

    tex = bpy.data.images.new(
        imageName, width=vnImage.size[0], height=vnImage.size[1])
    tex.pixels = vnImage.pixels[:]
    tex.update()
    tex.pack()

    tree.nodes.remove(render_layers_node)
    tree.nodes.remove(gamma_node)
    tree.nodes.remove(vl)

    return tex


def renderDepth(imageName, context):
    scene = context.scene
    scene.render.use_compositing = True
    scene.use_nodes = True
    tree = context.scene.node_tree
    links = tree.links

    # Configure renderer to record depth
    scene.view_layers["ViewLayer"].use_pass_z = True

    render_layers_node = tree.nodes.new(type="CompositorNodeRLayers")
    render_layers_node.location = 0, 0

    loc_x = 400
    loc_y = -300

    normalize_node = tree.nodes.new("CompositorNodeNormalize")
    normalize_node.location = (loc_x, loc_y)

    loc_x += 200
    oneMinus = tree.nodes.new('CompositorNodeMath')
    oneMinus.operation = "SUBTRACT"
    oneMinus.location = (loc_x, loc_y)
    oneMinus.inputs[0].default_value = 1.0

    loc_x += 200
    vl = tree.nodes.new('CompositorNodeViewer')
    vl.location = (loc_x, loc_y)

    links.new(render_layers_node.outputs['Depth'], normalize_node.inputs[0])
    links.new(normalize_node.outputs[0], oneMinus.inputs[1])
    links.new(oneMinus.outputs[0], vl.inputs[0])
    links.new(render_layers_node.outputs['Alpha'], vl.inputs['Alpha'])

    tree.nodes.active = vl
    bpy.ops.render.render()
    vnImage = bpy.data.images['Viewer Node']

    tex = bpy.data.images.new(
        imageName, width=vnImage.size[0], height=vnImage.size[1])
    tex.pixels = vnImage.pixels[:]
    tex.update()
    tex.pack()

    tree.nodes.remove(render_layers_node)
    tree.nodes.remove(normalize_node)
    tree.nodes.remove(vl)
    tree.nodes.remove(oneMinus)

    return tex


def renderNormal(imageName, context):
    scene = context.scene
    scene.render.use_compositing = True
    scene.use_nodes = True
    tree = context.scene.node_tree
    links = tree.links

    scene.view_layers["ViewLayer"].use_pass_normal = True

    # for n in tree.nodes:
    # tree.nodes.remove(n)

    render_layers_node = tree.nodes.new(type="CompositorNodeRLayers")
    render_layers_node.location = 0, 0

    # Create a node for outputting the surface normals of each pixel
    loc_x = 400
    loc_y = -300

    loc_x += 200
    vl = tree.nodes.new('CompositorNodeViewer')
    vl.location = (loc_x, loc_y)
    tree.nodes.active = vl

    links.new(render_layers_node.outputs['Normal'], vl.inputs[0])
    # links.new(render_layers_node.outputs['Alpha'], vl.inputs['Alpha'])

    bpy.ops.render.render()

    # read render result pixels
    vnImage = bpy.data.images['Viewer Node']
    tex = bpy.data.images.new(
        imageName, width=vnImage.size[0], height=vnImage.size[1])

    # world to view, and pack
    cam = bpy.data.objects[getLayer(context).name]
    w2vmat = cam.matrix_world.to_3x3()
    w2vmat = np.array(w2vmat)

    arr = np.array(vnImage.pixels[:]).reshape((-1, 4))
    arr = arr[:, :-1]  # del A
    arr = arr @ w2vmat
    mask = np.all(arr == 0, axis=1)
    arr[mask] = np.array([0, 0, 1])
    arr = arr * 0.5 + 0.5
    # RGB+A
    arr = np.concatenate((arr, np.expand_dims(
        np.ones(arr.shape[0]), axis=1)), axis=1)

    tex.pixels = arr.flatten()
    tex.update()
    tex.pack()

    tree.nodes.remove(render_layers_node)
    tree.nodes.remove(vl)

    return tex


class RenderImage(Operator):
    bl_idname = "pde.render_image"
    bl_label = "Render Material"
    bl_description = "Render scene with material"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return selectingLayer(context)

    def execute(self, context):
        layer = getLayer(context)

        name = make_images_label(layer.renderResults, layer.name + " render")
        image = renderMaterial(name, context)
        rr = layer.renderResults.add()
        rr.image = image
        layer.renderResultsEnum = rr.image.name
        return {"FINISHED"}


# https://blenderartists.org/t/live-scene-capture-to-texture/1380153
import gpu


class RenderViewport(Operator):
    bl_idname = "pde.render_viewport"
    bl_label = "Render viewport"
    bl_description = "Render 3d viewport"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return selectingLayer(context)

    def execute(self, context):
        layer = getLayer(context)
        x = int(layer.ResolutionX * (layer.ResolutionPercentage / 100))
        y = int(layer.ResolutionY * (layer.ResolutionPercentage / 100))
        cam = bpy.data.objects[layer.name]
        offscreen = gpu.types.GPUOffScreen(x, y)
        vm = cam.matrix_world.inverted()
        pm = cam.calc_matrix_camera(context.evaluated_depsgraph_get(), x=x, y=y)
        offscreen.draw_view3d(context.scene, context.view_layer, context.space_data, context.region, vm, pm,
                              do_color_management=True, draw_background=True)
        gpu.state.depth_mask_set(False)
        buffer = np.array(offscreen.texture_color.read(), dtype='float32').flatten(order='F')
        buffer = np.divide(buffer, 255)
        # gamma
        # buffer = buffer**0.4545

        name = make_images_label(layer.renderResults, layer.name + " render")
        image = bpy.data.images.new(
            name, width=x, height=y)
        image.pixels.foreach_set(buffer)
        image.pack()
        rr = layer.renderResults.add()
        rr.image = image
        layer.renderResultsEnum = rr.image.name
        return {"FINISHED"}


class RenderDepth(Operator):
    bl_idname = "pde.render_depth"
    bl_label = "Render Image"
    bl_description = "Render Image Selected"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return selectingLayer(context)

    def execute(self, context):
        # loadLayer(getLayer(context),context)
        layer = getLayer(context)
        texName = f"{layer.name}_depth"
        oriTex = bpy.data.images.get(texName)
        if oriTex is not None:
            bpy.data.images.remove(oriTex)
        tex = renderDepth(texName, context)
        layer.depthMap = tex

        return {"FINISHED"}


class RenderNormal(Operator):
    bl_idname = "pde.render_normal"
    bl_label = "Render normal"
    bl_description = "Render normal map"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return selectingLayer(context)

    def execute(self, context):
        layer = getLayer(context)
        texName = f"{layer.name}_normal"
        oriTex = bpy.data.images.get(texName)
        if oriTex is not None:
            bpy.data.images.remove(oriTex)
        tex = renderNormal(texName, context)
        layer.normalMap = tex

        return {"FINISHED"}


class ToggleRenderView(Operator):
    bl_idname = "pde.toggle_render_view"
    bl_label = "Toggle Render View"
    bl_description = "toggle render view with selected image"
    bl_options = {'UNDO'}

    imageName: bpy.props.StringProperty()

    def execute(self, context):
        if bpy.data.images.get(self.imageName):
            image = bpy.data.images[self.imageName]
            bpy.ops.render.view_show('INVOKE_DEFAULT')
            print(bpy.context.window.screen)
            print(bpy.context.area)
            area = bpy.context.area
            if bpy.context.window.screen.name != "temp":
                # bpy.context.scene.view_layers.update()
                area = bpy.data.screens['temp'].areas[0]
            area.spaces.active.image = image
        return {"FINISHED"}


class CopyRenderResult(Operator):
    bl_idname = "pde.copy_render_result"
    bl_label = "copy render result"
    bl_description = "copy render result selected"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return selectingLayer(context) and getLayer(context).renderResultSelected

    def execute(self, context):
        layer = getLayer(context)
        copy2Clipboard(layer.renderResultSelected)
        return {"FINISHED"}


class CopyDepth(Operator):
    bl_idname = "pde.copy_depth"
    bl_label = "copy depth"
    bl_description = "copy to Clipboard"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return selectingLayer(context) and getLayer(context).depthMap

    def execute(self, context):
        layer = getLayer(context)
        copy2Clipboard(layer.depthMap)
        return {"FINISHED"}


class CopyNormal(Operator):
    bl_idname = "pde.copy_normal"
    bl_label = "copy depth"
    bl_description = "copy to Clipboard"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return selectingLayer(context) and getLayer(context).normalMap

    def execute(self, context):
        layer = getLayer(context)
        copy2Clipboard(layer.normalMap)
        return {"FINISHED"}
