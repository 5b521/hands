import cv2
import mediapipe as mp
import time
import math
import numpy as np
import keyboard as key
from features_record import hand_recognition as hr
# self.results.multi_hand_world_landmarks
# 以手的几何中心为原点建立三维坐标系

# self.results.multi_hand_landmarks
# x 和 y 值被规范到 [0.0, 1.0]，表示在img上的位置
# z 值以手腕为原点，表示深度，z 值越小离摄像头越近


class handDetector():
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
        self.tipIds = [4, 8, 12, 16, 20]
        self.FClose_set = hr.FClose_recogenize()


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

    def is_straight(self, dot1, dot2, dot3, dot4, boundary, hand_num=0):

        d1 = self.results.multi_hand_world_landmarks[hand_num].landmark[dot1]
        d2 = self.results.multi_hand_world_landmarks[hand_num].landmark[dot2]
        d3 = self.results.multi_hand_world_landmarks[hand_num].landmark[dot3]
        d4 = self.results.multi_hand_world_landmarks[hand_num].landmark[dot4]

        v1 = [d2.x - d1.x, d2.y - d1.y, d2.z-d1.z]
        v2 = [d4.x - d3.x, d4.y - d3.y, d4.z-d3.z]
        # cv2.line(img, (self.lmList[dot2][1], self.lmList[dot2][2]), (self.lmList[dot1][1], self.lmList[dot1][2]), (255, 0, 255), 3)
        # cv2.line(img, (self.lmList[dot3][1], self.lmList[dot3][2]), (self.lmList[dot4][1], self.lmList[dot4][2]), (255, 0, 255), 3)
        angle = math.degrees(math.acos((v1[0] * v2[0] + v1[1] * v2[1] + v1[2] * v2[2])/(
            ((v1[0]**2 + v1[1]**2 + v1[2]**2)**0.5)*((v2[0]**2 + v2[1]**2 + v2[2]**2)**0.5))))

        if boundary < angle <= 180:
            # if(dot2 == 20):
            # print(v1[2],v2[2])
            return True
        else:
            # print(angle,v1[2],v2[2])
            return False

    def fingersStraight(self, hand_num=0):

        FStraight = []

        # 大拇指
        if (self.is_straight(3, 4, 3, 2, 130, hand_num)):
            FStraight.append(1)
        else:
            FStraight.append(0)

        # 其余手指
        for i in range(8, 21, 4):
            if (self.is_straight(i-2, i, i-2, i-3, 120, hand_num)):
                FStraight.append(1)
            else:
                FStraight.append(0)

        return FStraight

    def dot_to_line(self,dot1,dot2,hand_num = 0):
        d1 = self.results.multi_hand_world_landmarks[hand_num].landmark[dot1]
        d2 = self.results.multi_hand_world_landmarks[hand_num].landmark[dot2]

        return [d2.x - d1.x, d2.y - d1.y, d2.z-d1.z]


    def fingersUp(self, hand_num=0):
        self.FUp = []
        # 大拇指

        v1 = np.array(self.dot_to_line(9,5,hand_num))
        v2 = np.array(self.dot_to_line(2,4,hand_num))

        v1 = v1 / np.linalg.norm(v1)

        if np.dot(v1,v2) > np.linalg.norm(v2)/4:
            self.FUp.append(1)
        else:
            self.FUp.append(0)

        # 其余手指
        if self.is_straight(5, 6, 5, 0, 130, hand_num):
            self.FUp.append(1)
        else:
            self.FUp.append(0)

        if self.is_straight(9, 10, 5, 0, 140, hand_num):
            self.FUp.append(1),
        else:
            self.FUp.append(0)

        if self.is_straight(13, 14, 17, 0, 130, hand_num):
            self.FUp.append(1),
        else:
            self.FUp.append(0)

        if self.is_straight(17, 18, 17, 0, 150, hand_num):
            self.FUp.append(1),
        else:
            self.FUp.append(0)
        # totalFingers = fingers.count(1)
        return self.FUp

                            
    def close_together(self, hand_num=0):

        # 只记录四个手指是否并拢的值，从大拇指与食指到  无名指与小拇指
        FClose = []
        
            
        self.fingersUp(hand_num)

        if self.findDistance(4, 5, hand_num) < self.FClose_set[0]   and ((not self.FUp[0]) & self.FUp[1]):
            FClose.append(1)
        else:
            FClose.append(0)

        if self.findDistance(8, 12, hand_num) < self.FClose_set[1] and (self.FUp[1] & self.FUp[2]):
            FClose.append(1)
        else:
            FClose.append(0)

        if self.findDistance(16, 12, hand_num) < self.FClose_set[2] and (self.FUp[2] & self.FUp[3]):
            FClose.append(1)
        else:
            FClose.append(0)

        if self.findDistance(15, 20, hand_num) < self.FClose_set[3] and (self.FUp[3] & self.FUp[4]):
            FClose.append(1)
        else:
            FClose.append(0)

        return FClose

    def direction(self, left_right):

        if self.results.multi_handedness[0].classification[0].label == left_right:

            d1 = self.results.multi_hand_world_landmarks[0].landmark[0]
            d2 = self.results.multi_hand_world_landmarks[0].landmark[5]
            d3 = self.results.multi_hand_world_landmarks[0].landmark[17]

            v1 = [(d2.x - d1.x)*100, (d2.y - d1.y)*100, (d2.z-d1.z)*100]
            v2 = [(d3.x - d1.x)*100, (d3.y - d1.y)*100, (d3.z-d1.z)*100]

            return v1, v2

        elif len(self.results.multi_handedness) == 2:

            d1 = self.results.multi_hand_world_landmarks[1].landmark[0]
            d2 = self.results.multi_hand_world_landmarks[1].landmark[5]
            d3 = self.results.multi_hand_world_landmarks[1].landmark[17]

            v1 = [(d2.x - d1.x)*100, (d2.y - d1.y)*100, (d2.z-d1.z)*100]
            v2 = [(d3.x - d1.x)*100, (d3.y - d1.y)*100, (d3.z-d1.z)*100]

            return v1, v2
            # x3 = (v1[1]*v2[2] - v2[1]*v1[2]) / (v2[1]*v1[0] - v1[1]*v2[0])
            # y3 = (v1[0]*v2[2] - v2[0]*v1[2]) / (v2[0]*v1[1] - v1[0]*v2[1])
        else:
            return [0, 0, 0], [0, 0, 0]

    def direction_same(self, v1, v2, st):

        vd1 = np.array(v1[0]) - np.array(v2[0])
        vd2 = np.array(v1[1]) - np.array(v2[1])

        difference = np.linalg.norm(vd1) + np.linalg.norm(vd2)

        if (difference < st):
            return True
        else:
            return False

    def thumb_close(self, hand_num=0):

        TClose = []
        if self.findDistance(4, 8, hand_num) < 2:
            TClose.append(1)
        else:
            TClose.append(0)

        if self.findDistance(4, 12, hand_num) < 2:
            TClose.append(1)
        else:
            TClose.append(0)

        if self.findDistance(4, 16, hand_num) < 2:
            TClose.append(1)
        else:
            TClose.append(0)

        if self.findDistance(4, 20, hand_num) < 2:
            TClose.append(1)
        else:
            TClose.append(0)

        return TClose

    def getStandardUnit(self, img):
        '''
        返回从节点 0 到节点 5 的屏幕距离, 可作为移动距离的标准单位
        未检测到手时返回 None
        '''
        if self.results.multi_hand_landmarks:
            h, w, c = img.shape
            lk = self.results.multi_hand_landmarks[0].landmark
            x0, y0, z0 = lk[0].x * w, lk[0].y * h, lk[0].z * w
            x5, y5, z5 = lk[5].x * w, lk[5].y * h, lk[5].z * w
            return ((x5 - x0) ** 2 + (y5 - y0) ** 2 + (z5 - z0) ** 2) ** 0.5

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
    
    def findEvelation(self, hand_str1, p1, hand_str2, p2, img=None, draw=False):
        '''
        计算两个 landmark 之间连线的仰角，返回角度值和仰角角心所在的手
        draw_func: 绘画函数
        '''

        if len(self.lmList) != 0:
            hand_num1 = self.hdDict[hand_str1]
            hand_num2 = self.hdDict[hand_str2]

            d1x, d1y = self.lmList[hand_num1*21 + p1][1:]
            d2x, d2y = self.lmList[hand_num2*21 + p2][1:]

            # if hand_num1 != hand_num2: # means detect 2 hands
            #     if d1y > d2y:
            #         lower_hand = self.hdDict[hand_num2]

            if draw:
                cv2.line(img, (d1x, d1y), (d2x, d2y), (0, 255, 255), 3)

            return math.degrees(math.atan2(d2y - d1y, d2x - d1x))
            return math.degrees(math.atan(abs(d2y - d1y) / abs(d2x - d1x))), lower_hand
        else:
            return 0, "None"

def main():
    pTime = 0
    cTime = 0
    cap = cv2.VideoCapture(0)
    # detector = handDetector()
    detector = handDetector(maxHands=2)
    while True:
        success, img = cap.read()
        img = detector.findHands(img)        # 检测手势并画上骨架信息

        lmList = detector.findPosition(img)  # 获取得到坐标点的列表


        if len(lmList) != 0:
        # Elevation test
            # if detector.hdDict["Detected"] == 2:
            #     print(detector.findEvelation('Left', 6, 'Right', 6, img, 
            #                         True))
            # print(detector.direction('Left'))
            # direction = [[5.375117808580399, -9.055236307904124, -1.5031843446195126], [-0.8503671735525131, -7.541118375957012, -4.165707714855671]]
            # if(detector.direction_same(direction,detector.direction('Left'),10)):
            #     print("good")
            # print(detector.results.multi_handedness[0].classification[0].label)
            # v1,v2 = detector.direction('Left')
            # print(v1,v2)
            # print(cx,cy,cz)
            if detector.FClose_set:
                FClose = detector.close_together()
                for i in range(0, 4):
                    if (FClose[i] == 1):
                        cv2.circle(
                            img, (lmList[(i+1)*4][1], lmList[(i+1)*4][2]), 15, (0, 0, 255), cv2.FILLED)
            # print(FClose[0])
            # FUp = detector.fingersUp()
            # FStraight = detector.fingersUp()
            # for i in range(0, 5):
            #     if (FStraight[i] == 1):
            #         cv2.circle(
            #             img, (lmList[(i+1)*4][1], lmList[(i+1)*4][2]), 15, (0, 0, 255), cv2.FILLED)
            # if(FStraight[0] == 1):
            
            #     print("good")
            # else:
            #     print("bad")
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, 'fps:' + str(int(fps)), (10, 70),
                    cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
        cv2.imshow('Image', img)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()
