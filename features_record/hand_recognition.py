import HandTrackingModule as htm
import numpy as np
import os
import json
import keyboard as key
from features_record import hand_features_record as fr

absolutepath = os.path.abspath(__file__)
file_dir = os.path.dirname(absolutepath)

Path = os.path.join(file_dir, 'hand_features.json')

gestures = []

with open(Path, encoding='utf-8', mode='r') as f:
    gestures = json.loads(f.read())


# def gesture_same(hands,gestures):
#     if len(hands) == 1:
#         for gesture in gestures:
#             if len(gesture) == 2:
#                 right_left = list(hands.keys())[0]
#                 if gesture.get(right_left):
#                     hands[right_left]['FStraight'] = gesture[right_left]['FStraight']
#                     hands[right_left]['FUp'] = gesture[right_left]['FUp']
#                     hands[right_left]['FClose'] = gesture[right_left]['FClose']
#                     hands[right_left]['TClose'] = gesture[right_left]['TClose']

        # Left = hands.get('Left')
        # Right = hands.get('Right')
        # if Left :
        #     if Left['FStraight'] == gesture[]
        #  "FUp": [0, 1, 0, 0, 0], "FClose": [1, 0, 1, 1], "TClose": [0, 1, 1, 0]


############################################################################################################
# 供参考 gesture 结构
############################################################################################################
# {
#   "Left": {
#     "FStraight": [1, 1, 0, 0, 0],
#     "FUp": [0, 1, 0, 0, 0],
#     "FClose": [0, 0, 0, 0],
#     "TClose": [0, 0, 0, 0],
#     "FDirection": [
#       [2.90554640814662, -10.294727422297, -2.5022588670253754],
#       [-2.2675693966448307, -6.620354764163494, -6.000513210892677]
#     ]
#   },
#   "tag": "mouse"
# }
############################################################################################################
Path2 = os.path.join(file_dir, 'FingerClose_feature.json')

f = open(Path2, encoding='utf-8', mode='r')

FClose_feature = []

with open(Path2, encoding='utf-8', mode='r') as f:
    FClose_feature = json.loads(f.read())

def FClose_recogenize():

    return FClose_feature

def hand_recognition(detector, diff=10):
    hands = {}
    for i in range(len(detector.results.multi_handedness)):
        hands[detector.results.multi_handedness[i].classification[0].label] = fr.features_get(
            detector, i)
    # print(hands[detector.results.multi_handedness[0].classification[0].label])
    if len(hands) == 1:
        for gesture in gestures:
            if len(gesture) == 2:
                right_left = list(hands.keys())[0]
                if gesture.get(right_left):
                    if hands[right_left]['FStraight'] == gesture[right_left]['FStraight']\
                            and hands[right_left]['FUp'] == gesture[right_left]['FUp']\
                            and hands[right_left]['FClose'] == gesture[right_left]['FClose']\
                            and detector.direction_same(gesture[right_left]["FDirection"], hands[right_left]["FDirection"], diff):
                            # and hands[right_left]['TClose'] == gesture[right_left]['TClose']\
                        return gesture['tag']
                
    else:
        # 包含了 "Left", "Right" 和 "tag", 所以 len(gesture) == 3
        for gesture in gestures:
            if len(gesture) == 3:
                    right_left = list(hands.keys())[0]
                    if gesture.get(right_left):
                        if hands[right_left]['FStraight'] == gesture[right_left]['FStraight']\
                                and hands[right_left]['FUp'] == gesture[right_left]['FUp']\
                                and hands[right_left]['FClose'] == gesture[right_left]['FClose']\
                                and detector.direction_same(gesture[right_left]["FDirection"], hands[right_left]["FDirection"], diff):
                                # and hands[right_left]['TClose'] == gesture[right_left]['TClose']\

                            right_left = list(hands.keys())[1]
                            if hands[right_left]['FStraight'] == gesture[right_left]['FStraight']\
                                    and hands[right_left]['FUp'] == gesture[right_left]['FUp']\
                                    and hands[right_left]['FClose'] == gesture[right_left]['FClose']\
                                    and hands[right_left]['TClose'] == gesture[right_left]['TClose']\
                                    and detector.direction_same(gesture[right_left]["FDirection"], hands[right_left]["FDirection"], diff):
                                return gesture['tag']