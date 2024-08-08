import time
import math
import websockets
import asyncio
import queue
import json
import asyncio

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

        self.number_of_item = 9
        self.item=[0,0,0,0,0,0,0,0,0]
        self.undo_item=[0,0,0,0,0,0,0,0,0]

        window_size = 10
        self.filters = [MovingAverageFilter(window_size) for _ in range(self.number_of_item)]
        # 서버 정보
        self.SERVER_IP = '10.210.60.50'  # 서버의 IP 주소를 입력하세요
        self.SERVER_PORT = 8881  # 서버의 포트를 입력하세요

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

    def setRocketProtocol(self,mRocketProtocol):
        self.mRocketProtocol=mRocketProtocol

    async def send_messages(self, websocket):
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

                    RocketStatus={'Time':t,
                                  'IMUData':self.received_data,
                                  'IsIgnition':self.mRocketProtocol.IsIgnition,
                                  'IsSeperation':self.mRocketProtocol.IsSeperation,
                                  'Is1stServo':self.mRocketProtocol.Is1stServo,
                                  'Is2stServo':self.mRocketProtocol.Is2stServo}

                    json_RocketStatus = json.dumps(RocketStatus)

                    # 데이터 전송
                    print(json_RocketStatus)
                    await websocket.send(json_RocketStatus)
                    await asyncio.sleep(0.1)

        except websockets.exceptions.ConnectionClosed as e:
            print(f"Connection closed: {e}")
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            
        except queue.Empty as e:
            print(f"Queue is empty: {e}")
        
        except Exception as e:
            print(f"Error: {e}")

    async def receive_messages(self, websocket):        
        try:
            while True:
                # Receive new interval from server
                new_interval_data = await websocket.recv()
                print("New interval received:"+str(new_interval_data))
                #print("New interval received:"+str(new_interval_data))
                
                if new_interval_data!="None":
                    print("New interval recevied:"+str(new_interval_data))
                    readData = json.loads(new_interval_data)
                    if readData.get("Seperation")!=None:
                        self.mRocketProtocol.setSeperationServoBoolean(bool(readData["Seperation"]))
                    if readData.get("2ndParachute")!=None:
                        self.mRocketProtocol.set2ndServoBoolean(bool(readData["2ndParachute"]))
                    if readData.get("Ignition")!=None:
                        self.mRocketProtocol.setIgnition(bool(readData["Ignition"]))

        except websockets.exceptions.ConnectionClosed:
                print("Connection to server closed.")

        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
        
        except Exception as e:
            print(f"Error: {e}")
            
    async def communicationData(self):
        websocket = None
        uri = f"ws://{self.SERVER_IP}:{self.SERVER_PORT}"
        async with websockets.connect(uri) as websocket:
            try:
                self.IsCommunication=True
                print(f'connected to {self.SERVER_IP}:{self.SERVER_PORT}')
                # 데이터 전송
                #print(json_RocketStatus)
                send_task = asyncio.create_task(self.send_messages(websocket))

                # Receive new interval from server
                receive_task = asyncio.create_task(self.receive_messages(websocket))
                
                await asyncio.gather(receive_task,send_task)

            except Exception as e:
                print(f"Failed to connect or error during the session: {e}")
                            
            except KeyboardInterrupt:
                print("bye2")
                self.IsCommunication=False

            finally:
                self.IsCommunication = False

    def repeatData(self):
        while True:
            self.mSensorCommunicationDataQueue.put(["1","1","6"])
            time.sleep(0.1)


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
