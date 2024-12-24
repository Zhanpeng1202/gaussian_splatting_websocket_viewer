host = "127.0.0.1"
port = 6019

import asyncio
import websockets
import threading
import struct
import time

curr_id = -1
data_array = None
latest_width = 0
latest_height = 0
latest_result = bytes([])

# task_completed = asyncio.Event()

async def echo(websocket, path):
    start = time.time()
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
    data_array=[0,0,0,0,0,0,0,0,0]
    thread.start()

