import socket
import threading
import json
import queue
import asyncio
import websockets
from PyQt5.QtCore import *

import time
import math

class CommunicationManager(QThread):
    velocity_data = pyqtSignal(list)
    w_velocity_data = pyqtSignal(list)
    position_data = pyqtSignal(list)
    Is1stServo_data = pyqtSignal(bool)
    Is2stServo_data = pyqtSignal(bool)
    IsIgnition_data = pyqtSignal(bool)
    IsSeperation_data = pyqtSignal(bool)
    Time_data = pyqtSignal(str)
    
    def __init__(self,parent):
        super().__init__(parent)
        #'단분리 실행','2단 이그나이터 정지','2단 이그나이터 실행', '2단 낙하산 사출'
        #단분리 서보 기본    2단 서보 기본
        self.mSendDataQueue = queue.Queue()
        self.parent=parent

        self.SERVER_IP = '10.210.60.149'  # 서버의 IP 주소를 입력하세요
        self.SERVER_PORT = 8880  # 서버의 포트를 입력하세요

    async def send_messages(self, websocket, message):
            if message:
                await websocket.send(message)

    async def receive_messages(self, websocket):
        try:
            while True:
                # 실제 데이터 수신
                json_data = await websocket.recv()
                if not json_data:
                    break
                
                # 데이터 가공
                readData = json.loads(json_data)
                self.velocity_data.emit(readData["IMUData"].split(',')[0:3])
                self.w_velocity_data.emit(readData["IMUData"].split(',')[3:6])
                self.position_data.emit(readData["IMUData"].split(',')[6:8])
                self.Is1stServo_data.emit(readData["Is1stServo"])
                self.Is2stServo_data.emit(readData["Is2stServo"])
                self.IsIgnition_data.emit(readData["IsIgnition"])
                self.IsSeperation_data.emit(readData["IsSeperation"])
                t =float(readData["Time"])-math.round(time.time()%60,3)
                if(t>5):
                    self.Time_data.emit("5second overValue")
                else: 
                    self.Time_data.emit(str(t))
                #self.mCommunicationDataQueue.put(readData)
                #self.parent.GUIupdateThread.start()
                    
        except websockets.exceptions.ConnectionClosed:
            print("Connection to server closed.")

        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
        
        except Exception as e:
            print(f"Error: {e}")

    async def run(self):
        try:
            uri = f"ws://{self.SERVER_IP}:{self.SERVER_PORT}"
            async with websockets.connect(uri) as websocket:
                
                print(f'connected to {self.SERVER_IP}:{self.SERVER_PORT}')
                
                while True:
                    # IMU 데이터 수신
                    receive_task = asyncio.create_task(self.receive_messages(websocket))
                    await receive_task
                    
                    # Send new interval to client
                    if self.mSendDataQueue.qsize()<1:
                        await self.send_messages(websocket, str("None"))
                    else:
                        senddata = self.mSendDataQueue.get_nowait()
                        json_senddata = json.dumps(senddata)
                        await self.send_messages(websocket, json_senddata)
        except Exception as e:
            print(f"Failed to connect or error during the session: {e}")
                        
        except KeyboardInterrupt:
            print("bye2")
            self.IsCommunication=False
            websocket.close()
            
        finally:
            websocket.close()
