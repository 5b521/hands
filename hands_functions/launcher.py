import os
import webbrowser
import cv2
import autopy
from utils.key_controller import KeyController

class launcher:

    def __init__(self, detector, execute_func):
        self.is_executed = False
        self.detector = detector
        self.execute_func = execute_func
        self.FUp = None

    def onLock(self, img):
        self.img = img
        if not self.FUp:
            self.FUp = self.detector.fingersStraight()
        if self.FUp != self.detector.fingersStraight():
            # self.is_executed = False
            return False
        else:
            return True
        
    def onRun(self):
        # path =  repr(self.str)
        if not self.is_executed:
            # print('execute')
            self.execute_func()
            self.is_executed = True
        else:
            # draw the yellow for fingers
            for id in range(1, 6):
                cv2.circle(self.img, (self.detector.lmList[4 * id][1], self.detector.lmList[4 * id][2]), 15, (0, 255, 255), cv2.FILLED)
        return self.img

    def onEnd(self):
        print('here')
        self.is_executed = False
        


def exe_file_launcher(detector, path):
    return launcher(detector, lambda: os.startfile(path))


def webbrowser_launcher(detector, url):
    return launcher(detector, lambda: webbrowser.open(url))


def key_launcher(detector, key):
    kc = KeyController()
    return launcher(detector, lambda: kc.key_click(key))
