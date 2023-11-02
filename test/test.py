import bpy
import mathutils

def renderNormal(filepath):
    scene = bpy.context.scene
    tree = bpy.context.scene.node_tree
    links = tree.links

    scene.view_layers["ViewLayer"].use_pass_normal = True

    for n in tree.nodes:
        tree.nodes.remove(n)

    render_layers_node = tree.nodes.new(type="CompositorNodeRLayers")
    render_layers_node.location = 0,0

    # Create a node for outputting the surface normals of each pixel
    loc_x = 400
    loc_y = -300
    sep_xyz_node = tree.nodes.new("CompositorNodeSeparateXYZ")
    sep_xyz_node.location = (loc_x, loc_y)

    loc_x += 200
    normalize_x_node = tree.nodes.new("CompositorNodeNormalize")
    normalize_x_node.location = (loc_x, loc_y + 40)

    normalize_y_node = tree.nodes.new("CompositorNodeNormalize")
    normalize_y_node.location = (loc_x, loc_y - 40)

    loc_x += 200
    combine_xyz_node = tree.nodes.new("CompositorNodeCombineXYZ")
    combine_xyz_node.inputs[2].default_value = 1.0
    combine_xyz_node.location = (loc_x, loc_y)

    loc_x += 200
    vl = tree.nodes.new('CompositorNodeViewer')
    vl.location = (loc_x, loc_y)

    links.new(render_layers_node.outputs['Normal'], sep_xyz_node.inputs[0])
    links.new(sep_xyz_node.outputs[0], normalize_x_node.inputs[0])
    links.new(sep_xyz_node.outputs[1], normalize_y_node.inputs[0])
    links.new(normalize_x_node.outputs[0], combine_xyz_node.inputs[0])
    links.new(normalize_y_node.outputs[0], combine_xyz_node.inputs[1])
    links.new(combine_xyz_node.outputs[0], vl.inputs[0])
    links.new(render_layers_node.outputs['Alpha'], vl.inputs['Alpha'])

    bpy.ops.render.render()
    bpy.data.images['Viewer Node'].save_render(filepath=filepath)

def renderDepth(filepath):
    # Useful scene variables
    scene = bpy.context.scene
    tree = bpy.context.scene.node_tree
    links = tree.links

    scene.render.use_compositing = True
    scene.use_nodes = True
    # Configure renderer to record object index
    scene.view_layers["ViewLayer"].use_pass_z = True

    for n in tree.nodes:
        tree.nodes.remove(n)
    
    render_layers_node = tree.nodes.new(type="CompositorNodeRLayers")
    render_layers_node.location = 0,0

    loc_x = 400
    loc_y = -300

    normalize_node = tree.nodes.new("CompositorNodeNormalize")
    normalize_node.location = (loc_x, loc_y)

    loc_x += 200
    vl = tree.nodes.new('CompositorNodeViewer')
    vl.location = (loc_x, loc_y)

    links.new(render_layers_node.outputs['Depth'], normalize_node.inputs[0])
    links.new(normalize_node.outputs[0], vl.inputs[0])
    links.new(render_layers_node.outputs['Alpha'], vl.inputs['Alpha'])

    bpy.ops.render.render()
    bpy.data.images['Viewer Node'].save_render(filepath=filepath)

def projectMap(obj,img):
    scene = bpy.context.scene
    camera = scene.camera
    #print(camera.location)
    camera.scale = (1,1,1)
    right, up, back =camera.matrix_world.to_3x3().transposed() # type: ignore
    #print(up)

    render = scene.render
    matrix_world = camera.matrix_world.copy().transposed()
    offset = -(matrix_world @ matrix_world[3])
    matrix_world[3] = (0,0,0,1)
    matrix_world[0][3] = offset[0]
    matrix_world[1][3] = offset[1]
    matrix_world[2][3] = offset[2]

    # matrix_world = matrix_world.transpose()
    projection_mat = camera.calc_matrix_camera(
        bpy.context.evaluated_depsgraph_get(),       
        x=render.resolution_x,
        y=render.resolution_y,
        scale_x=render.pixel_aspect_x,
        scale_y=render.pixel_aspect_y
        )
    pv = projection_mat @  matrix_world
    #pv[3] = pv @ pv[3]
    # print(matrix_world)
    # print(projection_mat)
    # print(pv)
    #print(pv)
    #return 
    mat = obj.active_material
    tree = mat.node_tree
    nodes = tree.nodes
    links = tree.links

    for n in nodes:
        nodes.remove(n)
    # print(tree.nodes)

    locX, locY= 0 ,0
    
    GeometryInfo = tree.nodes.new("ShaderNodeNewGeometry")
    GeometryInfo.location = (locX,locY)

    locX += 200
    DX = tree.nodes.new("ShaderNodeVectorMath")
    DX.operation = 'DOT_PRODUCT'
    DX.location = (locX,locY)
    DX.hide = True
    DX.inputs[0].default_value = pv[0][:-1]

    locY -= 50
    DY = tree.nodes.new("ShaderNodeVectorMath")
    DY.operation = 'DOT_PRODUCT'
    DY.location = (locX,locY)
    DY.hide = True
    DY.inputs[0].default_value = pv[1][:-1]
    
    locY -= 50
    DZ = tree.nodes.new("ShaderNodeVectorMath")
    DZ.operation = 'DOT_PRODUCT'
    DZ.location = (locX,locY)
    DZ.hide = True
    DZ.inputs[0].default_value = pv[2][:-1]

    locY -= 50
    DW = tree.nodes.new("ShaderNodeVectorMath")
    DW.operation = 'DOT_PRODUCT'
    DW.location = (locX,locY)
    DW.hide = True
    DW.inputs[0].default_value = pv[3][:-1]

    locY -= 50
    DN = tree.nodes.new("ShaderNodeVectorMath")
    DN.operation = 'DOT_PRODUCT'
    DN.location = (locX,locY)
    DN.hide = True
    DN.inputs[0].default_value = (-pv[2])[:-1]

    links.new(GeometryInfo.outputs['Position'],DX.inputs[1])
    links.new(GeometryInfo.outputs['Position'],DY.inputs[1])
    links.new(GeometryInfo.outputs['Position'],DZ.inputs[1])
    links.new(GeometryInfo.outputs['Position'],DW.inputs[1])
    links.new(GeometryInfo.outputs['Normal'],DN.inputs[1])

    locY = 0
    locX += 200
    CombineXYZ = tree.nodes.new("ShaderNodeCombineXYZ")
    CombineXYZ.location = (locX,locY)
    CombineXYZ.hide = True

    links.new(DX.outputs['Value'],CombineXYZ.inputs[0])
    links.new(DY.outputs['Value'],CombineXYZ.inputs[1])
    links.new(DZ.outputs['Value'],CombineXYZ.inputs[2])

    locX += 200
    M1 = tree.nodes.new("ShaderNodeVectorMath")
    M1.operation = 'ADD'
    M1.location = (locX,locY)
    M1.hide = True
    M1.inputs[0].default_value = (pv[0][3],pv[1][3],pv[2][3])
    links.new(CombineXYZ.outputs[0],M1.inputs[1])

    locY -= 50
    M2 = tree.nodes.new("ShaderNodeMath")
    M2.operation = 'ADD'
    M2.location = (locX,locY)
    M2.hide = True
    M2.inputs[0].default_value = pv[3][3]
    links.new(DW.outputs['Value'],M2.inputs[1])
    locY = 0

    locX += 200
    M3 = tree.nodes.new("ShaderNodeVectorMath")
    M3.operation = 'DIVIDE'
    M3.location = (locX,locY)
    M3.hide = True
    links.new(M1.outputs['Vector'],M3.inputs[0])
    links.new(M2.outputs['Value'],M3.inputs[1])

    locX += 200
    M4 = tree.nodes.new("ShaderNodeVectorMath")
    M4.operation = 'MULTIPLY_ADD'
    M4.inputs[1].default_value = (0.5,0.5,1)
    M4.inputs[2].default_value = (0.5,0.5,0)
    M4.location = (locX,locY)
    M4.hide = True
    links.new(M3.outputs['Vector'],M4.inputs[0])

    locX += 200
    Tex = tree.nodes.new("ShaderNodeTexImage")
    Tex.location = (locX,locY)
    Tex.image = img
    Tex.width = GeometryInfo.width
    Tex.extension = "CLIP" 
    links.new(M4.outputs['Vector'],Tex.inputs[0])

    locY -= 300
    Ramp = tree.nodes.new("ShaderNodeValToRGB")
    Ramp.color_ramp.interpolation = 'B_SPLINE'
    Ramp.color_ramp.elements[0].position = 0.4
    Ramp.color_ramp.elements[1].position = 0.7
    Ramp.color_ramp.elements.new(0.545318).color = (0.004,0.004,0.004,1)

    print(Ramp.color_ramp.elements)

    Ramp.location = (locX,locY)
    links.new(DN.outputs['Value'],Ramp.inputs[0])
    locY = 0

    locX += 200
    locY -= 50
    M5 = tree.nodes.new("ShaderNodeMath")
    M5.operation = 'MULTIPLY'
    M5.location = (locX,locY)
    M5.hide = True
    links.new(Tex.outputs[1],M5.inputs[0])
    links.new(Ramp.outputs['Color'],M5.inputs[1])

    locX += 200
    locY += 20
    Emission = tree.nodes.new("ShaderNodeEmission")
    Emission.location = (locX,locY)
    Emission.hide = True
    links.new(Tex.outputs[0],Emission.inputs[0])
    links.new(M5.outputs[0],Emission.inputs[1])
    locY = 0

    locX += 200
    Output = tree.nodes.new("ShaderNodeOutputMaterial")
    Output.location = (locX,locY)
    links.new(Emission.outputs[0],Output.inputs[0])
    
    #CameraDirNode = tree.nodes.new("ShaderNodeValue")
    
    
projectMap(bpy.data.objects['Suzanne'],bpy.data.images['cp 5_normal'])
# renderDepth('myImg_D.png')
# renderNormal('myImg_N.png')