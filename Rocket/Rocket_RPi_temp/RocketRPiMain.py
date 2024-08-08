import threading
from IMUmanager import IMUmanager
from RocketProtocol import RocketProtocol
import time
import asyncio

import numpy as np

IMU_ON = True
COMMUNICATION_ON = True


if __name__== "__main__":
    start = time.time()

    mRocketProtocol = RocketProtocol()
#    mRocketProtocol.Cleanup()
    mIMUmanager= IMUmanager(mRocketProtocol)

    if(IMU_ON):
        IMUthread= threading.Thread(target=mIMUmanager.getData)

        IMUthread.start()

    if(COMMUNICATION_ON):
        mIMUmanager.initConnect()
        COMMUNICATIONthread= threading.Thread(target=mIMUmanager.communicationData)
        #COMMUNICATIONthreadrepeat= threading.Thread(target=mIMUmanager.repeatData)
        COMMUNICATIONthread.start()
        #COMMUNICATIONthreadrepeat.start()
        #if(ROCKETPROTOCOL_ON):
        #    while(mRocketProtocol.AlgorithmProcess(mIMUmanager.mSensorDataQueue)):
        #        print("RocketProtocol Processing")
        #for i in range(1000):
        #    data = ["1","1","6","2","1","6","1","1","6"]
        #    data[0]= np.random.normal(0, 5)
        #    data[3]= np.random.normal(0, 5)
        #    mIMUmanager.mSensorCommunicationDataQueue.put(data)
        #    time.sleep(0.1)
#    mRocketProtocol.setSeperationServoBoolean(False)
    while not mRocketProtocol.AlgorithmProcess(mIMUmanager.mSensorDataQueue):
        continue

    print("end")
    
