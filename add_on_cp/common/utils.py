import bpy
from ..op.op_cameraPosition import getProp
import numpy as np

def extract_number_from_label(label, prefix):
    parts = label.split()
    tocheck = " ".join(parts[:-1])
    if tocheck == prefix and parts[-1].isdigit():
        return int(parts[-1])
    return 0

def make_images_label(images, prefix):
    used_labels = {i.image.name for i in images if i.image}
    numbers = [extract_number_from_label(
        label, prefix) for label in used_labels]
    number = max(numbers) + 1 if numbers else 1

    return f"{prefix} {number}"

def make_layer_label(layers, prefix):
    used_labels = {layer.name for layer in layers}
    numbers = [extract_number_from_label(
        label, prefix) for label in used_labels]
    number = max(numbers) + 1 if numbers else 1

    return f"{prefix} {number}"


def getCollection():
    colName = "CameraPositionCollection"
    coll = bpy.data.collections.get(colName)
    if coll is None:
        coll = bpy.data.collections.new(colName)
        vl_colls = bpy.context.view_layer.layer_collection.children
        bpy.context.scene.collection.children.link(coll)
        for c in vl_colls:
            if c.collection == coll:
                c.exclude = True

    return coll

def copy2Clipboard(image):
    area = bpy.context.area
    old_type = area.type
    if old_type != 'IMAGE_EDITOR':
        area.type = 'IMAGE_EDITOR'
    oriImage = area.spaces.active.image
    
    # 3.6.5中clipboard_copy有3个像素的偏移，需要偏移回去，其实还有左下角会变黑，不知道咋改
    if getProp(bpy.context).offsetCopy:
        offset = 3
        tempImage = image.copy()
        arr = np.array(image.pixels).reshape((image.size[0],image.size[1],image.channels))
        arr = np.concatenate((arr[:, offset:,:], arr[:, :offset,:]), axis=1)
        tempImage.pixels = arr.flatten()
    
        area.spaces.active.image = tempImage
        bpy.ops.image.clipboard_copy()
        
        bpy.data.images.remove(tempImage)    
    else:
        area.spaces.active.image = image
        bpy.ops.image.clipboard_copy()
        
    area.spaces.active.image = oriImage 
    area.type = old_type

def pasteClipboard():
    area = bpy.context.area
    old_type = area.type
    if old_type != 'IMAGE_EDITOR':
        area.type = 'IMAGE_EDITOR'
    oriImage = area.spaces.active.image
    
    bpy.ops.image.clipboard_paste()
    image = area.spaces.active.image
    
    area.spaces.active.image = oriImage 
    area.type = old_type
    return image

def isPHILOGIXexist():
    try:
        bpy.ops.plx.add_surface.poll()
        return True
    except:
        return False
