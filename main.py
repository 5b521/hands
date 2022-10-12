from cProfile import run
import cv2
import HandTrackingModule as htm
import autopy
import numpy as np
import time
from hands_functions import AiVirtualMouse as mouse
from hands_functions import handsMove
from hands_functions import volumeControl
from features_record import hand_recognition as hr
from hands_functions import page
from hands_functions import game_control_car


def main(mode = 'office'):

    pTime = 0
    cap = cv2.VideoCapture(0)  # 若使用笔记5本自带摄像头则编号为0  若使用外接摄像头 则更改为1或其他编号

    wCam = int(cap.get(3))
    hCam = int(cap.get(4))

    if mode == 'office':
        detector = htm.handDetector(maxHands=1)
    elif mode == 'game':
        detector = htm.handDetector(maxHands=2)
    mouse_control = mouse.Mouse(wCam, hCam, detector)
    hands_move_control = handsMove.HandsMove(detector, page.page_move, lambda img: detector.fingersStraight()[1] == 1, True)
    volume_control = volumeControl.systemVolumeControler(detector)
    car_controller = game_control_car.car_controller(detector)
    lock_func = None
    run_func = None
    lock = False
    frame_count = 0
    gesture = ''

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
                    run_func = mouse_control.move_mouse
                elif (gesture == 'palm'):
                    start_func = hands_move_control.start
                    lock_func = hands_move_control.isLock
                    run_func = hands_move_control.handleChange
                elif (gesture == 'volume'):
                    lock_func = volume_control.is_volume_control
                    run_func = volume_control.run_volume_control
                elif gesture == 'car':
                    lock_func = car_controller.is_car_controller
                    run_func = car_controller.car_control
                if lock_func and run_func:
                    if start_func:
                        start_func(img)
                    lock = lock_func(img)
                    img = run_func()
                    
            else:
                lock = lock_func(img)
                if lock:
                    img = run_func()
                else:
                    lock_func = None
                    run_func = None
                    start_func = None
            frame_count = 0
        else:
            if frame_count > 10:
                lock = False
                start_func = None
                lock_func = None
                run_func = None
                frame_count = 0
                if gesture == 'palm':
                    hands_move_control.handleEnd()

            frame_count += 1

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, f'fps:{int(fps)}', [15, 25],
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)
        cv2.imshow("Image", img)
        cv2.waitKey(1)


if __name__ == "__main__":
    main('game')
    # main('office')