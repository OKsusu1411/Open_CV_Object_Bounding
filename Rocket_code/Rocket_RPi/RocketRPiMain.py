import threading
from IMUmanager import IMUmanager
from RocketProtocol import RocketProtocol
import time
import asyncio

import numpy as np

IMU_ON = False
COMMUNICATION_ON = True
ROCKETPROTOCOL_ON = False

if __name__== "__main__":
    start = time.time()

    mRocketProtocol = RocketProtocol()
    mIMUmanager= IMUmanager(mRocketProtocol)

    if(IMU_ON):
        IMUthread= threading.Thread(target=mIMUmanager.getData)
        
        IMUthread.start()

    if(COMMUNICATION_ON):
        def run_communication():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(mIMUmanager.communicationData())
            loop.close()
            
        COMMUNICATIONthread = threading.Thread(target=run_communication)
        COMMUNICATIONthread.start()
        
    #if(ROCKETPROTOCOL_ON):
    #    while(mRocketProtocol.AlgorithmProcess(mIMUmanager.mSensorDataQueue)):
    #        print("RocketProtocol Processing")
    
    for i in range(1000):
        data = ["1","1","6","2","1","6","1","1","6"]
        data[0]= np.random.normal(0, 5)
        data[3]= np.random.normal(0, 5)
        mIMUmanager.mSensorCommunicationDataQueue.put(data)
        time.sleep(0.1)
    