import os, sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import time

class ThreadManager(QThread):

    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.is_running = False

    def setManager(self,mCommunicationManager,mButtonGraphList,mCoordinateWidget,mSensorGraphList):
        self.mCommunicationManager=mCommunicationManager
        self.mButtonGraphList=mButtonGraphList
        self.mCoordinateWidget=mCoordinateWidget
        self.mSensorGraphList=mSensorGraphList

    def run(self):
            while not self.mCommunicationManager.mCommunicationDataQueue.empty():    
                #print(self.mCommunicationManager.mCommunicationDataQueue.qsize())
                # 과부화 방지
                if self.mCommunicationManager.mCommunicationDataQueue.qsize()>5:
                    self.mCommunicationManager.mCommunicationDataQueue.get()

                #센서값 반환
                readDataDictionary = self.mCommunicationManager.mCommunicationDataQueue.get_nowait()

                #['라즈베리파이','지그비','1단 서보', '2단 서보','이그나이터','단분리 서보']
                self.mButtonGraphList[0].checked=True
                self.mButtonGraphList[0].update_icon()

                if readDataDictionary.get("Is1stServo")!=None:
                    self.mButtonGraphList[2].checked=(readDataDictionary["Is1stServo"])
                    self.mButtonGraphList[2].update_icon()

                if readDataDictionary.get("Is2stServo")!=None:
                    self.mButtonGraphList[3].checked=(readDataDictionary["Is2stServo"])
                    self.mButtonGraphList[3].update_icon()

                if readDataDictionary.get("IsIgnition")!=None:
                    self.mButtonGraphList[4].checked=(readDataDictionary["IsIgnition"])
                    self.mButtonGraphList[4].update_icon()

                if readDataDictionary.get("IsSeperation")!=None:
                    self.mButtonGraphList[5].checked=(readDataDictionary["IsSeperation"])
                    self.mButtonGraphList[5].update_icon()

                if readDataDictionary.get("IMUData")!=None:
                    IMU = readDataDictionary["IMUData"].split(',')
                    #self.mCoordinateWidget.updateQueue((float(IMU[6]),float(IMU[7])))
                    # 속도, 각속도 위치 순
                    self.mSensorGraphList[0].updateData(IMU[0:3])
                    self.mSensorGraphList[1].updateData(IMU[3:6])





        #time.sleep(0.05)

