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
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(mIMUmanager.communicationData())
            except Exception as e:
                print(f"Exception in run_communication: {e}")
            finally:
                loop.close()
            
        COMMUNICATIONthread = threading.Thread(target=run_communication)
        COMMUNICATIONthread.start()
        
    while not mRocketProtocol.AlgorithmProcess(mIMUmanager.mSensorDataQueue):
        continue