import time
import math
import socket
import asyncio
import queue
import json

import numpy as np

from serial import Serial
import serial
from decimal import Decimal
# sudo raspi-config
# pip3 install pyserial

class IMUmanager:
    def __init__(self,mRocketProtocol):
        self.mRocketProtocol = mRocketProtocol
        # 센서 데이터 큐
        self.mSensorDataQueue = queue.Queue()
        self.mSensorCommunicationDataQueue = queue.Queue()

        self.number_of_item = 6
        self.item=[0,0,0,0,0,0]
        self.undo_item=[0,0,0,0,0,0]

        window_size = 10
        self.filters = [MovingAverageFilter(window_size) for _ in range(self.number_of_item)]
        # 서버 정보
        self.SERVER_IP = '10.210.60.90'  # 서버의 IP 주소를 입력하세요
        self.SERVER_PORT = 8521  # 서버의 포트를 입력하세요

        self.IsCommunication=True
        self.ser =Serial('/dev/ttyS0',115200,parity=serial.PARITY_NONE,stopbits=serial.STOPBITS_ONE,bytesize=serial.EIGHTBITS)

    def getData(self):
        while True:
            if self.ser.readable()> 0:
                try:
                    res = self.ser.readline()
#                    print(res)
                    self.received_data = res.decode('utf-8')
#                    print(self.received_data)
                    self.received_data = self.received_data.strip()
                    self.received_data = self.received_data.strip('*')
                    splited_texts = self.received_data.split(',')

                    for i in range(0,self.number_of_item):
                        #formatted_value=f"{math.ceil(float(splited_texts[i])*100)/100:.3f}"
                        d = Decimal(splited_texts[i])
                        
                        self.item[i] = d.quantize(Decimal('0.001'))
                        
                        self.filters[i].add_value(self.item[i])
                        self.item[i] = self.filters[i].get_filtered_value()
                        self.item[i] = Decimal(self.item[i])
                        self.item[i] = float(self.item[i].quantize(Decimal('0.001')))
                    
                    #print(self.item)
                    self.mSensorDataQueue.put(self.item)
                    if(self.IsCommunication):
                        self.mSensorCommunicationDataQueue.put(self.item)
                    else:
                        print(self.item)

                except:
                    for i in range(0,self.number_of_item):
                        self.item[i] = 0.0
                    if(self.IsCommunication):
                        self.mSensorDataQueue.put(self.item)
                        self.mSensorCommunicationDataQueue.put(self.item)
                    else:
                        print(self.item)

                    print("Error")

    def initConnect(self):
        # 소켓 생성
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.SERVER_IP, self.SERVER_PORT))

    def setRocketProtocol(self,mRocketProtocol):
        self.mRocketProtocol=mRocketProtocol

    def communicationData(self):
        try:
            self.IsCommunication=True
            while True:
                while not self.mSensorCommunicationDataQueue.empty():

                    # 과부화 방지
                    if self.mSensorCommunicationDataQueue.qsize()>5:
                        #print(self.mSensorCommunicationDataQueue.qsize())
                        self.mSensorCommunicationDataQueue.get()

                    #센서값 반환
                    sensor_item = self.mSensorCommunicationDataQueue.get_nowait()

                    # 데이터 string화
                    self.received_data=str(sensor_item[0])
                    for i in range(self.number_of_item-1):
                        self.received_data+=","
                        self.received_data+=str(sensor_item[i+1])
                    #print(self.received_data)
                    # 이그나이터 상태, 단분리 상태, 1단 2단 서보 상태
                    # 속도 3축 , 각속도 3축 값
                    # 위치 3축 값
                    t = round(time.time()%60,3)
                    RocketStatus={'Time':t,'IMUData':self.received_data,'IsIgnition':self.mRocketProtocol.IsIgnition,'IsSeperation':self.mRocketProtocol.IsSeperation,'Is1stServo':self.mRocketProtocol.Is1stServo,'Is2stServo':self.mRocketProtocol.Is2stServo}

                    json_RocketStatus = json.dumps(RocketStatus)

                    # 데이터 길이 정보 전송
                    self.client_socket.sendall(len(json_RocketStatus).to_bytes(4, byteorder='big'))
                    # 데이터 전송
                    print(json_RocketStatus)
                    self.client_socket.sendall((json_RocketStatus).encode('utf-8'))

                    # Receive new interval from server
                    data_length_bytes = self.client_socket.recv(4)
                    data_length = int.from_bytes(data_length_bytes, byteorder='big')
                    print(data_length)
                    new_interval_data = self.client_socket.recv(data_length).decode()
                    #print("New interval received:"+str(new_interval_data))
                    if new_interval_data!="None":
                        print("New interval recevied:"+str(new_interval_data))
                        readData = json.loads(new_interval_data)
                        if readData.get("Seperation")!=None:
                            if(bool(readData["Seperation"])):
                                self.mRocketProtocol.setSeperationServoBoolean(True)
                                print("True")
                            else:
                                self.mRocketProtocol.setSeperationServoBoolean(False)

                                print("False")
                        if readData.get("2ndParachute")!=None:
                            self.mRocketProtocol.set2ndServoBoolean(bool(readData["2ndParachute"]))

        except KeyboardInterrupt:
            print("bye2")
            self.IsCommunication=False
            self.client_socket.close()

    def repeatData(self):
        while True:
            self.mSensorCommunicationDataQueue.put(["1","1","6"])
            time.sleep(0.1)


    async def tcp_echo_client(self, message):
        reader, writer = await asyncio.open_connection(self.SERVER_IP, self.SERVER_PORT)

        print(f'Send: {message}')
        writer.write(message.encode())

        data = await reader.read(100)
        print(f'Received echo: {data.decode()}')

        data = await reader.read(100)
        print(f'Received from server: {data.decode()}')

        print('Close the connection')
        writer.close()
        await writer.wait_closed()

class MovingAverageFilter:
    def __init__(self, window_size):
        self.window_size = window_size
        self.data_window = []

    def add_value(self, value):
        self.data_window.append(value)
        if len(self.data_window) > self.window_size:
            self.data_window.pop(0)

    def get_filtered_value(self):
        if len(self.data_window) == 0:
            return None
        return np.median(self.data_window)
