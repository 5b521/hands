from asyncio.windows_events import NULL
import sys
sys.path.append("..")
import time
import numpy as np
import HandTrackingModule as htm
import cv2
import pydirectinput

import ctypes

SendInput = ctypes.windll.user32.SendInput

# C struct redefinitions 
PUL = ctypes.POINTER(ctypes.c_ulong)
class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time",ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                 ("mi", MouseInput),
                 ("hi", HardwareInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

# Actuals Functions

def PressKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput( 0, hexKeyCode, 0x0008, 0, ctypes.pointer(extra) )
    x = Input( ctypes.c_ulong(1), ii_ )
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def ReleaseKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput( 0, hexKeyCode, 0x0008 | 0x0002, 0, ctypes.pointer(extra) )
    x = Input( ctypes.c_ulong(1), ii_ )
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


class car_controller:
    def __init__(self, Detector):
        # self.Last_left_right = 'a'
        self.Last_left_right = NULL
        self.Last_time = time.time()
        self.Pressed = False
        self.ws_Pressed = False
        self.forward_back = True
        self.detector = Detector
    
    def press_key(self,key,t):
        # if self.Last_left_right != key:
        #     pydirectinput.keyUp(self.Last_left_right)
        if t == 0:
            if self.Pressed:
                ReleaseKey(self.Last_left_right)
                self.Pressed = False

            return 

        if self.Last_left_right != key :
            if self.Pressed:
                ReleaseKey(self.Last_left_right)
                PressKey(key)
                self.Last_time = time.time()
                self.Last_left_right = key
            else:
                self.Pressed = True
                PressKey(key)
                self.Last_time = time.time()
                self.Last_left_right = key

        elif not self.Pressed :
            # pydirectinput.keyUp(self.Last_left_right)
            # ReleaseKey(self.Last_left_right)
            self.Last_left_right = key
            # pydirectinput.keyDown(key)
            PressKey(key)

            self.Last_time = time.time()
            self.Pressed = True
        elif time.time() - self.Last_time > t :
            # pydirectinput.keyUp(key)
            ReleaseKey(key)
            self.Pressed = False    
    
    def is_car_controller(self,img):
        self.img = img
        return True 

    def car_control(self):
        # tt = time.time()
        # print('here')
        # if tt - self.Last_time > 5:
        #     pydirectinput.keyDown('y')
        #     pydirectinput.keyUp('y')
        #     self.Last_time = tt

        if self.detector.hdDict["Detected"] == 2:
            vector = self.detector.findEvelation('Left', 6, 'Right', 6, self.img, True)
            if vector:
                if vector > 0:
                    left_right = 0x1E
                else:
                    left_right = 0x20
                
                angle = abs(vector)

                if angle < 5:
                    self.press_key(left_right,0)
                else:
                    self.press_key(left_right,angle/360)
            
            Left_Fup = self.detector.fingersUp(self.detector.hdDict['Left'])
            Right_Fup = self.detector.fingersUp(self.detector.hdDict['Right'])

            if Right_Fup[0] and not Left_Fup[0]:
                if not self.ws_Pressed:
                    self.ws_Pressed = True
                    self.forward_back = True
                    PressKey(0x11)
                else:
                    if not self.forward_back:
                        ReleaseKey(0x1f)
                        self.forward_back = True
                        PressKey(0x11)
            elif not Right_Fup[0] and Left_Fup[0]:
                if not self.ws_Pressed:
                    self.ws_Pressed = True
                    self.forward_back = False
                    PressKey(0x1f)
                else:
                    if self.forward_back:
                        ReleaseKey(0x11)
                        self.forward_back = False
                        PressKey(0x1f)
            else:
                if self.ws_Pressed:
                    if self.forward_back:
                        ReleaseKey(0x11)
                        self.ws_Pressed = False
                    else:
                        self.ws_Pressed =False
                        ReleaseKey(0x1f)
            # print('left:',Left_Fup[0],"right",Right_Fup[0])
        return self.img

## shift 0x2A  w 0x11 s 0x1f a 0x1E d 0x20
if __name__ == "__main__":
    pTime = 0
    cap = cv2.VideoCapture(0)  # 若使用笔记5本自带摄像头则编号为0  若使用外接摄像头 则更改为1或其他编号
    detector = htm.handDetector(maxHands=2)
    car_controller = car_controller(detector)

    while True:

        success, img = cap.read()
        # 1. 检测手部 得到手指关键点坐标
        img = detector.findHands(img)
        lmList = detector.findPosition(img, draw=False)

        if len(lmList) != 0:

            # if mouse_control.is_mouse_gesture(img):
            #     img = mouse_control.move_mouse()
            car_controller.is_car_controller(img)
            car_controller.car_control()
                    
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        img = cv2.flip(img, 1)
        cv2.putText(img, f'fps:{int(fps)}', [15, 25],
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)
        cv2.imshow("Image", img)
        cv2.waitKey(1)