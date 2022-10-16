import keyboard as key
import json
import os
import time
import cv2
import sys
import mediapipe as mp

absolutepath = os.path.abspath(__file__)
file_dir = os.path.dirname(absolutepath)

Path = os.path.join(file_dir, 'FingerClose_feature.json')

class FClose_record():
    def __init__(self, mode=False, maxHands=1, model_complexity=1, detectionCon=0.8, trackCon=0.8):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon
        self.model_complexity = model_complexity
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            self.mode, self.maxHands, self.model_complexity, self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        # build hands dict, an example
        # {
        #     "Detected": 2,
        #     "Left": [0,],
        #     "Right": [1,],
        #     0: "Left",
        #     1: "Right"
        # }
        self.hdDict = {"Detected": 0}
        len_hands = 0
        if self.results.multi_hand_landmarks:
            len_hands = len(self.results.multi_hand_landmarks)
        if len_hands:
            for i in range(0,len_hands):
                # hands to id, 1-multi
                left_right = self.results.multi_handedness[i].classification[0].label
                
                self.hdDict[left_right] = i
                # id to hands, 1-1
                self.hdDict[i] = left_right
                self.hdDict["Detected"] += 1
        if len_hands == 2 and self.hdDict[0] == self.hdDict[1]:
            self.hdDict["Detected"] = 1
        # draw hand connections
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(
                        img, handLms, self.mpHands.HAND_CONNECTIONS)
        return img

    def findPosition(self, img, draw=True):
        self.lmList = []
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                for id, lm in enumerate(handLms.landmark):
                    h, w, c = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    # print(id, cx, cy)
                    self.lmList.append([id, cx, cy])
                    if draw:
                        cv2.circle(img, (cx, cy), 12,
                                   (255, 0, 255), cv2.FILLED)
        return self.lmList



    def FClose_rescord(self):
        FClose_set = []
        FClose_set.append(self.findDistance(4, 5, 0)+0.5)
        FClose_set.append(self.findDistance(8, 12, 0)+0.5)
        FClose_set.append(self.findDistance(12, 16, 0)+0.5)
        FClose_set.append(self.findDistance(15, 20, 0)+1)
        
        return FClose_set
        # json_str = json.dumps(self.FClose_set, indent=4, ensure_ascii=False)
        # absolutepath = os.path.abspath(__file__)
        # file_dir = os.path.dirname(absolutepath)

        # Path = os.path.join(file_dir, 'FClose_record.json')
        # with open(Path, "w") as f:
        #     f.write(json_str)
        #     f.write('\n')
        #     print("success")
                            

    def findDistance(self, p1, p2, hand_num=0, draw=True, r=15, t=3):
        d1 = self.results.multi_hand_world_landmarks[hand_num].landmark[p1]
        d2 = self.results.multi_hand_world_landmarks[hand_num].landmark[p2]

        cx, cy, cz = (d1.x + d2.x) / 2, (d1.y + d2.y) / 2, (d1.z + d2.z) / 2

        # if draw:
        #     cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), t)
        #     cv2.circle(img, (x1, y1), r, (255, 0, 255), cv2.FILLED)
        #     cv2.circle(img, (x2, y2), r, (255, 0, 255), cv2.FILLED)
        #     cv2.circle(img, (cx, cy), r, (0, 0, 255), cv2.FILLED)

        length = ((d2.x - d1.x)**2 + (d2.y - d1.y)
                  ** 2 + ((d2.z - d1.z)/5)**2)**0.5

        return length*100



def features_record(tag):
    pTime = 0
    cTime = 0
    cap = cv2.VideoCapture(0)
    detector = FClose_record()

    count = 0


    while True:
        success, img = cap.read()
        img = detector.findHands(img)        # 检测手势并画上骨架信息

        land_mark_List = detector.findPosition(img)  # 获取得到坐标点的列表

        if len(land_mark_List) != 0 and key.is_pressed(' '):
            count += 1

            FClose_set = detector.FClose_rescord()
             
            cv2.putText(img, 'good Q,continue E', (10, 70),
                        cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
            cv2.imshow('Image', img)
            cv2.waitKey(1)

            while not key.is_pressed('e') and not key.is_pressed('q'):
                continue
            if key.is_pressed('q'):
                
                
                json_str = json.dumps(FClose_set, indent=4, ensure_ascii=False)

                with open(Path, "w") as f:
                    f.write(json_str)
                    f.write('\n')
                    print("success")
                return FClose_set

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
    # features_record('car')  # 体感游戏
    # features_record('QQ')  # 打开QQ
    features_record('web')  # 打开网页
