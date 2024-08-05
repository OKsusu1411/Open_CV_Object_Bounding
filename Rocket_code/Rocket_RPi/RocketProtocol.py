import RPi.GPIO as GPIO


from time import sleep
import time


class RocketProtocol:
    def __init__(self):
        GPIO.setmode(GPIO.BOARD)
        ##initial
        self.mSeperationServoPin = 0 ##change
        #GPIO.setup(self.mSeperationServoPin,GPIO.OUT)
        #self.mSeperationServo = GPIO.PWM(self.mSeperationServoPin, 50);
        #self.mSeperationServo.start(0)

        self.m2ndServoPin = 32
        #GPIO.setup(self.m2ndServoPin,GPIO.OUT)
        #self.m2ndServo = GPIO.PWM(self.m2ndServoPin, 50);
        #self.m2ndServo.start(0)

        self.mIgnitionRelayPin = 0 ##change
        #self.mIgnitionRelay = GPIO.setup(self.mIgnitionRelayPin, GPIO.OUT);
        #GPIO.output(self.mIgnitionRelay,False)

        self.SERVO_MAX_DUTY = 12.5 # servo Max
        self.SERVO_MIN_DUTY = 2.5

        self.RocketStep=0
        self.RocketMaxStep=4

        # 이그나이터 상태, 단분리 상태, 1단 2단 서보 상태
        self.IsIgnition=False
        self.IsSeperation=True
        self.Is1stServo=False
        self.Is2stServo=True

        self.SERVORELEASE=43;
        self.SERVOLOCK=10;

    def set2ndServoPos(self,degree):
        if degree > 180:
            degree = 180

        duty =self.SERVO_MIN_DUTY+(degree*(self.SERVO_MAX_DUTY-self.SERVO_MIN_DUTY)/180.0)
        self.m2ndServo.ChangeDutyCycle(duty)

    def set2ndServoBoolean(self,booldata):
        self.Is2stServo=booldata
        if self.Is2stServo:
            self.set2ndServoPos(self.SERVORELEASE);
        else:
            self.set2ndServoPos(self.SERVOLOCK);

    def setSeprationServoPos(self,degree):
        if degree > 180:
            degree = 180

        duty =self.SERVO_MIN_DUTY+(degree*(self.SERVO_MAX_DUTY-self.SERVO_MIN_DUTY)/180.0)
        self.mSeperationServo.ChangeDutyCycle(duty)
    
    def setSeprationServoBoolean(self,booldata):
        self.IsSeperation=booldata
        if self.IsSeperation:
            self.setSeprationServoPos(self.SERVORELEASE);
        else:
            self.setSeprationServoPos(self.SERVOLOCK);
    
    def Algorithm1Check(self):
        # 1차 점화 완료 체크
        # 가속도 Global z값 확인
        if False:
            self.RocketStep+=1
            return True
        else:
            return False    
        
    def Algorithm2Check(self):
        # 2차 점화전 시작 체크
        # 속도 Global z값 확인(1m/s 이상 True)
        # 각속도 Global x,y값 확인
        if False:
            self.RocketStep+=1
            return True
        else:
            return False    
      
    def Algorithm3Check(self):
        # 2차 점화후 완료 체크
        # 알고리즘2 체크후 2초동안 확인, 2초 지나면 점화 중지
        # 가속도 Global z값 확인(가속도가 높아지지 않으면 점화 안된 것)
        # 속도 Global z값 확인(1m/s 이상 유지해야함)
        # 각속도 Global x,y값 확인( 로켓 자세가 이상하게 떨어지면 점화 중지 )
        if False:
            self.RocketStep+=1
            return True
        else:
            return False      
     
    def Algorithm4Check(self):
        # 2차 추력 완료 체크 == 알고리즘 1번과 같음
        if False:
            self.RocketStep+=1
            return True
        else:
            return False      
    
    def AlgorithmProcess(self,mSensorqueue):
        # 알고리즘 전체

        if(self.RocketStep==0):
            print("Rocket step1")
            self.Algorithm1Check()

        elif(self.RocketStep==1):
            print("Rocket step2")
            self.Algorithm2Check()

        elif(self.RocketStep==2):
            print("Rocket step3")
            self.Algorithm3Check()

        elif(self.RocketStep==3):
            print("Rocket step4")
            self.Algorithm4Check()

        else:
            print("Rocket finished")

        return self.RocketStep>=self.RocketMaxStep    
    