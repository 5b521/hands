import time
import numpy as np
import autopy
import HandTrackingModule as htm
import cv2
from this import d
import sys
sys.path.append("..")


# 时间间隔, 单位变化或坐标变化阈值
delayTime = 0.1
unitChange = 30
distFromOrigin = 0.3
posChange = 0.1
blockWidth = 0.3

# 原点, 超过一秒钟固定在同一个地方就作为新原点, 以及单位长度
standardUnit = 10
originPos = [200, 200]

# 上一秒钟的坐标与单位长度
lastTime = 0
lastUnit = 100
lastPos = [0, 0]

# 记录的轨迹
track = []
count = 0


def handleUnitChange():
    '''
    当单位长度发生变化时, 触发的函数, 进行一系列处理
    '''
    # print('unit change')
    pass


def handleOriginChange():
    '''
    当原点发生变化时, 触发的函数, 进行一系列处理
    '''
    global track, count
    if len(track) == 0 or len(track) == 1:
        track.clear()
        return
    count += 1
    print(f'{count}: ', end='')
    if max(tr[3] for tr in track) - min(tr[3] for tr in track) < 2:
        if all(tr[1] == track[0][1] for tr in track):
            if all(track[i][2] < track[i + 1][2] for i in range(len(track) - 1)) \
                    or all(track[i][2] > track[i + 1][2] for i in range(len(track) - 1)):
                if abs(track[-1][2] - track[0][2]) >= 2:
                    if track[-1][2] > track[0][2]:
                        print('垂直向下')
                    else:
                        print('垂直向上')
            else:
                print('垂直波动')
        elif all(tr[2] == track[0][2] for tr in track):
            if all(track[i][1] < track[i + 1][1] for i in range(len(track) - 1)) \
                    or all(track[i][1] > track[i + 1][1] for i in range(len(track) - 1)):
                if abs(track[-1][1] - track[0][1]) >= 2:
                    if track[-1][1] > track[0][1]:
                        print('水平向左')
                    else:
                        print('水平向右')
            else:
                print('水平波动')
    else:
        def getZStr():
            return '出拳' if track[-1][3] > track[0][3] else '收拳'
        if abs(track[-1][1] - track[0][1]) >= 3:
            print('水平' + getZStr())
        elif abs(track[-1][2] - track[0][2]) >= 3:
            print('垂直' + getZStr())
        else:
            print(getZStr())
    track.clear()


##############################
pTime = 0
cTime = 0
cap = cv2.VideoCapture(0)
detector = htm.handDetector()
while True:
    success, img = cap.read()
    img = detector.findHands(img)        # 检测手势并画上骨架信息
    h, w, c = img.shape

    lmList = detector.findPosition(img)  # 获取得到坐标点的列表
    unit = detector.getStandardUnit(img)  # 获取标准单位
    # if len(lmList) != 0:
    #     print(lmList[4])

    ########################################

    # 根据原点和单位绘制网格图
    cv2.line(img, (max(0, int(originPos[0] - standardUnit)), originPos[1]), (min(
        w, int(originPos[0] + standardUnit)), originPos[1]), (255, 0, 255), 2)
    cv2.line(img, (originPos[0], max(0, int(originPos[1] - standardUnit))),
             (originPos[0], min(h, int(originPos[1] + standardUnit))), (255, 0, 255), 2)

    if lmList:
        # 手腕坐标
        wristPos = lmList[0]

        # 超过一秒
        if cTime - lastTime > delayTime:
            # print(track)
            # 单位发生较大变化, 更新单位长度
            if abs(unit - standardUnit) > unitChange:
                handleUnitChange()
                standardUnit = lastUnit
            # 坐标相对原点发生变化, 但相对上一秒坐标没有发生较大变化, 则更新坐标
            if (abs(wristPos[1] - originPos[0]) / unit > distFromOrigin or abs(wristPos[2] - originPos[1]) / unit > distFromOrigin) \
                    and abs(wristPos[1] - lastPos[0]) / unit < posChange and abs(wristPos[2] - lastPos[1]) / unit < posChange:
                handleOriginChange()
                originPos = lastPos
            # 更新上一秒的信息
            lastTime = cTime
            lastUnit = unit
            lastPos = [wristPos[1], wristPos[2]]

        # 获取当前网格块和深度
        blockPos = [int((wristPos[1] - originPos[0]) / standardUnit / blockWidth),
                    int((wristPos[2] - originPos[1]) /
                        standardUnit / blockWidth),
                    int(standardUnit / unitChange)]

        if not track or track[-1][1] != blockPos[0] or track[-1][2] != blockPos[1] or track[-1][3] != blockPos[2]:
            track.append([cTime, blockPos[0], blockPos[1], blockPos[2]])

    ########################################

    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    cv2.putText(img, 'fps:' + str(int(fps)), (10, 70),
                cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)
    cv2.imshow('Image', img)
    cv2.waitKey(1)
