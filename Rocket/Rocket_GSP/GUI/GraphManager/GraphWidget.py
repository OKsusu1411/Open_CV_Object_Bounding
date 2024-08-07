import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import pyqtgraph as pg

import numpy as np

from MainWindow import MainWindow

class GraphWidget(pg.PlotWidget):

    def __init__(self):
        super().__init__()

        self.setBackground('#FFFFFF')

        self.sensorDataTime = [0]
        self.sensorData = [0]
        # PlotWidget에 데이터 업데이트
        self.plot(self.sensorDataTime, self.sensorData, clear=True, pen="black")

        self.showGrid(x=True,y=True)

        self.setStyleSheet("""border-radius: 10px;
                           padding-top: 5px;
                           padding-left: 5px""")

        self.maxTime=5       #보여주고 싶은 시간 길이
        self.updateTime=0.1  #업데이트 시간 길이
        self.presentTime=0   #현재시간
        self.translate(10,10)


    def updateData(self,IMUdata):
        self.presentTime+=self.updateTime
        self.sensorDataTime.append(self.presentTime)

        if(self.presentTime>=self.maxTime):
            self.setXRange(self.presentTime-self.maxTime,self.presentTime)
        else:
            self.setXRange(0,self.maxTime)
        
        self.sensorData.append(float(IMUdata[0]))

        if(len(self.sensorData)>=int(self.maxTime/self.updateTime)):
            self.sensorData.pop(0)
            self.sensorDataTime.pop(0)

        # PlotWidget에 데이터 업데이트
        self.plot(self.sensorDataTime, self.sensorData, clear=True, pen='black')
        self.setYRange(-10,10)

    def setFixedSize(self,widgetwidth,widgetheight):
        self.setFixedHeight(int(widgetheight))
        self.setFixedWidth(int(widgetwidth))

