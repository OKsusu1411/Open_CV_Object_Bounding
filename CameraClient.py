import socket
import pickle
import pyrealsense2 as rs
import numpy as np
import argparse

# RealSense 카메라 초기화o
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 15)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# 스트리밍 시작
pipeline.start(config)

def TCP_Connect(ip, port):
    # 소켓 생성
    global client_socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((ip, port))

def main():
    parser = argparse.ArgumentParser(description="TCP/IP Connection")
    parser.add_argument('--ip', type = str, default = '127.0.0.1')
    parser.add_argument('--port', type = int, default = '9999')
    args = parser.parse_args()
    TCP_Connect(args.ip, args.port)

    try:
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
            data = pickle.dumps(depth_image)
            data2 = pickle.dumps(color_image)

            # 데이터 길이 정보 전송
            client_socket.sendall(len(data).to_bytes(4, byteorder='big'))
            # 데이터 전송
            client_socket.sendall(data)
            # 데이터 길이 정보 전송
            client_socket.sendall(len(data2).to_bytes(4, byteorder='big'))
            # 데이터 전송
            client_socket.sendall(data2)

    finally:
        # 스트리밍 중지
        pipeline.stop()
        client_socket.close()

if __name__=="__main__":
    main()