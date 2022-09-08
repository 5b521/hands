import sys
sys.path.append("..")
import cv2
import HandTrackingModule as htm
import autopy
import numpy as np
import time

# -1代表向下移动一个单位
# win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL,0,0,-1)


class Mouse():

    def __init__(self,wCam,hCam,Detector):

        self.frameR = 150
        self.smoothening = 5
        self.wCam = wCam
        self.hCam = hCam
        self.plocX, self.plocY = 0, 0
        self.clocX, self.clocY = 0, 0
        self.mouse_click = False
        self.detector = Detector
        self.wScr, self.hScr = autopy.screen.size()
        self.toggle = False
    # print(wScr, hScr)
    # print((wCam - frameR, hCam - frameR))
    # 2. 判断食指和中指是否伸出
    def is_mouse_gesture(self, img):
        self.img = img
        self.fingers = self.detector.fingersStraight()
        if self.fingers[1] == 1:
            return True
        else:
            return False
    
    def move_mouse(self):
        
        cv2.rectangle(self.img, (self.frameR, self.frameR), (self.wCam - self.frameR, self.hCam - self.frameR), (0, 255, 0), 2,  cv2.FONT_HERSHEY_PLAIN)

        x1, y1 = self.detector.lmList[8][1:]
        x2, y2 = self.detector.lmList[12][1:]
        # 3. 若只有食指伸出 则进入移动模式
        if self.fingers[1] and self.fingers[2] == False:
            TClose = self.detector.thumb_close()
            # 4. 坐标转换： 将食指在窗口坐标转换为鼠标在桌面的坐标
            # 鼠标坐标

            if TClose[0] == 1 and not self.toggle:
                self.toggle = True
                autopy.mouse.toggle(autopy.mouse.Button.LEFT, True)
            elif TClose[0] == 0 and self.toggle:
                self.toggle = False
                autopy.mouse.toggle(autopy.mouse.Button.LEFT, False)

            x3 = np.interp(x1, (self.frameR, self.wCam - self.frameR), (0, self.wScr))
            y3 = np.interp(y1, (self.frameR, self.hCam - self.frameR), (0, self.hScr))

            # smoothening values
            self.clocX = self.plocX + (x3 - self.plocX) / self.smoothening
            self.clocY = self.plocY + (y3 - self.plocY) / self.smoothening

            autopy.mouse.move(self.wScr - self.clocX, self.clocY)
            cv2.circle(self.img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            self.plocX, self.plocY = self.clocX, self.clocY

        # 5. 若是食指和中指都伸出 则检测指头距离 距离够短则对应鼠标点击
        elif self.fingers[1] and self.fingers[2]:
            close = self.detector.close_together()
            # if close[1]:
            #     print(close[1])
            if close[1] and not self.mouse_click:
                # cv2.circle(img, (pointInfo[4], pointInfo[5]),
                #            15, (0, 255, 0), cv2.FILLED)
                autopy.mouse.click()
                self.mouse_click = True
            elif not close[1]:
                self.mouse_click = False
        
        return self.img


