# import libs, torch first if run on macOS
import torch
import mediapipe as mp
import numpy as np
import cv2
import time

from lstm_model import SequenceClassificationPred
from data import HandTrackingModule as htm


NUM_MAX_HANDS = 1
detector = htm.handDetector(maxHands=NUM_MAX_HANDS, detectionCon = 0.5, trackCon = 0.5)
mp_hands = detector.mpHands
mp_hands_handle = detector.hands
mp_draw = detector.mpDraw

# load model
# MODEL_PATH = './model/less_0123_relu.pt'
# model = StaticClassificationPred(MODEL_PATH, num_classes=4)
MODEL_PATH = './gesture_dl/model/ipn_model_new_73.pt'
GESTURE_NAME = './gesture_dl/data/IPN_Hand/id2gesture_new.csv'
model = SequenceClassificationPred(MODEL_PATH, gesture_name_map=GESTURE_NAME)

def main(mode = 'office'):

    pTime = 0
    cap = cv2.VideoCapture(0)  # 若使用笔记5本自带摄像头则编号为0  若使用外接摄像头 则更改为1或其他编号

    if mode == 'office':
        detector = htm.handDetector(maxHands=1)
    elif mode == 'game':
        detector = htm.handDetector(maxHands=2)
    
    # gesture_map = {
        
    #     # 'key': launcher.key_launcher(detector, 'f11'),
    # }
    # start_func = None
    # lock_func = None
    # run_func = None
    # end_func = None
    # lock = False
    # current_map = gesture_map
    # frame_count = 0
    # gesture = ''
    last_gesture_name1 = None
    last_gesture_name2 = None
    fram_count = 0
    while True:

        success, img = cap.read()
        # 1. 检测手部 得到手指关键点坐标
        img = detector.findHands(img)
        raw_results = detector.results
        lmList = detector.findPosition(img, draw=False)
    
        if len(lmList) != 0:
            results = raw_results.multi_hand_world_landmarks
            gesture_name, frames = model.send2(results[0], detector.fingersStraight(), detector.fingersUp())
            if gesture_name:
                if gesture_name == "Click with one finger":
                    gesture_name = 'Click'
                last_gesture_name2 = last_gesture_name1
                last_gesture_name1 = gesture_name
                print(f"{frames} frames are predicted as {gesture_name}")
            fram_count = 0
            # if mouse_control.is_mouse_gesture(img):
            #     img = mouse_control.move_mouse()
        else:
            if fram_count >= 10:
                fram_count -= 1
                gesture_name, frames = model.clear_queue()
                if gesture_name:
                    print(f"{frames} frames are predicted as {gesture_name}")
            fram_count += 1
        if last_gesture_name1:
            # cv2.putText(img, '...', [15, 60],
            #         cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)
            cv2.putText(img, f'this gesture:{last_gesture_name1}', [15, 60],
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)
            # cv2.putText(img, f'last gesture:{last_gesture_name2}', [15, 90],
            #         cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, f'fps:{int(fps)}', [15, 25],
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)
        cv2.imshow("Image", img)
        cv2.waitKey(1)


if __name__ == "__main__":
    # main('game')
    main('office')