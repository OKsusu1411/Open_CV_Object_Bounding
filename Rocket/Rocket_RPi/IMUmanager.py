import time
import socket
import asyncio
import queue
import json
import websockets

import math
# sudo raspi-config
# pip3 install pyserial


class IMUmanager:
    def __init__(self,mRocketProtocol):
        self.mRocketProtocol = mRocketProtocol
        # 센서 데이터 큐
        self.mSensorDataQueue = queue.Queue()
        self.mSensorCommunicationDataQueue = queue.Queue()

        self.number_of_item = 9
        self.item=[0,0,0]
        self.undo_item=[0,0,0]

        # 서버 정보
        self.SERVER_IP = '10.210.60.149 '  # 서버의 IP 주소를 입력하세요
        self.SERVER_PORT = 8880  # 서버의 포트를 입력하세요

        self.IsCommunication=False
        
    def getData(self):
        while True:
            if self.ser.in_waiting > 0:
                try:
                    self.received_data = self.ser.readline().decode('utf-8').rstrip()
                    self.received_data = self.received_data.strip()
                    self.received_data = self.received_data.strip('*')
                    print("Received:", self.received_data)
                    splited_texts = self.received_data.split(',')
                    for i in range(0,self.number_of_item):
                        self.item[i] = float(splited_texts[i])

                    if(self.IsCommunication):
                        self.mSensorDataQueue.put(self.item)
                        self.mSensorCommunicationDataQueue.put(self.item)
                    else:
                        print(self.item)
                
                except Exception as e:
                    print("Error:", e)
                    break

    # def initConnect(self):
    #     # 웹소켓 생성
    #     asyncio.run(self.chat_client(self.SERVER_IP, self.SERVER_PORT))

    # async def chat_client(self, ip, port):
    #     uri = f"ws://{ip}:{port}"
    #     try:
    #         async with websockets.connect(uri) as websocket:
    #             send_task = asyncio.create_task(self.send_messages(websocket))
    #             receive_task = asyncio.create_task(self.receive_messages(websocket))
    #             await asyncio.gather(send_task, receive_task)
    #     except Exception as e:
    #         print(f"Failed to connect or error during the session: {e}")
            
    async def send_messages(self, websocket, message):
            if message:
                await websocket.send(message)

    async def receive_messages(self, websocket):
        try:
            while True:
                new_interval_data = await websocket.recv()
                print("New interval received:"+str(new_interval_data))
                if new_interval_data!="None":
                    readData = json.loads(new_interval_data)
                    if readData.get("Ignition")!=None:
                        if(readData["Ignition"]):
                            #self.mRocketProtocol.set2ndServoBoolean(True)
                            print("True")
                        else:
                            #self.mRocketProtocol.set2ndServoBoolean(False)
                            print("False")
        except websockets.exceptions.ConnectionClosed:
            print("Connection to server closed.")

        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
        
        except Exception as e:
            print(f"Error: {e}")

    def setRocketProtocol(self,mRocketProtocol):
        self.mRocketProtocol=mRocketProtocol

    

    async def communicationData(self):
        websocket = None
        
        try:
            self.IsCommunication=True
            uri = f"ws://{self.SERVER_IP}:{self.SERVER_PORT}"
            async with websockets.connect(uri) as websocket:
                print(f'connected to {self.SERVER_IP}:{self.SERVER_PORT}')
                while True:
                    while not self.mSensorCommunicationDataQueue.empty():

                        # 과부화 방지
                        if self.mSensorCommunicationDataQueue.qsize()>5:
                            self.mSensorCommunicationDataQueue.get()

                        #센서값 반환
                        sensor_item = self.mSensorCommunicationDataQueue.get_nowait()
                        
                        # 데이터 string화
                        # self.received_data=str(round(sensor_item[0],3))
                        # for i in range(self.number_of_item-1):
                        #     self.received_data+=","
                        #     self.received_data+=str(round(sensor_item[i+1],3))
                        self.received_data = ",".join([str(round(val, 3)) for val in sensor_item])
                        
                        # 이그나이터 상태, 단분리 상태, 1단 2단 서보 상태
                        # 속도 3축 , 각속도 3축 값
                        # 위치 3축 값 
                        RocketStatus = {
                            'Time': round(time.time() % 60, 3),
                            'IMUData': self.received_data,
                            'IsIgnition': self.mRocketProtocol.IsIgnition,
                            'IsSeperation': self.mRocketProtocol.IsSeperation,
                            'Is1stServo': self.mRocketProtocol.Is1stServo,
                            'Is2stServo': self.mRocketProtocol.Is2stServo
                        }
                        json_RocketStatus = json.dumps(RocketStatus)

                        # 데이터 전송
                        #print(json_RocketStatus)
                        await self.send_messages(websocket,json_RocketStatus)

                        # Receive new interval from server
                        receive_task = asyncio.create_task(self.receive_messages(websocket))
                        await receive_task

        except Exception as e:
            print(f"Failed to connect or error during the session: {e}")
                        
        except KeyboardInterrupt:
            print("bye2")
            self.IsCommunication=False

        finally:
            self.IsCommunication = False
            websocket.close()

    def repeatData(self):
        while True:
            self.mSensorCommunicationDataQueue.put(["1","1","6"])
            time.sleep(0.1)
