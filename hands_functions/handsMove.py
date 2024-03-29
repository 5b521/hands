import time
import cv2


class HandsMove:

    def __init__(self, detector, onEnd=None, isLockFunc=None, usingOldLockFunc=False):
        '''
        当手势识别结束时, 触发 onEnd 函数, 并传入一个 HandsMove 对象,
        
        你可以通过 HandsMove 对象的 result 属性获取识别结果,
        还有 useful 属性, 用于判断识别结果是否有用, "水平波动" 等结果被认为是没有用的.

        例如回调函数可以写为:

        def onEnd(handsMove):
            if handsMove.useful:
                print(handsMove.result)
        
        你还可以使用 HandsMove 对象的 track 属性获取手势的轨迹等.

        还可以输入一个自定义的 isLockFunc 函数
        '''

        # 回调函数
        self.end_fun = onEnd
        self.isLockFunc = isLockFunc
        self.usingOldLockFunc = usingOldLockFunc
        self.result = None
        self.useful = False

        # 时间间隔, 单位变化或坐标变化阈值
        self.delayTime = 0.1
        self.unitChange = 30
        self.distFromOrigin = 0.3
        self.posChange = 0.1
        self.blockWidth = 0.3

        # 原点, 超过一秒钟固定在同一个地方就作为新原点, 以及单位长度
        self.standardUnit = 10
        self.originPos = [200, 200]

        # 上一秒钟的坐标与单位长度
        self.lastTime = 0
        self.lastUnit = 100
        self.lastPos = [0, 0]

        # 记录的轨迹
        self.track = []

        # 手势识别
        self.pTime = 0
        self.cTime = 0
        self.cap = cv2.VideoCapture(0)
        self.detector = detector

        # 是否仍然继续识别
        self.lock = False

    def onStart(self, img):
        self.lock = True
        self.img = img
        lmList = self.detector.findPosition(img)  # 获取得到坐标点的列表
        self.standardUnit = self.detector.getStandardUnit(self.img)  # 获取标准单位
        self.originPos = [lmList[0][1], lmList[0][2]]  # 获取原点坐标
        self.lastUnit = self.standardUnit
        self.lastPos = self.originPos

    def end(self, result, useful=True):
        self.track.clear()
        self.result = result
        self.useful = useful
        if self.lock and callable(self.end_fun):
            self.end_fun(self)
        self.lock = False

    def onEnd(self):
        '''
        当原点发生变化时, 触发的函数, 进行一系列处理
        '''
        if len(self.track) == 0 or len(self.track) == 1:
            return self.end('原地不动', False)
        # z 轴变化较小
        if max(tr[3] for tr in self.track) - min(tr[3] for tr in self.track) < 2:
            # 垂直方向变化较小
            if all(abs(tr[1] - self.track[0][1]) < 3 for tr in self.track):
                # 单调递减或单调递增
                if all(self.track[i][2] <= self.track[i + 1][2] + 1 for i in range(len(self.track) - 1)) \
                        or all(self.track[i][2] >= self.track[i + 1][2] - 1 for i in range(len(self.track) - 1)):
                    # 超过一定的长度
                    if abs(self.track[-1][2] - self.track[0][2]) >= 2:
                        if self.track[-1][2] > self.track[0][2]:
                            return self.end('垂直向下')
                        else:
                            return self.end('垂直向上')
                # 不单调递减或单调递增, 则为波动
                else:
                    return self.end('垂直波动', False)
            # 水平方向变化较小
            elif all(abs(tr[2] - self.track[0][2]) < 2 for tr in self.track):
                if all(self.track[i][1] <= self.track[i + 1][1] + 1 for i in range(len(self.track) - 1)) \
                        or all(self.track[i][1] >= self.track[i + 1][1] - 1 for i in range(len(self.track) - 1)):
                    if abs(self.track[-1][1] - self.track[0][1]) >= 2:
                        if self.track[-1][1] > self.track[0][1]:
                            return self.end('水平向左')
                        else:
                            return self.end('水平向右')
                else:
                    return self.end('水平波动', False)
            # 倾斜(左/右)(上/下)
            else:
                if (all(self.track[i][1] <= self.track[i + 1][1] for i in range(len(self.track) - 1)) \
                        or all(self.track[i][1] >= self.track[i + 1][1] for i in range(len(self.track) - 1))) \
                    or (all(self.track[i][2] <= self.track[i + 1][2] for i in range(len(self.track) - 1)) \
                        or all(self.track[i][2] >= self.track[i + 1][2] for i in range(len(self.track) - 1))):
                    if abs(self.track[-1][1] - self.track[0][1]) >= 3 and abs(self.track[-1][2] - self.track[0][2]) >= 3:
                        if self.track[-1][2] > self.track[0][2]:
                            if self.track[-1][1] > self.track[0][1]:
                                return self.end('倾斜左下')
                            else:
                                return self.end('倾斜右下')
                        else:
                            if self.track[-1][1] > self.track[0][1]:
                                return self.end('倾斜左上')
                            else:
                                return self.end('倾斜右上')
        else:
            def getZStr():
                return '出拳' if self.track[-1][3] > self.track[0][3] else '收拳'
            if abs(self.track[-1][1] - self.track[0][1]) >= 3:
                return self.end('水平' + getZStr())
            elif abs(self.track[-1][2] - self.track[0][2]) >= 3:
                return self.end('垂直' + getZStr())
            else:
                return self.end(getZStr())
        return self.end('未识别到手势', False)

    def onLock(self, img):
        self.img = img
        return self.lock

    def onRun(self):

        self.cTime = time.time()

        h, w, c = self.img.shape

        lmList = self.detector.findPosition(self.img)  # 获取得到坐标点的列表
        self.unit = self.detector.getStandardUnit(self.img)  # 获取标准单位
        # if len(lmList) != 0:
        #     print(lmList[4])

        # 根据原点和单位绘制网格图
        cv2.line(self.img, (max(0, int(self.originPos[0] - self.standardUnit)), self.originPos[1]), (min(
            w, int(self.originPos[0] + self.standardUnit)), self.originPos[1]), (255, 0, 255), 2)
        cv2.line(self.img, (self.originPos[0], max(0, int(self.originPos[1] - self.standardUnit))),
                 (self.originPos[0], min(h, int(self.originPos[1] + self.standardUnit))), (255, 0, 255), 2)

        if lmList:
            # 手腕坐标
            wristPos = lmList[0]

            # 超过一秒
            if self.cTime - self.lastTime > self.delayTime:
                # print(track)
                # 单位发生较大变化, 更新单位长度
                if abs(self.unit - self.standardUnit) > self.unitChange:
                    self.standardUnit = self.lastUnit
                if self.isLockFunc:
                    if self.isLockFunc(self.img) == False:
                        self.onEnd()
                if not self.isLockFunc or self.usingOldLockFunc:
                    # 坐标相对原点发生变化, 但相对上一秒坐标没有发生较大变化, 则更新坐标, 表明结束
                    if (abs(wristPos[1] - self.originPos[0]) / self.unit > self.distFromOrigin or abs(wristPos[2] - self.originPos[1]) / self.unit > self.distFromOrigin) \
                            and abs(wristPos[1] - self.lastPos[0]) / self.unit < self.posChange and abs(wristPos[2] - self.lastPos[1]) / self.unit < self.posChange:
                        self.onEnd()
                        self.originPos = self.lastPos
                # 更新上一秒的信息
                self.lastTime = self.cTime
                self.lastUnit = self.unit
                self.lastPos = [wristPos[1], wristPos[2]]

            # 获取当前网格块和深度
            blockPos = [int((wristPos[1] - self.originPos[0]) / self.standardUnit / self.blockWidth),
                        int((wristPos[2] - self.originPos[1]) /
                            self.standardUnit / self.blockWidth),
                        int(self.standardUnit / self.unitChange)]

            if not self.track or self.track[-1][1] != blockPos[0] or self.track[-1][2] != blockPos[1] or self.track[-1][3] != blockPos[2]:
                self.track.append(
                    [self.cTime, blockPos[0], blockPos[1], blockPos[2]])

        return self.img

        