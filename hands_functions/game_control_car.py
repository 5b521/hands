import sys
sys.path.append("..")
import time
import numpy as np
import HandTrackingModule as htm
import cv2
from utils.key_controller import KeyController

class car_controller:
    def __init__(self, Detector):
        self.Last_time = time.time()
        self.Pressed = False
        self.ws_Pressed = False
        self.forward_back = True
        self.detector = Detector
        self.kc = KeyController()
        # 注册新键和注册 lr (left right) fb (forward back) 为冲突按键
        self.kc.register_keymap('l', 'a')
        self.kc.register_keymap('r', 'd')
        self.kc.register_keymap('f', 'w')
        self.kc.register_keymap('b', 's')
        self.kc.register_conflicting_keys('lr', ['l', 'r'])
        self.kc.register_conflicting_keys('fb', ['f', 'b'])
        
    def press_key(self, key, t):

        if not self.kc.is_keydown(key):
            self.kc.keydown(key)
            self.Last_time = time.time()

        elif time.time() - self.Last_time > t:
            # print(t)
            self.kc.keyup(key)
    
    def onLock(self,img):
        self.img = img
        return True 

    def onRun(self):
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
                    left_right = 'l'
                else:
                    left_right = 'r'
                
                angle = abs(vector)

                if angle < 5:
                    self.kc.release_conflicting_keys('lr')
                else:
                    self.press_key(left_right, angle/360)
            
            Left_Fup = self.detector.fingersUp(self.detector.hdDict['Left'])
            Right_Fup = self.detector.fingersUp(self.detector.hdDict['Right'])

            if Right_Fup[0] and not Left_Fup[0]:
                # 前进
                if not self.kc.is_keydown('f'):
                    self.kc.keydown('f')
            elif not Right_Fup[0] and Left_Fup[0]:
                # 后退
                if not self.kc.is_keydown('b'):
                    self.kc.keydown('b')
            else:
                # 既不前进也不后退
                self.kc.release_conflicting_keys('fb')
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
            car_controller.onLock(img)
            car_controller.onRun()
                    
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        img = cv2.flip(img, 1)
        cv2.putText(img, f'fps:{int(fps)}', [15, 25],
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)
        cv2.imshow("Image", img)
        cv2.waitKey(1)