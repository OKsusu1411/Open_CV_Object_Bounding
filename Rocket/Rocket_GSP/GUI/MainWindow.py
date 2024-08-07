import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from GraphManager.GraphWidget import *
from GraphManager.ProgressWidget import *
from GraphManager.CoordinateWidget import *
from GraphManager.CircleButtonWidget import *
from GraphManager.ImageCheckWidget import *
from GraphManager.WifiSignalWidget import *
from Commuincation.CommuincationManager import *
from Commuincation.SerialComuincationManager import *
from Commuincation.ThreadManager import *

import os
import time

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Rocket Ground Server Program")
        self.windowwidth=1200
        self.windowheight=1000

        #self.setBackground('#FFFFFF')
        self.setStyleSheet("background-color: #FFFFFF;")
        self.centralwidget = QWidget();
        self.setCentralWidget(self.centralwidget);
        self.maingridlayout = QGridLayout(self.centralwidget)
        self.maingridlayout.setHorizontalSpacing=10;
        self.maingridlayout.setVerticalSpacing=10;
        self.maingridlayout.setContentsMargins(10,10,10,10)
        self.maingridlayout.setRowMinimumHeight(0, 10)
###############################################################################################
        #Topbar Label Region
        
        self.mTopbarLabelString = ['CommunicationStatus','Chung-ang University','SensorStatus']
        self.mTopbarLabelList = []
        for flag in range(3):
            mTopbarLabel = QLabel(self.mTopbarLabelString[flag])
            mTopbarLabel.setAlignment(Qt.AlignHCenter)
            mTopbarLabel.setMaximumHeight(40)
            mTopbarLabel.setStyleSheet("Color : Black")
            if flag==1:
                mTopbarLabel.setMinimumWidth(int(self.windowwidth/2))
            else:
                mTopbarLabel.setMinimumWidth(int(self.windowwidth/4))
            self.maingridlayout.addWidget(mTopbarLabel, 0, flag)
            self.mTopbarLabelList.append(mTopbarLabel)
            
###############################################################################################
        #Sensor Graph Region
        self.mSensorGraphList = []
        for flag in range(2):
            mSensorGraph = GraphWidget()
            mSensorGraph.setFixedSize(self.windowwidth/4,self.windowheight/4)
            #mSensorGraph.startUpdateData()
            self.maingridlayout.addWidget(mSensorGraph, flag+1, 2)
            self.mSensorGraphList.append(mSensorGraph)
###############################################################################################
        #ProgressBar Region
        self.mProgressGraphList=[]
        self.mProgressGraphLayout = QVBoxLayout()
        self.maingridlayout.setRowMinimumHeight(3, int(self.windowheight/4)-50)
        for flag in range(2):
            mProgressBar = ProgressWidget()
            self.mProgressGraphLayout.addWidget(mProgressBar)
            self.mProgressGraphList.append(mProgressBar)

        self.mButtonLabelString = ['라즈베리파이','지그비','1단 서보', '2단 서보','이그나이터','단분리 서보']
        self.mButtonGraphList=[]      
        self.mButtonGroupWidget = QGroupBox("Button");
        self.mButtonLayout = QGridLayout(self.mButtonGroupWidget)
        self.mButtonLayout.setHorizontalSpacing=10;
        self.mButtonLayout.setVerticalSpacing=10;
        self.mButtonLayout.setContentsMargins(10,10,10,10)

        
        for flag in range(6):
            self.mButtonLabelLayout = QVBoxLayout()
            mButton = ImageCheckWidget(flag+1)
            mButtonLabel = QLabel(self.mButtonLabelString[flag])
            mButtonLabel.setAlignment(Qt.AlignHCenter)
            self.mButtonLabelLayout.addWidget(mButton)
            self.mButtonLabelLayout.addWidget(mButtonLabel)
            self.mButtonGraphList.append(mButton)
            self.mButtonLayout.addLayout(self.mButtonLabelLayout, int(flag/3), int(flag%3),Qt.AlignCenter)
        
        
        self.mProgressGraphLayout.addWidget(self.mButtonGroupWidget)
        self.maingridlayout.addLayout(self.mProgressGraphLayout, 3, 2,Qt.AlignTop)


        '''


                self.mButtonLayout1 = QHBoxLayout()
                for flag in range(3):
                    mButton = ImageCheckWidget(self.mButtonLabelString[flag])
                    self.mButtonLayout1.addWidget(mButton)
                    self.mButtonGraphList.append(mButton)

                self.mGroupButtonBox1.setLayout(self.mButtonLayout1)
                self.mProgressGraphLayout.addWidget(self.mGroupButtonBox1,Qt.AlignCenter)

                self.mGroupButtonBox2 = QGroupBox("")
                
                self.mGroupButtonBox2.setStyleSheet("QGroupBox{\n"
                            "    margin-top: 10px;\n"
                            "    margin-bottom: 10px;\n"
                            "}\n")
                
                self.mButtonLayout2 = QHBoxLayout()
                for flag in range(3):
                    mButton = ImageCheckWidget(self.mButtonLabelString[flag+3])
                    self.mButtonLayout2.addWidget(mButton)
                    self.mButtonGraphList.append(mButton)

                self.mGroupButtonBox2.setLayout(self.mButtonLayout2)
                self.mProgressGraphLayout.addWidget(self.mGroupButtonBox2,Qt.AlignCenter)
        '''
        #self.maingridlayout.addLayout(self.mProgressGraphLayout, 3, 2,Qt.AlignTop)
###############################################################################################
        #ForceButton region
        
        self.mForceGroup = QGroupBox("ForceButton")
        self.mForceGroupLayout = QVBoxLayout()

        self.mForceButtonList=[]
        self.mGroupForceButtonBox = QWidget()
        self.mForceButtonLayout = QHBoxLayout()
        for flag in range(4):
            mButton = CircleButtonWidget(flag+1)
            self.mForceButtonLayout.addWidget(mButton)
            self.mForceButtonList.append(mButton)

        self.mGroupForceButtonBox.setLayout(self.mForceButtonLayout)

        self.mForceLabelString = ['단분리 실행','2단 이그나이터 정지','2단 이그나이터 실행', '2단 낙하산 사출']
        self.mForceLabelList=[]
        self.mGroupForceLabelBox = QWidget()
        self.mForceLabelLayout = QHBoxLayout()
        for flag in range(4):
            mLabel = QLabel(self.mForceLabelString[flag])
            mLabel.setAlignment(Qt.AlignHCenter)
            self.mForceLabelLayout.addWidget(mLabel)
            self.mForceLabelList.append(mLabel)

        self.mGroupForceLabelBox.setLayout(self.mForceLabelLayout)

        self.mForceGroup.setLayout(self.mForceGroupLayout)
        self.mForceGroupLayout.addWidget(self.mGroupForceButtonBox)
        self.mForceGroupLayout.addWidget(self.mGroupForceLabelBox)

        self.maingridlayout.addWidget(self.mForceGroup, 4, 1)
###############################################################################################
        #CheckList Region
        self.mCheckBoxList=[]
        self.mCheckBoxLayout = QVBoxLayout()
        self.mGroupCheckBox = QGroupBox("CheckList")
        for flag in range(5):
            mCheckBox = QCheckBox('체크리스트'+str(flag), self)
            mCheckBox.setStyleSheet("Color : Black")
            self.mCheckBoxLayout.addWidget(mCheckBox)
            self.mCheckBoxList.append(mCheckBox)

        self.mGroupCheckBox.setLayout(self.mCheckBoxLayout)
        self.maingridlayout.addWidget(self.mGroupCheckBox, 4, 0)
###############################################################################################
        #RocketLock Region
        self.mStatusLabelList=[]
        self.mGroupStatusBox = QGroupBox("RocketLock")
        self.mGroupStatusBox.setMinimumHeight(int(self.windowheight*5/26))
        self.mLockGroupLayout = QVBoxLayout()
        self.mGroupStatusBox.setLayout(self.mLockGroupLayout)

        self.mLockButtonList=[]
        self.mGroupLockButtonBox = QWidget()
        self.mLockButtonLayout = QHBoxLayout()
        for flag in range(2):
            mButton = CircleButtonWidget(flag+5)
            self.mLockButtonLayout.addWidget(mButton)
            self.mLockButtonList.append(mButton)

        self.mGroupLockButtonBox.setLayout(self.mLockButtonLayout)

        self.mLockLabelString = ['단분리 잠금', '2단 낙하산 잠금']
        self.mLockLabelList=[]
        self.mGroupLockLabelBox = QWidget()
        self.mLockLabelLayout = QHBoxLayout()
        for flag in range(2):
            mLabel = QLabel(self.mLockLabelString[flag])
            mLabel.setAlignment(Qt.AlignHCenter)
            self.mLockLabelLayout.addWidget(mLabel)
            self.mLockLabelList.append(mLabel)

        self.mGroupLockLabelBox.setLayout(self.mLockLabelLayout)
        self.mLockGroupLayout.addWidget(self.mGroupLockButtonBox)
        self.mLockGroupLayout.addWidget(self.mGroupLockLabelBox)

        self.maingridlayout.addWidget(self.mGroupStatusBox, 4, 2)
###############################################################################################
        #Coordinate Region
        self.mCoordinateWidget=CoordinateWidget();
        self.maingridlayout.addWidget(self.mCoordinateWidget, 3, 0)
###############################################################################################

        #self.mWifiSignalWidget=WifiSignalWidget()
        #self.maingridlayout.addWidget(self.mWifiSignalWidget, 1, 0)

        self.mCommuincationStatusLabel=QLabel('timedelay')
        self.maingridlayout.addWidget(self.mCommuincationStatusLabel, 2, 0)

###############################################################################################

        self.mRocketImage = QPixmap(os.path.dirname(os.path.abspath(__file__)) +'./image/rimage.jpg')
        #self.mRocketImage = self.mRocketImage.scaled(500, 1000, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        lbl_img = QLabel()
        lbl_img.setPixmap(self.mRocketImage)
        lbl_img.setScaledContents(True)
        self.maingridlayout.addWidget(lbl_img, 1, 1,3,1) 
###############################################################################################
        self.setGeometry(0, 0, self.windowwidth, self.windowheight)
        self.setFixedSize(self.windowwidth, self.windowheight)

        self.mCommunicationManager = CommunicationManager(self)
        self.mCommunicationManager.velocity_data.connect(self.mSensorGraphList[0].updateData)
        self.mCommunicationManager.w_velocity_data.connect(self.mSensorGraphList[1].updateData)
        self.mCommunicationManager.position_data.connect(self.mCoordinateWidget.updateQueue)

        self.mCommunicationManager.Is1stServo_data.connect(self.mButtonGraphList[2].update_icon)
        self.mCommunicationManager.Is2stServo_data.connect(self.mButtonGraphList[3].update_icon)
        self.mCommunicationManager.IsIgnition_data.connect(self.mButtonGraphList[4].update_icon)
        self.mCommunicationManager.IsSeperation_data.connect(self.mButtonGraphList[5].update_icon)
        self.mCommunicationManager.Time_data.connect(self.mCommuincationStatusLabel.setText)
        
        self.mCommunicationManager.start()

        #self.mSerialCommunicationManager = SerialCommunicationManager(self)
        #self.mSerialCommunicationManager.start()
       # self.mSerialCommunicationManager.IsZigbee_data.connect(self.mButtonGraphList[1].update_icon)
        for mButton in self.mForceButtonList:
            mButton.setCommuincation(self.mCommunicationManager)




if __name__=="__main__":
    app = QApplication(sys.argv)
    mainwindow = MainWindow()

    mainwindow.show()

    fontDB = QFontDatabase()
    fontDB.addApplicationFont('./font/NotoSansKR-Regular.ttf')
    app.setFont(QFont('NotoSansKR-Regular'))

    app.exec()

