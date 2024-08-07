
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

import pyqtgraph as pg

import numpy as np

import queue

class CoordinateWidget(pg.PlotWidget):

    def __init__(self):
        super().__init__()

        self.setBackground('#FFFFFF')

        self.plot = self.plot()
        self.data = np.array([[0, 0]])

        self.Rangeradius=5
        self.setXRange(-self.Rangeradius, self.Rangeradius)  # Set x-axis range
        self.setYRange(-self.Rangeradius, self.Rangeradius)  # Set y-axis range

        # Update the plot periodically
        #self.timer = pg.QtCore.QTimer()
        #self.timer.timeout.connect(self.update_plot)
        #self.timer.start(100)  # Update every 100 ms

        #self.mCommunicationDataQueue = queue.Queue()

    def updateQueue(self,newdata):
        new_point = [float(newdata[0]),float(newdata[1])]
        # Add a new point to the data
        self.data = np.vstack([self.data, new_point])

        # Update the plot with the new data
        self.plot.setData(self.data[:, 0], self.data[:, 1])

        if(abs(new_point[0])>abs(new_point[1])):
            if(abs(new_point[0])>self.Rangeradius):
                self.Rangeradius=abs(new_point[0])
                self.setXRange(-self.Rangeradius, self.Rangeradius)  # Set x-axis range
                self.setYRange(-self.Rangeradius, self.Rangeradius)  # Set y-axis range
        else:
            if(abs(new_point[1])>self.Rangeradius):
                self.Rangeradius=abs(new_point[1])
                self.setXRange(-self.Rangeradius, self.Rangeradius)  # Set x-axis range
                self.setYRange(-self.Rangeradius, self.Rangeradius)  # Set y-axis range    



