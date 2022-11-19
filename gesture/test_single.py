# import libs, torch first if run on macOS
import torch
import mediapipe as mp
import numpy as np
import cv2

import time

from lstm_model import SequenceClassificationPred
from data import HandTrackingModule as htm
NUM_MAX_HANDS = 1
USE_SELFLIB = True
# init mp
if not USE_SELFLIB:
    mp_hands = mp.solutions.hands
    mp_hands_handle = mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=NUM_MAX_HANDS,
        model_complexity=1,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    )
    mp_draw = mp.solutions.drawing_utils
else:
    detector = htm.handDetector(maxHands=NUM_MAX_HANDS, detectionCon = 0.5, trackCon = 0.5)
    mp_hands = detector.mpHands
    mp_hands_handle = detector.hands
    mp_draw = detector.mpDraw

# load model
# MODEL_PATH = './model/less_0123_relu.pt'
# model = StaticClassificationPred(MODEL_PATH, num_classes=4)
MODEL_PATH = './model/ipn_model_new_73.pt'
GESTURE_NAME = './data/IPN_Hand/id2gesture_new.csv'
model = SequenceClassificationPred(MODEL_PATH, gesture_name_map=GESTURE_NAME)

def main():
    
    # init cap
    cap = cv2.VideoCapture(0)
    cap_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    cap_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    pTime = 0
    mode = 0
    while True:
        success, raw_img = cap.read()
        if not success:
            # TODO cap exception handle
            pass
        
        # mode logic
        ret = cv2.waitKey(1) & 0xFF
        # ascii
        if ret == ord('n') and mode == 0:
            mode = 1
        elif ret == ord('n') and mode == 1:
            mode = 2
        if ret == 27: #esc
            break

        img = cv2.cvtColor(raw_img, cv2.COLOR_BGR2RGB)
        # raw_img, cv2 use
        # img, mediapipe use
        if mode == 1 or mode == 2:
            if not USE_SELFLIB:
                # set flag to improve performance
                img.flags.writeable = False
                raw_results = mp_hands_handle.process(img)
                img.flags.writeable = True
            else:
                detector.findHands(raw_img, False)
                raw_results = detector.results
            if raw_results.multi_hand_landmarks:
                results = {"detect": 0}
                for hand_world_landmarks, handedness in zip(raw_results.multi_hand_world_landmarks,
                                                      raw_results.multi_handedness):
                    idx = results["detect"]
                    results[idx] = hand_world_landmarks
                    results["detect"] += 1
                
                assert results["detect"] == 1
                # drawing utils use only hand_landmarks, not hand_world_handmarks
                mp_draw.draw_landmarks(raw_img, raw_results.multi_hand_landmarks[0], mp_hands.HAND_CONNECTIONS)
                # label_index = model.pred(results[0])
                # if label_index is not None:
                    # print(label_index)
                    # cv2.putText(raw_img, f"label_index:{label_index}", (15, 50),
                            # fontFace=cv2.FONT_HERSHEY_PLAIN,
                            # fontScale=2,
                            # color=(255, 0, 255),
                            # thickness=2)
                if mode == 1:
                    model.send(results[0], detector.fingersStraight(), detector.fingersUp())
                else:
                    gesture_name, frames = model.send(results[0], detector.fingersStraight(), detector.fingersUp(),True)
                    print(f"{frames} frames are predicted as {gesture_name}")
                    mode = 0


        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(raw_img, f'fps:{int(fps)}', [15, 25],
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)
        cv2.imshow("Image", raw_img)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()