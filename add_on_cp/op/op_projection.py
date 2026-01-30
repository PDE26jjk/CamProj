import bpy

from bpy.types import Operator

from ..common.console import console_print
from ..common.utils import isPHILOGIXexist, make_images_label, pasteClipboard

from .op_cameraPosition import getLayer, getProp, selectingLayer


class PasteTexture(Operator):
    bl_idname = "pde.paste_texture"
    bl_label = "paste texture"
    bl_description = "paste texture from clipboard"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return selectingLayer(context)

    def execute(self, context):
        layer = getLayer(context)
        img = pasteClipboard()
        if img:
            img.name = make_images_label(
                layer.textureSet, f"{layer.name} texture")
            img.pack()
            tex = layer.textureSet.add()
            tex.image = img
            layer.texturesEnum = img.name
        return {"FINISHED"}


class AddTexture(Operator):
    bl_idname = "pde.add_to_texture"
    bl_label = "Add to texture"
    bl_description = "Add selected image to texture set"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return selectingLayer(context) and getProp(context).texture_preview

    def execute(self, context):
        prop = getProp(context)
        layer = getLayer(context)
        img = prop.texture_preview
        img.pack()
        tex = layer.textureSet.add()
        tex.image = img
        layer.texturesEnum = img.name
        return {"FINISHED"}


def getPLXmatProps(context):
    obj = context.active_object
    mat = obj.active_material
    prop = getProp(context)
    if hasattr(mat, 'PlxProps'):
        # fine for plx 4.0
        mat_props = mat.PlxProps
        try:
            prop.plxVersion = 4
        except:
            pass
    elif hasattr(mat, 'PlxMatProps'):
        mat_props = mat.PlxMatProps
        try:
            prop.plxVersion = 3
        except:
            pass
    return mat_props


def getPLXmatLayer(context):
    mat_props = getPLXmatProps(context)
    if getProp(context).plxVersion == 3:
        return mat_props.Layers[mat_props.Layers_index]
    return mat_props.layers[mat_props.layers_index]


def getPLXActiveMatNodeGroup(context):
    mat_layer = getPLXmatLayer(context)
    if getProp(context).plxVersion == 3:
        return mat_layer

    layer_node = mat_layer.id_data.node_tree.nodes.get(mat_layer.ID)
    # for i in range
    # return layer_node.node_tree
    return layer_node.node_tree


def projectMap(layer, img):
    scene = bpy.context.scene
    camera = bpy.data.objects[layer.name]
    # print(camera.location)
    camera.scale = (1, 1, 1)
    # right, up, back =camera.matrix_world.to_3x3().transposed() # type: ignore
    # print(up)

    render = scene.render
    matrix_world = camera.matrix_world.copy().transposed()
    offset = -(matrix_world @ matrix_world[3])
    matrix_world[3] = (0, 0, 0, 1)
    matrix_world[0][3] = offset[0]
    matrix_world[1][3] = offset[1]
    matrix_world[2][3] = offset[2]

    # matrix_world = matrix_world.transpose()
    projection_mat = camera.calc_matrix_camera(
        bpy.context.evaluated_depsgraph_get(),
        x=int(layer.ResolutionX * (layer.ResolutionPercentage / 100)),
        y=int(layer.ResolutionY * (layer.ResolutionPercentage / 100)),
        scale_x=layer.AspectX,
        scale_y=layer.AspectY
    )
    pv = projection_mat @ matrix_world

    nodeGroup = bpy.context.space_data.edit_tree
    tree = nodeGroup
    nodes = tree.nodes
    links = tree.links

    if nodeGroup.inputs.get('Color'):
        nodeGroup.inputs.remove(nodeGroup.inputs['Color'])
    f1 = nodeGroup.inputs.new("NodeSocketFloatFactor", "FloatFactor")
    f1.name = "Clamp"
    f1.min_value = 0
    f1.default_value = 0
    f1.max_value = 1

    f2 = nodeGroup.inputs.new("NodeSocketFloatFactor", "FloatFactor")
    f2.name = "Hard edge"
    f2.min_value = 0
    f2.default_value = 0.5
    f2.max_value = 1

    for n in nodes:
        nodes.remove(n)

    locX, locY = 0, 0

    GroupInput = tree.nodes.new("NodeGroupInput")
    GroupInput.location = (locX, locY - 300)
    f1 = GroupInput.outputs[f1.name]
    f2 = GroupInput.outputs[f2.name]

    GeometryInfo = tree.nodes.new("ShaderNodeNewGeometry")
    GeometryInfo.location = (locX, locY)

    locX += 200
    DX = tree.nodes.new("ShaderNodeVectorMath")
    DX.operation = 'DOT_PRODUCT'
    DX.location = (locX, locY)
    DX.hide = True
    DX.inputs[0].default_value = pv[0][:-1]

    locY -= 50
    DY = tree.nodes.new("ShaderNodeVectorMath")
    DY.operation = 'DOT_PRODUCT'
    DY.location = (locX, locY)
    DY.hide = True
    DY.inputs[0].default_value = pv[1][:-1]

    locY -= 50
    DZ = tree.nodes.new("ShaderNodeVectorMath")
    DZ.operation = 'DOT_PRODUCT'
    DZ.location = (locX, locY)
    DZ.hide = True
    DZ.inputs[0].default_value = pv[2][:-1]

    locY -= 50
    DW = tree.nodes.new("ShaderNodeVectorMath")
    DW.operation = 'DOT_PRODUCT'
    DW.location = (locX, locY)
    DW.hide = True
    DW.inputs[0].default_value = pv[3][:-1]

    locY -= 50
    DN = tree.nodes.new("ShaderNodeVectorMath")
    DN.operation = 'DOT_PRODUCT'
    DN.location = (locX, locY)
    DN.hide = True
    DN.inputs[0].default_value = (-pv[2])[:-1]

    links.new(GeometryInfo.outputs['Position'], DX.inputs[1])
    links.new(GeometryInfo.outputs['Position'], DY.inputs[1])
    links.new(GeometryInfo.outputs['Position'], DZ.inputs[1])
    links.new(GeometryInfo.outputs['Position'], DW.inputs[1])
    links.new(GeometryInfo.outputs['Normal'], DN.inputs[1])

    locY = 0
    locX += 200
    CombineXYZ = tree.nodes.new("ShaderNodeCombineXYZ")
    CombineXYZ.location = (locX, locY)
    CombineXYZ.hide = True

    links.new(DX.outputs['Value'], CombineXYZ.inputs[0])
    links.new(DY.outputs['Value'], CombineXYZ.inputs[1])
    links.new(DZ.outputs['Value'], CombineXYZ.inputs[2])

    locX += 200
    M1 = tree.nodes.new("ShaderNodeVectorMath")
    M1.operation = 'ADD'
    M1.location = (locX, locY)
    M1.hide = True
    M1.inputs[0].default_value = (pv[0][3], pv[1][3], pv[2][3])
    links.new(CombineXYZ.outputs[0], M1.inputs[1])

    locY -= 50
    M2 = tree.nodes.new("ShaderNodeMath")
    M2.operation = 'ADD'
    M2.location = (locX, locY)
    M2.hide = True
    M2.inputs[0].default_value = pv[3][3]
    links.new(DW.outputs['Value'], M2.inputs[1])
    locY = 0

    locX += 200
    M3 = tree.nodes.new("ShaderNodeVectorMath")
    M3.operation = 'DIVIDE'
    M3.location = (locX, locY)
    M3.hide = True
    links.new(M1.outputs['Vector'], M3.inputs[0])
    links.new(M2.outputs['Value'], M3.inputs[1])

    locX += 200
    M4 = tree.nodes.new("ShaderNodeVectorMath")
    M4.operation = 'MULTIPLY_ADD'
    M4.inputs[1].default_value = (0.5, 0.5, 1)
    M4.inputs[2].default_value = (0.5, 0.5, 0)
    M4.location = (locX, locY)
    M4.hide = True
    links.new(M3.outputs['Vector'], M4.inputs[0])

    locX += 200
    Tex = tree.nodes.new("ShaderNodeTexImage")
    Tex.location = (locX, locY)
    Tex.image = img
    Tex.width = GeometryInfo.width
    Tex.extension = "CLIP"
    links.new(M4.outputs['Vector'], Tex.inputs[0])

    locY -= 300
    Ramp = tree.nodes.new("ShaderNodeValToRGB")
    Ramp.color_ramp.interpolation = 'B_SPLINE'
    Ramp.color_ramp.elements[0].position = 0.123867
    Ramp.color_ramp.elements[1].position = 0.664652
    Ramp.color_ramp.elements.new(0.442598).color = (0.004, 0.004, 0.004, 1)
    Ramp.location = (locX, locY)

    locX -= 200
    MapRange = tree.nodes.new("ShaderNodeMapRange")
    MapRange.location = (locX, locY)
    links.new(MapRange.outputs[0], Ramp.inputs[0])
    links.new(DN.outputs['Value'], MapRange.inputs[0])
    links.new(f1, MapRange.inputs[1])

    locX -= 200
    PowNode = tree.nodes.new("ShaderNodeMath")
    PowNode.operation = 'POWER'
    PowNode.location = (locX, locY)
    PowNode.inputs[0].default_value = 15.0
    links.new(f2, PowNode.inputs[1])
    links.new(PowNode.outputs[0], MapRange.inputs[4])

    locY = 0

    locX += 600
    locY -= 50
    M5 = tree.nodes.new("ShaderNodeMath")
    M5.operation = 'MULTIPLY'
    M5.location = (locX, locY)
    M5.hide = True
    links.new(Tex.outputs[1], M5.inputs[0])
    links.new(Ramp.outputs['Color'], M5.inputs[1])

    locX += 200
    locY += 20

    GroupOutput = tree.nodes.new("NodeGroupOutput")
    GroupOutput.location = (locX, locY)
    if GroupOutput.inputs.get('Color'):
        links.new(Tex.outputs[0], GroupOutput.inputs['Color'])
    elif GroupOutput.inputs.get('Base Color'):
        links.new(Tex.outputs[0], GroupOutput.inputs['Base Color'])
    elif GroupOutput.inputs.get('Base Color/Diffuse'):
        links.new(Tex.outputs[0], GroupOutput.inputs['Base Color/Diffuse'])

    if GroupOutput.inputs.get('Alpha'):
        links.new(M5.outputs[0], GroupOutput.inputs['Alpha'])
    if GroupOutput.inputs.get('Fac'):
        links.new(M5.outputs[0], GroupOutput.inputs['Fac'])
    if GroupOutput.inputs.get('Layer Mask'):
        links.new(M5.outputs[0], GroupOutput.inputs['Layer Mask'])


class CreateSmartMaterial(Operator):
    bl_idname = "pde.create_plx_smart_material"
    bl_label = "create plx smart material"
    bl_description = "Create plx smart material from texture"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        if isPHILOGIXexist() and selectingLayer(context) and getLayer(context).textureSelected:
            return bpy.ops.plx.remove_shader.poll() and bpy.ops.plx.add_smart.poll()
        return False

    def execute(self, context):
        layer = getLayer(context)
        img = layer.textureSelected

        bpy.ops.plx.add_smart()
        matNodeGroup = getPLXActiveMatNodeGroup(context)
        if getProp(context).plxVersion == 4:
            matNodeGroup.PlxProps.name = img.name
            value_node = matNodeGroup.nodes.get('Value')
        else:
            node_tree = matNodeGroup.id_data.node_tree
            value_node = node_tree.nodes[f"{matNodeGroup.name}$.Value"]
            frame_node = node_tree.nodes[f"{matNodeGroup.name}$.Frame"]
            frame_node.label = img.name

        group_name = value_node.node_tree.name

        area = bpy.context.area
        old_type = area.type
        if getProp(context).plxVersion == 4:
            bpy.ops.plx.open_group(group_name=group_name)
        else:
            bpy.ops.plx.open_group(node_name=group_name)
        # in shader nodes editor
        projectMap(layer, img)

        area.type = old_type
        return {"FINISHED"}


class CreateSurfaceLayer(Operator):
    bl_idname = "pde.create_plx_surface_layer"
    bl_label = "create plx surface layer"
    bl_description = "Create plx smart material from texture"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        if isPHILOGIXexist() and selectingLayer(context) and getLayer(context).textureSelected and \
                bpy.ops.plx.remove_shader.poll() and bpy.ops.plx.remove_layer.poll():
            # does not work.
            # return bpy.ops.plx.add_surface.poll()
            try:
                nodeGroup = getPLXActiveMatNodeGroup(context)
                if getProp(context).plxVersion == 4:
                    return nodeGroup.PlxProps.layer_type == 'CUSTOM'
                else:
                    return nodeGroup.type == 'CUSTOM'
            except Exception as e:
                print(e)
                return False
        return False

    def execute(self, context):
        layer = getLayer(context)
        img = layer.textureSelected

        bpy.ops.plx.add_surface()

        mat_layer = getPLXmatLayer(context)

        if getProp(context).plxVersion == 3:
            mat_props = getPLXmatProps(context)
            edit_maps = mat_props.edit_maps
            channel_name = "$.".join((edit_maps, mat_layer.name))
            channel = mat_layer.channels[channel_name]
            channel_layer = channel.Layers[channel.Layers_index]

            mat = channel_layer.id_data
            nodes_name = '$.'.join(channel_layer.name.split('$.')[1:])
            node_tree = mat.node_tree.nodes[nodes_name].node_tree

            item_nodes = node_tree.nodes
            value_node = item_nodes[f"{channel_layer.name}$.Value"]
            frame_node = item_nodes[f"{channel_layer.name}$.Frame"]
            frame_node.label = img.name

        if getProp(context).plxVersion == 4:
            mat_props = mat_layer.id_data.PlxProps
            matNodeGroup = getPLXActiveMatNodeGroup(context)

            channel_node_group = matNodeGroup.nodes.get(mat_props.edit_maps).node_tree
            channel_props = channel_node_group.PlxProps
            channel_layers = channel_props.channel_layers
            channel_layer = channel_layers[channel_props.channel_layers_index]
            layer_node = channel_layer.id_data.nodes.get(channel_layer.ID)

            surfaceNodeGroup = layer_node.node_tree
            surfaceNodeGroup.PlxProps.name = img.name
            value_node = surfaceNodeGroup.nodes.get('Value')

        group_name = value_node.node_tree.name
        # print(value_node)

        area = bpy.context.area
        old_type = area.type

        if getProp(context).plxVersion == 4:
            bpy.ops.plx.open_group(group_name=group_name)
        else:
            bpy.ops.plx.open_group(node_name=group_name)
        # in shader nodes editor
        projectMap(layer, img)

        area.type = old_type
        return {"FINISHED"}


class RemoveTexture(Operator):
    bl_idname = "pde.remove_texture"
    bl_label = "Remove Texture"
    bl_description = "Remove this texture from texture set (not delete it)"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return selectingLayer(context) and getLayer(context).textureSelected

    def execute(self, context):
        layer = getLayer(context)
        image = layer.textureSelected

        for i in range(len(layer.textureSet)):
            if layer.textureSet[i].image == image:
                layer.textureSet.remove(i)
                break
        # bpy.data.images.remove(image)
        if i > 0:
            layer.textureSelected = layer.textureSet[i - 1].image
        elif i == 0 and len(layer.textureSet) > 0:
            layer.textureSelected = layer.textureSet[0].image
        else:
            layer.textureSelected = None
        if layer.textureSelected:
            layer.texturesEnum = layer.textureSelected.name

        return {"FINISHED"}


def view3d_find():
    area = next(area for area in bpy.context.screen.areas if area.type == 'VIEW_3D')
    if not area:
        return None, None
    v3d = area.spaces[0]
    rv3d = v3d.region_3d
    for region in area.regions:
        if region.type == 'WINDOW':
            return region, rv3d


def alignStencil():
    # https://blender.stackexchange.com/questions/6377/coordinates-of-corners-of-camera-view-border
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

    dimension = (frame_px[0] - frame_px[2]) * 0.5
    position = (frame_px[0] + frame_px[2]) * 0.5
    prop = getProp(bpy.context)
    position.x += prop.offsetAlignX
    position.y += prop.offsetAlignY

    bpy.ops.brush.stencil_reset_transform()
    brush = bpy.context.tool_settings.image_paint.brush
    brush.stencil_pos = position
    brush.stencil_dimension = dimension


class AlignStencil(Operator):
    bl_idname = "pde.align_stencil"
    bl_label = "align stencil"
    bl_description = "Align texture stencil to camera frame, \nneed to in camera view and have texture stencil"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        region, rv3d = view3d_find()
        return bpy.ops.brush.stencil_reset_transform.poll() and rv3d and rv3d.view_perspective == 'CAMERA'

    def execute(self, context):
        alignStencil()
        return {"FINISHED"}


def getProjectionTexture():
    name = "CamProj Projection Texture"
    if not bpy.data.textures.get(name):
        bpy.data.textures.new(name, 'IMAGE')
    tex = bpy.data.textures[name]
    return tex


def getProjectionBrush():
    name = "CamProj Projection Brush"
    if not bpy.data.brushes.get(name):
        bpy.data.brushes.new(name, mode='TEXTURE_PAINT').asset_mark()
    brush = bpy.data.brushes[name]
    return brush


class ApplyTexture(Operator):
    bl_idname = "pde.apply_texture"
    bl_label = "Apply Texture"
    bl_description = "Apply image as texture to brush,\n create texture if not exist"
    bl_options = {'UNDO'}

    @classmethod
    def poll(cls, context):
        return bpy.ops.object.mode_set.poll() and selectingLayer(context) and getLayer(context).textureSelected

    def execute(self, context):
        texture = getProjectionTexture()
        texture.image = getLayer(context).textureSelected

        # brush = bpy.context.tool_settings.image_paint.brush
        brush = getProjectionBrush()
        context.tool_settings.image_paint.brush = brush

        brush.texture_slot.map_mode = "STENCIL"
        # console_print('before', brush.texture)
        brush.texture = texture
        # console_print('after', brush.texture)
        bpy.ops.object.mode_set(mode='TEXTURE_PAINT', toggle=False)
        # alignStencil()
        return {"FINISHED"}
