import HandTrackingModule as htm
import numpy as np
import os
import json
import keyboard as key
from features_record import hand_features_record as fr

absolutepath = os.path.abspath(__file__)
file_dir = os.path.dirname(absolutepath)

Path = os.path.join(file_dir, 'hand_features.json')

f = open( Path,encoding= 'utf-8',mode='r')

gestures = []

with open(Path,encoding= 'utf-8',mode='r') as f:
    for pinyin_str in f.readlines():
        gestures.append(json.loads(pinyin_str))


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


def hand_recognition(detector):
    hands = {}
    for i in range(len(detector.results.multi_handedness)):
        hands[detector.results.multi_handedness[i].classification[0].label] = fr.features_get(detector,i)
    # print(hands[detector.results.multi_handedness[0].classification[0].label])
    if len(hands) == 1:
        for gesture in gestures:
            if len(gesture) == 2:
                right_left = list(hands.keys())[0]
                if gesture.get(right_left):
                    if hands[right_left]['FStraight'] == gesture[right_left]['FStraight']\
                        and hands[right_left]['FUp'] == gesture[right_left]['FUp']\
                        and hands[right_left]['FClose'] == gesture[right_left]['FClose']\
                        and hands[right_left]['TClose'] == gesture[right_left]['TClose']\
                        and detector.direction_same(gesture[right_left]["FDirection"],hands[right_left]["FDirection"],3):
                        return gesture['tag']
            else:
                if len(gesture) == 3:
                    right_left = list(hands.keys())[0]
                    if gesture.get(right_left):
                        if hands[right_left]['FStraight'] == gesture[right_left]['FStraight']\
                        and hands[right_left]['FUp'] == gesture[right_left]['FUp']\
                        and hands[right_left]['FClose'] == gesture[right_left]['FClose']\
                        and hands[right_left]['TClose'] == gesture[right_left]['TClose']\
                        and detector.direction_same(gesture[right_left]["FDirection"],hands[right_left]["FDirection"],3):
                        
                            right_left = list(hands.keys())[1]
                            if hands[right_left]['FStraight'] == gesture[right_left]['FStraight']\
                            and hands[right_left]['FUp'] == gesture[right_left]['FUp']\
                            and hands[right_left]['FClose'] == gesture[right_left]['FClose']\
                            and hands[right_left]['TClose'] == gesture[right_left]['TClose']\
                            and detector.direction_same(gesture[right_left]["FDirection"],hands[right_left]["FDirection"],3):
                                return gesture['tag']





    
    

    
    
    

    

