import cv2
import HandTrackingModule as htm
import time
from features_record import hand_recognition as hr
from hands_functions import launcher
from gesture_dl.lstm_model import SequenceClassificationPred


MODEL_PATH = './gesture_dl/model/ipn_model_new_73.pt'
GESTURE_NAME = './gesture_dl/data/IPN_Hand/id2gesture_new.csv'
model = SequenceClassificationPred(MODEL_PATH, gesture_name_map=GESTURE_NAME)

def handTrack(register_map, mode='office'):

    cap = cv2.VideoCapture(0)  # 若使用笔记5本自带摄像头则编号为0  若使用外接摄像头 则更改为1或其他编号

    if mode == 'office':
        detector = htm.handDetector(maxHands=1)
    elif mode == 'game':
        detector = htm.handDetector(maxHands=2)

    gesture_map = register_map(cap, detector)

    pTime = 0
    mapChancedLauncher = launcher.launcher(detector, lambda: None)
    start_func = None
    lock_func = None
    run_func = None
    end_func = None
    lock = False
    current_map = gesture_map
    current_map_name = 'default'
    frame_count = 0
    gesture = ''
    gesture_name = ''
    while True:

        success, img = cap.read()
        # 1. 检测手部 得到手指关键点坐标
        img = detector.findHands(img)
        lmList = detector.findPosition(img, draw=False)

        if len(lmList) != 0:

            # if mouse_control.is_mouse_gesture(img):
            #     img = mouse_control.move_mouse()
            if not lock:
                results = detector.results.multi_hand_world_landmarks
                gesture_name, frames = model.send2(results[0], detector.fingersStraight(), detector.fingersUp())
                gesture = hr.hand_recognition(detector)
                # 如果要退出
                if 'exit' in current_map and current_map['exit'] == gesture:
                    current_map = gesture_map
                    current_map_name = 'default'
                    lock_func = mapChancedLauncher.onLock
                    run_func = mapChancedLauncher.onRun
                    print('exit')
                else:
                    if gesture_name in current_map:
                    
                        # 如果存在 onStart 方法
                        current_map[gesture_name](gesture_name)
                        
                    elif gesture in current_map :
                        # 如果嵌套
                        if isinstance(current_map[gesture], dict):
                            current_map = current_map[gesture]
                            current_map_name = gesture
                            # lock_func = mapChancedLauncher.onLock
                            # run_func = mapChancedLauncher.onRun
                            print('enter', gesture)
                        else:
                            # 如果存在 onStart 方法
                            if hasattr(current_map[gesture], 'onStart'):
                                start_func = current_map[gesture].onStart
                            lock_func = current_map[gesture].onLock
                            run_func = current_map[gesture].onRun
                            # 如果存在 onEnd 方法
                            if hasattr(current_map[gesture], 'onEnd'):
                                end_func = current_map[gesture].onEnd

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
                    gesture = ''
            frame_count = 0
        else:
            if frame_count > 10:
                gesture_name, frames = model.clear_queue()
                lock = False
                lock_func = None
                run_func = None
                start_func = None
                end_func = None
                gesture = ''
                frame_count = 0
                if end_func:
                    end_func()
                end_func = None
            frame_count += 1

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, f'[{current_map_name}][{gesture}] fps:{int(fps)}', [15, 25],
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)
        cv2.imshow("Image", img)
        cv2.waitKey(1)


if __name__ == "__main__":
    handTrack('game')
    # main('office')