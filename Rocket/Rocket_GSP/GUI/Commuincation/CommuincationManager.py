import socket
import threading
import json
import queue
import asyncio
import websockets
from PyQt5.QtCore import *

import time
import math

connected = set()
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

    async def send_messages(self, websocket):# Send new interval to client
        try:
            while True:
                if self.mSendDataQueue.qsize()>=1:
                    senddata = self.mSendDataQueue.get_nowait()
                    json_senddata = json.dumps(senddata)
                    print(json_senddata)
                    await websocket.send(json_senddata)
        except websockets.exceptions.ConnectionClosed:
            print("Connection to server closed.")

        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
        
        except Exception as e:
            print(f"Error: {e}")

    async def receive_messages(self, websocket):
        print("alkdfladkfjl;a")
        try:
            print("alkdfladkfjl;a")
            while True:
                # 실제 데이터 수신
                json_data = await websocket.recv()
                if not json_data:
                    break
                
                # 데이터 가공
                readData = json.loads(json_data)
                print(readData)
                self.velocity_data.emit(readData["IMUData"].split(',')[0:3])
                self.w_velocity_data.emit(readData["IMUData"].split(',')[3:6])
                self.position_data.emit(readData["IMUData"].split(',')[6:8])
                self.Is1stServo_data.emit(readData["Is1stServo"])
                self.Is2stServo_data.emit(readData["Is2stServo"])
                self.IsIgnition_data.emit(readData["IsIgnition"])
                self.IsSeperation_data.emit(readData["IsSeperation"])
                t =float(readData["Time"])-round(time.time()%60,3)
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

    def run(self):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.start_server('10.210.60.149',8880))
        except Exception as e:
            print(f"Error : {e}")
        finally:
            loop.close()
                    
    async def run_communication(self):
        try:
            uri = f"ws://{self.SERVER_IP}:{self.SERVER_PORT}"
            async with websockets.connect(uri) as websocket:
                print(f'connected to {self.SERVER_IP}:{self.SERVER_PORT}')
                #while True:
                    # 데이터 전송
                    #print(json_RocketStatus)
                send_task = asyncio.create_task(self.send_messages(websocket))

                # Receive new interval from server
                receive_task = asyncio.create_task(self.receive_messages(websocket))

                await asyncio.gather(send_task(), receive_task())

        except Exception as e:
            print(f"Failed to connect or error during the session: {e}")

        except KeyboardInterrupt:
            print("bye2")
            self.IsCommunication=False
            websocket.close()
            
        finally:
            websocket.close()
    
    async def start_server(self, host, port):
        async with websockets.serve(self.chat_handler, host, port, ping_interval=10, ping_timeout=20):
            print(f"서버가 {host}:{port}에서 시작됨")
            await asyncio.Future()  # 서버가 계속 실행되도록 유지
    
    async def chat_handler(self, websocket, path):
        connected.add(websocket)
        try:
            # 정기적으로 핑 보내야 함
            # asyncio.create_task(ping_interval(websocket))
            while True:
                await self.receive_messages(websocket)
                await self.send_messages(websocket)
        except websockets.exceptions.ConnectionClosed:
            print(f"Connection closed: {websocket.remote_address}")
        finally:
            connected.remove(websocket)