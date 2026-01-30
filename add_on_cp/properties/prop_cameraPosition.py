import bpy
from bpy.props import BoolProperty, IntProperty, StringProperty, CollectionProperty, FloatProperty, EnumProperty, \
    PointerProperty
from bpy.types import PropertyGroup

from .prop_update import get_cp_name, layers_index_update, set_cp_name


class ImageType(PropertyGroup):
    # path: StringProperty()
    image: PointerProperty(type=bpy.types.Image)
    # selected: BoolProperty(name="Selected", default=False)


def getRenderResultsItems(self, context):
    items = []
    num = 1
    for i in self.renderResults:
        image = i.image
        preview = 1
        if image:
            if not image.preview and hasattr(image, 'preview_ensure'):
                image.preview_ensure()
            preview = image.preview.icon_id
            size = f"{image.size[0]} x {image.size[1]}"
            items.append((image.name, image.name, size, preview, num))
        else:
            items.append(("error", "error", "error", preview, num))
        num += 1
    return items


def renderResultsItemsUpdate(self, context):
    dataID = self.renderResultsEnum
    self.renderResultSelected = bpy.data.images[dataID]


def getTextureItems(self, context):
    items = []
    num = 1
    for i in self.textureSet:
        image = i.image
        preview = 1
        if image:
            if not image.preview and hasattr(image, 'preview_ensure'):
                image.preview_ensure()
            preview = image.preview.icon_id
            size = f"{image.size[0]} x {image.size[1]}"
            items.append((image.name, image.name, size, preview, num))
        else:
            items.append(("error", "error", "error", preview, num))
        num += 1
    return items


def texturesItemsUpdate(self, context):
    dataID = self.texturesEnum
    self.textureSelected = bpy.data.images[dataID]


class CameraPositionType(PropertyGroup):
    name: StringProperty(get=get_cp_name,
                         set=set_cp_name)
    preview: PointerProperty(type=bpy.types.Image)
    depthMap: PointerProperty(type=bpy.types.Image)
    normalMap: PointerProperty(type=bpy.types.Image)
    renderResults: CollectionProperty(type=ImageType)
    renderResultsEnum: EnumProperty(name='render_results',
                                    description='List of render results',
                                    items=getRenderResultsItems,
                                    update=renderResultsItemsUpdate
                                    )
    renderResultSelected: PointerProperty(type=bpy.types.Image)

    texturesEnum: EnumProperty(name='texture_results',
                               description='List of textures',
                               items=getTextureItems,
                               update=texturesItemsUpdate
                               )
    textureSelected: PointerProperty(type=bpy.types.Image)
    textureSet: CollectionProperty(type=ImageType)

    ResolutionX: IntProperty()
    ResolutionY: IntProperty()
    ResolutionPercentage: IntProperty()
    AspectX: FloatProperty()
    AspectY: FloatProperty()


class CameraPositionProp(PropertyGroup):
    autoLoad: BoolProperty(name="Auto Load", description='Auto load layer when Selecting', default=False)
    showPreview: BoolProperty(name="Show Preview", default=False)
    layers: CollectionProperty(type=CameraPositionType)
    layers_index: IntProperty(
        name='', update=layers_index_update, options={'LIBRARY_EDITABLE'})

    render_extended_settings: BoolProperty(
        name="Render result extend", default=True)
    dn_extended_settings: BoolProperty(
        name="Depth normal extend", default=True)
    tex_extended_settings: BoolProperty(name="Texture extend", default=True)
    texture_preview: PointerProperty(type=bpy.types.Image)

    # plx
    plxVersion: IntProperty(default=4)
    # debug
    debug_extended_settings: BoolProperty(
        name="Debug extend", default=False)
    offsetCopy: BoolProperty(name="Texture extend",
                             description='some bug fixing ',
                             default=False)
    offsetAlignX: FloatProperty(name="Align offset  X",
                                description='fix align bias',
                                default=-1)
    offsetAlignY: FloatProperty(name="Align offset  Y",
                                description='fix align bias',
                                default=-1)
