import math
import os
import bpy
from bpy.types import Panel, UIList, Menu, PropertyGroup, Operator
from ..common.utils import isPHILOGIXexist

from ..op.op_cameraPosition import selectingLayer

def draw_image_preview(layout, image):
    preview = 1
    if image is not None:
        if hasattr(image, 'preview_ensure') and not image.preview:
            image.preview_ensure()
        preview = image.preview.icon_id
    
    row = layout.row() 
    row.scale_y = 6 + int(image is None) * 0
    
    row.template_icon(preview,scale=1)
    
    
class CameraPosition_PT_Info(Panel):
    bl_label = "CamProj"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'CamProj'
    # bl_context = "objectmode"

    def draw(self, context):
        cp_prop = context.scene.cp_prop
        layout = self.layout

        row = layout.row()
        box = row.box()
        box.alignment = "CENTER"
        col = box.row()
        row1 = col.row()
        row1.operator("pde.add_layer", text="", icon_value=125, emboss=False)
        row1.operator("pde.load_layer", text="",
                      icon="RESTRICT_VIEW_OFF", emboss=False)

        col.separator(factor=0.5)
        row2 = col.row()
        row2.alignment = "RIGHT"
        row2.operator("pde.update_layer", text="",
                      icon="UV_SYNC_SELECT", emboss=False)
        row2.operator("pde.remove_layer", text="", icon="TRASH", emboss=False)

        row = layout.row()
        row.prop(cp_prop, "autoLoad", text="Auto load")
        row.prop(cp_prop, "showPreview", text="Show Preview")
        row = layout.row(align=True)
        if cp_prop.showPreview:
            num_cols = max(1,(context.region.width) // 200)
            row.template_list("LayerItems", "abc", cp_prop, "layers", cp_prop,
                            "layers_index", sort_reverse=False, sort_lock=False, maxrows=1,columns=num_cols,type="GRID")
        else:
            row.template_list("LayerItems", "abc", cp_prop, "layers", cp_prop,
                            "layers_index", sort_reverse=False, sort_lock=False, rows=3)

        layout.separator(factor=0.5)
        row = layout.row()

        layers = cp_prop.layers
        layer_index = cp_prop.layers_index
        if len(layers) > layer_index > -1:
            layer = layers[layer_index]
            row.label(
                text=f"{layer.name} {int(layer.ResolutionX*(layer.ResolutionPercentage/100))} x {int(layer.ResolutionY*(layer.ResolutionPercentage/100))}")
        row = layout.row()
        
        
        # preview = bpy.data.images['微信图片_20231007225433.png'].preview.icon_id
        if not selectingLayer(context): return
        
        row = layout.row()
        # render
        box = row.box()
        row1 = box.row()
        layer = cp_prop.layers[cp_prop.layers_index]
        row1.prop(cp_prop, 'render_extended_settings', text='', emboss=False, icon_value = 4+int(cp_prop.render_extended_settings))
        row1.label(text="Render results: ")
        if cp_prop.render_extended_settings:
            row = box.row()
            row.operator("pde.render_image", text="", emboss=False, icon="SHADING_RENDERED")
            row.operator("pde.render_viewport", text="", emboss=False, icon="SCENE_DATA")
            row.operator("pde.set_render_result_as_preview", text="Set as preview")
            
            box.template_icon_view(layer, "renderResultsEnum", show_labels=True, scale_popup=4)
            texture_selected = layer.renderResultSelected
            row = box.row()
            
            row.label(text=texture_selected.name if texture_selected else "No render result")
            if texture_selected:
                row = row.row()
                row.alignment = "RIGHT"
                row.operator("pde.copy_render_result", text="", emboss=False, icon="COPYDOWN")
                row.operator("pde.toggle_render_view", text="", emboss=False, icon="RESTRICT_VIEW_OFF").imageName = layer.renderResultSelected.name
                row.operator("pde.remove_render_result", text="", emboss=False, icon="TRASH")
            #draw_image_preview(row, bpy.data.images['微信图片_20231007225433.png'])
        
        # 渲染深度、法线
        row = layout.row()
        box = row.box()
        row1 = box.row()
        row1.prop(cp_prop, 'dn_extended_settings', text='', emboss=False, icon_value = 4+int(cp_prop.dn_extended_settings))
        row1.label(text="Depth and normal: ")
        if cp_prop.dn_extended_settings:
            row2 = box.row()
            box1 = row2.box()
            row = box1.row()
            row.alignment = "CENTER"
            row.label(text="Depth")
            draw_image_preview(box1, layer.depthMap)
            row = box1.row()
            row.alignment = "CENTER"
            row.operator("pde.render_depth", text="", emboss=False, icon="SHADING_RENDERED")
            #row.operator("pde.copy_depth", text="", emboss=False, icon="COPYDOWN")
            row = row.row()
            if not layer.depthMap:
                row.enabled = False
            row.operator("pde.toggle_render_view", text="", emboss=False, icon="RESTRICT_VIEW_OFF").imageName = layer.depthMap.name if layer.depthMap else ""
            row = box1.row()
            row.operator("pde.copy_depth", text="Copy")
            
            box2 = row2.box()
            row = box2.row()
            row.alignment = "CENTER"
            row.label(text="View normal")
            draw_image_preview(box2, layer.normalMap)
            row = box2.row()
            row.alignment = "CENTER"
            row.operator("pde.render_normal", text="", emboss=False, icon="SHADING_RENDERED")
            # row.operator("pde.copy_normal", text="", emboss=False, icon="COPYDOWN")
            row = row.row()
            if not layer.normalMap:
                row.enabled = False
            row.operator("pde.toggle_render_view", text="", emboss=False, icon="RESTRICT_VIEW_OFF").imageName = layer.normalMap.name if layer.normalMap else ""
            row = box2.row()
            row.operator("pde.copy_normal", text="Copy")
        
        row = layout.row()
        
        # 图集选择
        box = row.box()
        row1 = box.row()
        layer = cp_prop.layers[cp_prop.layers_index]
        row1.prop(cp_prop, 'tex_extended_settings', text='', emboss=False, icon_value = 4+int(cp_prop.tex_extended_settings))
        row1.label(text="Textures projection: ")
        if cp_prop.tex_extended_settings:
            row = box.row()
            box = row.box()
            box.alignment = "CENTER"
            col = box.row()
            row1 = col.row()
            row1.operator("pde.paste_texture", text="", icon="PASTEDOWN", emboss=False)
            
            row1.template_ID(cp_prop,"texture_preview", open="image.open")
            row1.operator("pde.add_to_texture", text="",
                        icon="SORT_ASC", emboss=False)
            box.template_icon_view(layer, "texturesEnum", show_labels=True, scale_popup=4)
            texture_selected = layer.textureSelected
            row = box.row()
            row.enabled = not not texture_selected
            row.label(text=texture_selected.name if texture_selected else "Not selected")
            row.operator("pde.toggle_render_view", text="", emboss=False ,icon="RESTRICT_VIEW_OFF").imageName = texture_selected.name if texture_selected else ""
            row.operator("pde.remove_texture", text="", emboss=False ,icon="TRASH")
            box.separator(factor=0.1)
            
            # texture painting
            col = box.column()
            col.label(text="Texture painting :")
            col.operator("pde.apply_texture", text="Apply texture",icon="TEXTURE")
            col.operator("pde.align_stencil", text="Align stencil",icon="MOD_MESHDEFORM")
            
            # Philogix
            col = box.column()
            plxExist = isPHILOGIXexist()
            col.enabled = plxExist
            col.label(text=f"Philogix {cp_prop.plxVersion} :" if plxExist else "No philogix detected")
            if plxExist:
                col.operator("pde.create_plx_smart_material", text="create smart material",icon="NODE_MATERIAL")
                col.operator("pde.create_plx_surface_layer", text="create surface layer",icon="SURFACE_NSPHERE")
        
        row = layout.row()
        box = row.box()
        row1 = box.row()
        layer = cp_prop.layers[cp_prop.layers_index]
        row1.prop(cp_prop, 'debug_extended_settings', text='', emboss=False, icon_value = 4+int(cp_prop.debug_extended_settings))
        row1.label(text="Debug setting:")
        if cp_prop.debug_extended_settings:
            row = box.row()
            row.prop(cp_prop, "offsetCopy", text="offset 3 pixels when copy")
            row = box.row()
            row.label(text="Align offset")
            row.prop(cp_prop, "offsetAlignX", text="X")
            row.prop(cp_prop, "offsetAlignY", text="Y")
            
class LayerItems(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if context.scene.cp_prop.showPreview:
            layout.scale_x = 2
            
            # draw layer type
            box = layout.box()
            box.alignment = "CENTER"
            box.prop(item, "name", icon="NONE", emboss=False,text="")
            #box.prop(item, "name", icon="NONE", emboss=False, text="")
            draw_image_preview(box, item.preview)
        else:
            layout.prop(item, "name", icon="NONE", emboss=False, text="")
        

    def draw_error_layer(self, layout, active_mat, index, text=''):
        layout.alert = True
        layout.label(text=text, icon="ERROR")
