import bpy
import asyncio
import concurrent.futures
import threading

import urllib.request
import json
import time
import io
import base64
import bpy

t2iSetting = {
    "prompt": "maltese puppy",
    "steps": 10,
    "width": 512,
    "height": 512,
}
json_data = json.dumps(t2iSetting).encode('utf-8')



headers = {
    "Content-Type": "application/json",
    "Content-Length": len(json_data)
}
host = 'http://127.0.0.1:7860'


def cb(res):
    print(res)
process = 1
_img = None
def main():
    global process
    req = urllib.request.Request(url=f'{host}/sdapi/v1/txt2img',
                        data=json_data,
                        headers=headers,
                        method='POST')
    
    def saveImg(res):
        for i in res['images']:
            img = bpy.data.images.new('MyImage', t2iSetting["width"], t2iSetting["height"])
            imageData = io.BytesIO(base64.b64decode(i.split(",",1)[0])).getvalue()
            img.pack(data=imageData, data_len=len(imageData))
            img.source = 'FILE'
            _img = img
            img.file_format = 'PNG'
            img.filepath_raw = "./res.png"
            img.save()
            
    
    Worker(req,saveImg).start()

    req = urllib.request.Request(url=f'{host}/sdapi/v1/progress',
                    data=None,
                    headers=headers,
                    method='GET')
    def handleProcess(res):
        global process
        process = res['progress']
        print(process)
    process = 1

    while process >0:
        Worker(req,handleProcess).start()
        time.sleep(2)


class Worker(threading.Thread):
    def __init__(self,req, callback):
        self.req = req
        self.callback = callback
        threading.Thread.__init__(self)

    def run(self):

        with urllib.request.urlopen(self.req) as response:
            # 获取响应内容
            response_data = response.read().decode()
            res = json.loads(response_data)
            if self.callback is not None:
                self.callback(res)
main()
print("start")
