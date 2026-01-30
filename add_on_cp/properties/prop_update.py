import bpy
from ..op.op_cameraPosition import loadLayer


def layers_index_update(self, context):
    if context.scene.cp_prop.autoLoad:
        layers = self.layers
        if len(layers) > 0 and self.layers_index >= 0:
            layer = layers[self.layers_index]
            loadLayer(layer, context)


def get_cp_name(self):
    return self.get("name", "")


def set_cp_name(self, value):
    oldname = self.get("name", "")
    cam = bpy.data.objects.get(oldname)
    if cam is not None:
        cam.name = value
        cam.data.name = value
        value = cam.name
    self["name"] = value
