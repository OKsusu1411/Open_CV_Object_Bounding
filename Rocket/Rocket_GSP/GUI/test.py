import serial
import queue

class SerialCommunicationManager():

    #velocity_data = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        #'단분리 실행','2단 이그나이터 정지','2단 이그나이터 실행', '2단 낙하산 사출'
        #단분리 서보 기본    2단 서보 기본
        self.mSendDataQueue = queue.Queue()
        self.mReceiveDataQueue = queue.Queue()
        self.mSendDataQueue.put('D')

    def run(self):
        ser = serial.Serial(
            port='COM9',\
            baudrate=9600,\
            parity=serial.PARITY_NONE,\
            stopbits=serial.STOPBITS_ONE,\
            bytesize=serial.EIGHTBITS,\
                timeout=0)
        print(ser.portstr) #연결된 포트 확인.
        #ser.write(bytes('hello', encoding='ascii')) #출력방식1
        #ser.write(b'hello') #출력방식2
        #출력방식4
        vals = [12, 0, 0, 0, 0, 0, 0, 0, 7, 0, 36, 100] 
        ser.write(bytearray(vals))
        ser.read(ser.inWaiting()) #입력방식1
        ser.close()
        try:
            ser = serial.Serial(
            port='COM9',\
            baudrate=9600,\
            parity=serial.PARITY_NONE,\
            stopbits=serial.STOPBITS_ONE,\
            bytesize=serial.EIGHTBITS,\
                timeout=0)
            print(ser.portstr) #연결된 포트 확인.
                
            while True:
                # 송신할 데이터 입력
                # 송신 큐에 데이터가 있는 경우 데이터 전송
                if not self.mSendDataQueue.empty():
                    data_to_send = self.mSendDataQueue.get()
                    if ser.is_open:
                        ser.write(data_to_send.encode())
                        print(f"Sent: {data_to_send}")
                    else:
                        print("Serial port is not open")

                # 시리얼 포트로부터 데이터 수신
                if ser.is_open:
                    received_data = ser.readline().decode().strip()
                    if received_data:
                        #self.mReceiveDataQueue.put(received_data)
                        print(f"Received: {received_data}")
                
        finally:
            # 시리얼 포트 닫기
            if ser.is_open:
                ser.close()
                print("Serial port closed")


mSerialCommunicationManager=SerialCommunicationManager();
mSerialCommunicationManager.run()