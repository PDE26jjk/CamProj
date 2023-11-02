import bpy
import bmesh
 
import urllib.request
import json

# 构建请求的JSON数据
data = {

}
json_data = json.dumps(data).encode('utf-8')

# 设置请求头
headers = {
    "Content-Type": "application/json",
    "Content-Length": len(json_data)
}
host = 'http://R9000p:7860'
# 发送POST请求
req = urllib.request.Request(url=host+'/sdapi/v1/sd-models',
                             data=data,
                             headers=headers,
                             method='GET')
async def send_async():
    urllib.request.urlopen(req)

import bpy
import bpy.utils.previews
import asyncio
def setup_asyncio_executor():
    """Sets up AsyncIO to run properly on each platform."""

    import sys

    if sys.platform == 'win32':
        asyncio.get_event_loop().close()
        # On Windows, the default event loop is SelectorEventLoop, which does
        # not support subprocesses. ProactorEventLoop should be used instead.
        # Source: https://docs.python.org/3/library/asyncio-subprocess.html
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)
    else:
        loop = asyncio.get_event_loop()

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)
    loop.set_default_executor(executor)

class Panel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Hello World Panel"
    bl_idname = "OBJECT_PT_custom_properties"
    
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Tool"

    def draw(self, context):
        scene = bpy.context.scene
        layout = self.layout
        layout.operator( button1.bl_idname , text=button1.bl_label)


class button1(bpy.types.Operator):
    bl_idname = "ddd.init_my_prop"
    bl_label = "Init dmy_prop"

 
    def execute(self, context):
        asyncio.run(send_async())
        print("hahah")    

        return {'FINISHED'}

classList = [
    Panel,
    button1
]
def register(): 
    # register the classes
    for c in classList:
        bpy.utils.register_class(c)
    

def unregister():
    for c in classList:
        bpy.utils.unregister_class(c)



if __name__ == "__main__":
    register()