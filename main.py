import cv2
import HandTrackingModule as htm
import time
from hands_functions import AiVirtualMouse as mouse
from hands_functions import handsMove
from hands_functions import volumeControl
from features_record import hand_recognition as hr
from hands_functions import page
from hands_functions import game_control_car
from hands_functions import launcher


def main(mode = 'office'):

    pTime = 0
    cap = cv2.VideoCapture(0)  # 若使用笔记5本自带摄像头则编号为0  若使用外接摄像头 则更改为1或其他编号

    wCam = int(cap.get(3))
    hCam = int(cap.get(4))

    if mode == 'office':
        detector = htm.handDetector(maxHands=1)
    elif mode == 'game':
        detector = htm.handDetector(maxHands=2)
    gesture_map = {
        'mouse': mouse.Mouse(wCam, hCam, detector),
        'palm': handsMove.HandsMove(detector, page.page_move, lambda img: detector.fingersStraight()[1] == 1, True),
        'volume': volumeControl.systemVolumeControler(detector),
        'car': game_control_car.car_controller(detector),
        'web': launcher.exe_file_launcher(r'D:\tencent\Bin\QQScLauncher.exe', detector),
        'QQ': launcher.webbrowser_launcher(r'https://www.bilibili.com/', detector),
    }
    start_func = None
    lock_func = None
    run_func = None
    end_func = None
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
                if gesture in gesture_map:
                    # 如果存在 onStart 方法
                    if hasattr(gesture_map[gesture], 'onStart'):
                        start_func = gesture_map[gesture].onStart
                    lock_func = gesture_map[gesture].onLock
                    run_func = gesture_map[gesture].onRun
                    # 如果存在 onEnd 方法
                    if hasattr(gesture_map[gesture], 'onEnd'):
                        end_func = gesture_map[gesture].onEnd

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
                    end_func = None
            frame_count = 0
        else:
            if frame_count > 10:
                lock = False
                start_func = None
                lock_func = None
                run_func = None
                frame_count = 0
                if end_func:
                    end_func()
                end_func = None
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