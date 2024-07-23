import asyncio
import websockets
import argparse
import sys
import pickle
import numpy as np
import cv2
from object_tracking import *
import globals

async def send_messages(websocket):
    while True:
        # 비동기적으로 사용자 입력 받기
        message = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
        message = message.strip()  # 줄바꿈 문자 제거
        if message:
            await websocket.send(message)

async def receive_messages(websocket):
    try:
        while True:
            # depth 데이터 길이 정보 수신
            data_tmp_depth = await websocket.recv()
            if len(data_tmp_depth) < 4:
                continue

            # data_len_depth = data_tmp_depth[:4]
            # if not data_len_depth:
            #     break
            data_len_depth = int.from_bytes(data_tmp_depth[:4], byteorder='big')

            # depth 데이터 수신
            data_depth = data_tmp_depth[4:]
            while len(data_depth) < data_len_depth:
                packet_depth = await websocket.recv()
                if not packet_depth:
                    break
                data_depth += packet_depth
            
            # 데이터 역직렬화
            image_depth = pickle.loads(data_depth)
            image_depth = np.array(image_depth, dtype=np.uint8)
            # # RGB 데이터 길이 정보 수신
            # data_len_color = await websocket.recv(4)
            # if not data_len_color:
            #     break
            # data_len_color = int.from_bytes(data_len_color, byteorder='big')

            # # RGB 데이터 수신
            # data_color = b""
            # while len(data_color) < data_len_color:
            #     packet = websocket.recv((data_len_color - len(data_color)))
            #     if not packet:
            #         break
            #     data_color += packet
            # 화면 출력
            # cv2.namedWindow('Color Bounding', cv2.WINDOW_AUTOSIZE)
            # cv2.imshow('Color Bounding', image_depth)
            # cv2.waitKey(1)
            # Class 생성
            Depthimagebounding = DepthImageBounding(data_depth)
            # Colorimagebounding = ColorImageBounding(data_color)
            
            # image 출력
            Depthimagebounding.image_out()
            # Colorimagebounding.image_out()

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