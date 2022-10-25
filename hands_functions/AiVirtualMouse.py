import time
import numpy as np
import autopy
import cv2
import sys
sys.path.append("..")

# -1代表向下移动一个单位
# win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL,0,0,-1)


class Mouse():

    def __init__(self, Detector, wCam, hCam):

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
        self.delay = 0.5
        self.press_time = 0
    # print(wScr, hScr)
    # print((wCam - frameR, hCam - frameR))
    # 2. 判断食指和中指是否伸出

    def onLock(self, img):
        self.img = img
        self.fingers = self.detector.fingersStraight()
        if self.fingers[1] == 1:
            return True
        else:
            return False

    def onRun(self):

        cv2.rectangle(self.img, (self.frameR, self.frameR), (self.wCam - self.frameR,
                      self.hCam - self.frameR), (0, 255, 0), 2,  cv2.FONT_HERSHEY_PLAIN)

        x1, y1 = self.detector.lmList[8][1:]
        x2, y2 = self.detector.lmList[12][1:]
        # 3. 若只有食指伸出 则进入移动模式
        if self.fingers[1]:

            # 鼠标按下和放开
            close = self.detector.close_together()

            if self.fingers[2] and close[1] and not self.mouse_click:
                self.mouse_click = True
                autopy.mouse.toggle(autopy.mouse.Button.LEFT, True)
                self.press_time = time.time()
            elif (self.fingers[2] and not close[1] or not self.fingers[2]) and self.mouse_click:
                self.mouse_click = False
                autopy.mouse.toggle(autopy.mouse.Button.LEFT, False)

            # 另一种拖动
            TClose = self.detector.thumb_close()
            if TClose[0] == 1 and not self.toggle:
                self.toggle = True
                autopy.mouse.toggle(autopy.mouse.Button.LEFT, True)
                self.press_time = time.time()
            elif TClose[0] == 0 and self.toggle:
                self.toggle = False
                autopy.mouse.toggle(autopy.mouse.Button.LEFT, False)


            if not (self.fingers[1] and self.fingers[2] and not close[1]) and (time.time() - self.press_time > self.delay):
                    
                # 4. 坐标转换： 将食指在窗口坐标转换为鼠标在桌面的坐标
                # 鼠标坐标
                x3 = np.interp(x1, (self.frameR, self.wCam -
                            self.frameR), (0, self.wScr))
                y3 = np.interp(y1, (self.frameR, self.hCam -
                            self.frameR), (0, self.hScr))

                # smoothening values
                self.clocX = self.plocX + (x3 - self.plocX) / self.smoothening
                self.clocY = self.plocY + (y3 - self.plocY) / self.smoothening

                autopy.mouse.move(self.wScr - self.clocX, self.clocY)
                cv2.circle(self.img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
                self.plocX, self.plocY = self.clocX, self.clocY


        return self.img
