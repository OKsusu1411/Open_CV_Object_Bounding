import asyncio
import websockets
import argparse
import sys
import pickle
import pyrealsense2 as rs
import numpy as np

# RealSense 카메라 초기화
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 15)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# 스트리밍 시작
pipeline.start(config)

async def send_messages(websocket):
    while True:
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        if not depth_frame or not color_frame:
            continue

        # Depth 데이터를 numpy 배열로 변환
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # 데이터 직렬화
        data_depth = pickle.dumps(depth_image)
        data_color = pickle.dumps(color_image)

        message_depth=len(data_depth).to_bytes(4, byteorder='big')+data_depth
        message_color=len(data_color).to_bytes(4, byteorder='big')+data_color
        if message_depth or message_color:
            await websocket.send(message_depth)
            #await websocket.send(message_color)

async def receive_messages(websocket):
    try:
        while True:
            response = await websocket.recv()
            print(f"Received: {response}")
    except websockets.exceptions.ConnectionClosed:
        print("Connection to server closed.")

async def chat_client(ip, port):
    uri = f"ws://{ip}:{port}"
    try:
        async with websockets.connect(uri) as websocket:
            send_task = asyncio.create_task(send_messages(websocket))
            receive_task = asyncio.create_task(receive_messages(websocket))
            await asyncio.gather(send_task, receive_task)
    except Exception as e:
        print(f"Failed to connect or error during the session: {e}")

def main():
    parser = argparse.ArgumentParser(description="Connect to a websocket server.")
    parser.add_argument('--ip', type=str, default='localhost', help='Host of the websocket server')
    parser.add_argument('--port', type=int, default=9998, help='Port of the websocket server')
    
    args = parser.parse_args()
    asyncio.run(chat_client(args.ip, args.port))

if __name__ == "__main__":
    main()
