from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QWidget

from PyQt5 import *
from PyQt5.Qt import *

import os

class ImageCheckWidget(QPushButton):
    def __init__(self,number):
        super().__init__()
        self.setGeometry(200, 150, 100, 100)
        if number==1:
            self.setIcon(QIcon(os.path.dirname(os.path.abspath(__file__)) +"/../image/raspberry.png"))
        elif number==2:
            self.setIcon(QIcon(os.path.dirname(os.path.abspath(__file__)) +"/../image/zigbee.svg"))
        elif number==3:
            self.setIcon(QIcon(os.path.dirname(os.path.abspath(__file__)) +"/../image/motor1.png"))
        elif number==4:
            self.setIcon(QIcon(os.path.dirname(os.path.abspath(__file__)) +"/../image/motor2.png"))
        elif number==5:
            self.setIcon(QIcon(os.path.dirname(os.path.abspath(__file__)) +"/../image/fire.png"))
        else:
            self.setIcon(QIcon(os.path.dirname(os.path.abspath(__file__)) +"/../image/seperation.png"))

        self.setIconSize (QSize(40,40))

        self.clicked.connect(self.click)
        self.setStyleSheet("QPushButton{\n"
            "    padding-top: 5px;\n"
            "    padding-bottom: 5px;\n"
            "    background-color: rgb(100, 100, 100);"
            "}\n")
        self.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.update_icon(False)

    def update_icon(self,data):
        self.checked=data
        if self.checked:
            self.setStyleSheet("QPushButton{\n"
                "    padding-top: 5px;\n"
                "    padding-bottom: 5px;\n"
                "    background-color: rgb(255, 255, 255);"
                "}\n")
        else:
            self.setStyleSheet("QPushButton{\n"
                "    padding-top: 5px;\n"
                "    padding-bottom: 5px;\n"
                "    background-color: rgb(100, 100, 100);"
                "}\n")

    def click(self):
        self.checked = not self.checked
        self.update_icon(self.checked)