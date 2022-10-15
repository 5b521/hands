import os
import webbrowser
import cv2
from features_record import hand_recognition


class launcher:

    def __init__(self, detector, execute_func):
        self.is_executed = False
        self.detector = detector
        self.execute_func = execute_func
        self.FUp = None

    def lock_func(self,img):
        self.img = img
        if not self.FUp:
            self.FUp = self.detector.fingersUp()
        if self.FUp != self.detector.fingersUp():
            self.is_executed = False
            return False
        else:
            return True
        
    def execute(self):
        # path =  repr(self.str)
        if not self.is_executed:
            print('execute')
            self.execute_func()
            self.is_executed = True
        else:
            # draw the yellow for fingers
            for id in range(1, 6):
                cv2.circle(self.img, (self.detector.lmList[4 * id][1], self.detector.lmList[4 * id][2]), 15, (0, 255, 255), cv2.FILLED)
        return self.img

    def handleEnd(self):
        self.is_executed = False
        


def exe_file_launcher(path, detector):
    return launcher(detector, lambda: os.startfile(path))


def webbrowser_launcher(url, detector):
    return launcher(detector, lambda: webbrowser.open(url))
        
