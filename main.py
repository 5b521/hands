from cProfile import run
import cv2
import HandTrackingModule as htm
import autopy
import numpy as np
import time
from hands_functions import AiVirtualMouse as mouse
from features_record import hand_recognition as hr


def main():

    pTime = 0
    cap = cv2.VideoCapture(0)  # 若使用笔记本自带摄像头则编号为0  若使用外接摄像头 则更改为1或其他编号

    wCam = int(cap.get(3))
    hCam = int(cap.get(4))

    detector = htm.handDetector(maxHands=1)
    mouse_control = mouse.Mouse(wCam, hCam, detector)
    lock_func = None
    run_func = 0
    lock = False

    while True:

        success, img = cap.read()
        # 1. 检测手部 得到手指关键点坐标
        img = detector.findHands(img)
        lmList = detector.findPosition(img, draw=False)

        if len(lmList) != 0:

            # if mouse_control.is_mouse_gesture(img):
            #     img = mouse_control.move_mouse()
            if not lock:
                gesture = hr.hand_recognition(detector)
                if (gesture == 'mouse'):
                    lock_func = mouse_control.is_mouse_gesture
                    lock = lock_func(img)
                    run_func = mouse_control.move_mouse
                    img = mouse_control.move_mouse()
            else:
                lock = lock_func(img)
                if lock:
                    img = run_func()
        else:
            lock = False

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, f'fps:{int(fps)}', [15, 25],
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)
        cv2.imshow("Image", img)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()
