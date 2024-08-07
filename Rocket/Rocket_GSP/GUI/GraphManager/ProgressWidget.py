
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QWidget

from PyQt5 import *
from PyQt5.Qt import *

import pyqtgraph as pg

class ProgressWidget(QProgressBar):
    def __init__(self) -> None:
        super().__init__()

        self.setValue(70)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("QProgressBar{\n"
                    "    background-color: rgb(213, 235, 248);\n"
                    "    border-style: 1px solid black;\n"
                    "    border-bottom-right-radius: 10px;\n"
                    "    border-bottom-left-radius: 10px;\n"
                    "    border-top-right-radius: 10px;\n"
                    "    border-top-left-radius: 10px;\n"
                    "    text-align: center;\n"
                    "}\n"
                    "QProgressBar::chunk{\n"
                    "    border-style: 1px solid black;\n"
                    "    border-bottom-right-radius: 10px;\n"
                    "    border-bottom-left-radius: 10px;\n"
                    "    border-top-right-radius: 10px;\n"
                    "    border-top-left-radius: 10px;\n"
                    "    background-color: qlineargradient(spread:pad, x1:0, y1:0.511364, x2:1, y2:0.523, stop:0 rgba(12, 71, 240, 255), stop:1 rgba(43, 151, 221, 255));\n"
                    "}\n"
                    "\n")