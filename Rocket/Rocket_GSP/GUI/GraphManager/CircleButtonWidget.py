
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QWidget

from PyQt5 import *
from PyQt5.Qt import *

import os

class CircleButtonWidget(QPushButton):
    def __init__(self,number):
        super().__init__()
        self.setGeometry(200, 150, 100, 100)
        self.number = number
        if number==1:
            self.setIcon(QIcon(os.path.dirname(os.path.abspath(__file__)) +"/../image/seperation.png"))
        elif number==2:
            self.setIcon(QIcon(os.path.dirname(os.path.abspath(__file__)) +"/../image/stop.png"))
        elif number==3:
            self.setIcon(QIcon(os.path.dirname(os.path.abspath(__file__)) +"/../image/fire.png"))
        elif number==4:
            self.setIcon(QIcon(os.path.dirname(os.path.abspath(__file__)) +"/../image/parachute.png"))
        else:
            self.setIcon(QIcon(os.path.dirname(os.path.abspath(__file__)) +"/../image/lock.png"))


        self.setIconSize (QSize(100,100))
        self.setStyleSheet("QPushButton{border-radius : 60px;border : 2px solid black;}\n"
                           "QPushButton:hover{background-color: rgb(177, 177, 177);}\n"
                           "QPushButton:pressed{background-color: rgb(100, 100, 100);}\n")

        self.clicked.connect(self.click)
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def setCommuincation(self, commuincation):
        self.Communication=commuincation

    def click(self):
        
        data_dict={}

        if self.number==1:
            data_dict ={"Seperation": True}
            self.Communication.mSendDataQueue.put(data_dict)
        elif self.number==2:
            data_dict ={"Ignition": False}
            self.Communication.mSendDataQueue.put(data_dict)
        elif self.number==3:
            data_dict ={"Ignition": True}
            self.Communication.mSendDataQueue.put(data_dict)
        elif self.number==4:
            data_dict ={"2ndParachute": True}
            self.Communication.mSendDataQueue.put(data_dict)
        elif self.number==5:
            data_dict ={"Seperation": False}
            self.Communication.mSendDataQueue.put(data_dict)
        elif self.number==6:
            data_dict ={"2ndParachute": False}
            self.Communication.mSendDataQueue.put(data_dict)
        print("ClickClickClickClickClickClickClickClickClick")
        #QMessageBox.about(self, "data_dict", "clicked")