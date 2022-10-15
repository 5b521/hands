import keyboard as key
import json
import os
import time
import numpy as np
import autopy
import cv2
import sys
sys.path.append("..")
import HandTrackingModule as htm

absolutepath = os.path.abspath(__file__)
file_dir = os.path.dirname(absolutepath)

Path = os.path.join(file_dir, 'hand_features.json')
gestures = []
if os.path.exists(Path):
    with open(Path, encoding='utf-8', mode='r') as f:
        try:
            gestures = json.loads(f.read())
        except:
            pass
gesture_map = {}
for gesture in gestures:
    gesture_map[gesture['tag']] = gesture

def features_get(detector: htm, hand_num=0):

    FStraight = detector.fingersStraight(hand_num)
    FUp = detector.fingersUp(hand_num)
    FClose = detector.close_together(hand_num)
    TClose = detector.thumb_close(hand_num)
    FDirection = detector.direction(
        detector.results.multi_handedness[hand_num].classification[0].label)

    return {"FStraight": FStraight, "FUp": FUp, "FClose": FClose, "TClose": TClose, "FDirection": FDirection}


############################################################################################################
# 供参考 gesture 结构
############################################################################################################
# {
#   "Left": {
#     "FStraight": [1, 1, 0, 0, 0], # 1代表手指直立，0代表手指弯曲
#     "FUp": [0, 1, 0, 0, 0], # 1代表手指偏，0代表手指偏下
#     "FClose": [0, 0, 0, 0], # 1代表两指靠近（并拢），0代表两指分开
#     "TClose": [0, 0, 0, 0], # 1代表拇指靠近某个手指（指尖）
#     "FDirection": [
#       [2.90554640814662, -10.294727422297, -2.5022588670253754], # vector, landmark 0 to 5
#       [-2.2675693966448307, -6.620354764163494, -6.000513210892677] # vector, landmark 0 to 7
#     ]
#   },
#   "tag": "mouse"
# }
############################################################################################################


def features_record(tag):
    pTime = 0
    cTime = 0
    cap = cv2.VideoCapture(0)
    detector = htm.handDetector(maxHands=2)

    count = 0

    record_features = {}

    while True:
        success, img = cap.read()
        img = detector.findHands(img)        # 检测手势并画上骨架信息

        land_mark_List = detector.findPosition(img)  # 获取得到坐标点的列表

        if len(land_mark_List) != 0 and key.is_pressed(' '):
            count += 1

            for i in range(0, len(detector.results.multi_hand_landmarks)):

                curr_features = features_get(detector, i)
                left_right = detector.results.multi_handedness[i].classification[0].label

                if record_features.get(left_right):
                    record_features[left_right]['FStraight'] = curr_features['FStraight']
                    record_features[left_right]['FUp'] = curr_features['FUp']
                    record_features[left_right]['FClose'] = curr_features['FClose']
                    record_features[left_right]['TClose'] = curr_features['TClose']
                    if not detector.direction_same(curr_features['FDirection'], record_features[left_right]['FDirection'], 2):
                        record_features[left_right]['FDirection'] = curr_features['FDirection']
                else:
                    record_features[detector.results.multi_handedness[i]
                                    .classification[0].label] = curr_features

            cv2.putText(img, 'good Q,continue E', (10, 70),
                        cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
            cv2.imshow('Image', img)
            cv2.waitKey(1)

            while not key.is_pressed('e') and not key.is_pressed('q'):
                continue
            if key.is_pressed('q'):
                record_features['tag'] = tag
                gesture_map[tag] = record_features
                json_str = json.dumps(list(gesture_map.values()), indent=4, ensure_ascii=False)

                with open(Path, "w") as f:
                    f.write(json_str)
                    f.write('\n')
                    print("success")
                return record_features

        # 终端输出手势信息
        # if len(land_mark_List) != 0:
        #     curr_features = features_get(detector, 0)
        #     print(curr_features)

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, 'fps:' + str(int(fps)), (10, 70),
                    cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
        cv2.imshow('Image', img)
        cv2.waitKey(1)


if __name__ == "__main__":
    
    # features_record('mouse')  # 鼠标
    # features_record('palm')  # 巴掌
    # features_record('volume')  # 音量
    # features_record('car') #体感游戏
    features_record('QQ') #打开QQ
