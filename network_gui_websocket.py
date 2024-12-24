import asyncio
import websockets
import threading
import struct
import math
import numpy as np
import torch
import copy
from utils.graphics_utils import getWorld2View2, getProjectionMatrix

curr_id = -1
data_array = None
web_camera = None
latest_width = 0
latest_height = 0
latest_result = bytes([])

# task_completed = asyncio.Event()

def eulerRotation(theata,phi,psi):
    yaw = np.array([
        [math.cos(theata), 0 , math.sin(theata)],
        [0,1,0],
        [-math.sin(theata), 0 , math.cos(theata)],
    ])
    pitch = np.array([
        [1,0,0],
        [0,math.cos(phi),-math.sin(phi)],
        [0,math.sin(phi),math.cos(phi)],
    ])
    roll = np.array([
        [math.cos(psi),-math.sin(psi),0],
        [math.sin(psi),math.cos(psi),0],
        [0,0,1],
    ])
    
    return yaw@pitch@roll.tolist()

async def echo(websocket, path):
    global curr_id
    
    global data_array
    
    global latest_result
    
    global webpage_train_speed
    try:
        async for message in websocket:

            if isinstance(message, bytes):
                num_integers = (len(message)) // 4 
                received_floats = []
                int_received = int.from_bytes(message[0:4], byteorder='big', signed=True)
                webpage_train_speed = value = struct.unpack('>f', message[4:8])[0]

                for i in range(2,num_integers):
                    float_bytes = message[i * 4:(i + 1) * 4]
                    value = struct.unpack('>f', float_bytes)[0]
                    received_floats.append(value)

                curr_id = int_received 
                data_array = received_floats
                header = struct.pack('ii', latest_width, latest_height) 
                await websocket.send(header + latest_result)
                  
    except websockets.exceptions.ConnectionClosed as e:
        print(f"Connection closed: {e}")

async def websocket_server(host, port):
    async with websockets.serve(echo, host, port):
        await asyncio.Future()  
                
def run_asyncio_loop(wish_host, wish_port):
    asyncio.run(websocket_server(wish_host, wish_port))

def init(wish_host, wish_port):
    thread = threading.Thread(target=run_asyncio_loop,args=[wish_host, wish_port])    
    thread.start()


x0 = 0.0
y0 = 0.0
z0 = 0.0

def init_camera(scene):
    global web_camera, x0, y0, z0
    web_camera = copy.deepcopy(scene.getTrainCameras()[0])
    x0,y0,z0 = web_camera.T

def update_camera(web_cam):
    web_cam.world_view_transform = torch.tensor(getWorld2View2(web_cam.R, web_cam.T, web_cam.trans, web_cam.scale)).transpose(0, 1).cuda()
    web_cam.projection_matrix = getProjectionMatrix(znear=web_cam.znear, zfar=web_cam.zfar, fovX=web_cam.FoVx, fovY=web_cam.FoVy).transpose(0,1).cuda()
    web_cam.full_proj_transform = (web_cam.world_view_transform.unsqueeze(0).bmm(web_cam.projection_matrix.unsqueeze(0))).squeeze(0)
    web_cam.camera_center = web_cam.world_view_transform.inverse()[3, :3]

def render_for_websocket(render, gaussians, pipe, background):
    global data_array
    if data_array == None:
        print("Refresh the webpage in the local computer")
        return
    else:
        global web_camera
        extrin = data_array

        x,y,z = extrin[0],extrin[1],extrin[2]
        theata,phi,psi = extrin[3],extrin[4],extrin[5]
        scale = extrin[6]

        web_rot = eulerRotation(theata,phi,psi)
        web_camera.R = web_rot
        
        web_xyz = [x+x0,y+y0,z+z0]
        web_camera.T = web_xyz
        
        update_camera(web_camera)
        
        net_image = render(web_camera, gaussians, pipe, background, scaling_modifier = scale)["render"]
        global latest_height, latest_width, latest_result
        latest_width = net_image.size(2)
        latest_height = net_image.size(1)
        latest_result = memoryview((torch.clamp(net_image, min=0, max=1.0) * 255).byte().permute(1, 2, 0).contiguous().cpu().numpy())


