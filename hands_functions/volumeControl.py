# create a new class
# provide lock_func and run_func
if __name__ == '__main__':
    import sys
    sys.path.append("..")
import HandTrackingModule as htm
from features_record import hand_recognition as hr
import platform
import time
import cv2
if platform.system() == 'Windows':
    from ctypes import cast, POINTER
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume, ISimpleAudioVolume

class volumeControler:
    if platform.system() == 'Windows':
        def __init__(self) -> None:
            self.devices = AudioUtilities.GetSpeakers()
            self.interface = self.devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self.volume = cast(self.interface, POINTER(IAudioEndpointVolume))
        
        def getCurrentVolume(self):
            return int(round(self.volume.GetMasterVolumeLevelScalar() * 100))
        
        def setVolume(self, scalarVolume):
            scalarVolume = int(scalarVolume)/100
            self.volume.SetMasterVolumeLevelScalar(scalarVolume, None)
    else:
        # virtual audio
        def __init__(self) -> None:
            self.virtual_volume = 0.5
        def getCurrentVolume(self):
            return self.virtual_volume*100
        def setVolume(self, scalarVolume):
            self.virtual_volume = int(scalarVolume)/100
            print("Set Volume to {}% virtually".format(int(scalarVolume)))

class fingerLengthMeter:
    '''
    计算两个指尖之间的距离
    gesture_tag: 绑定的手势
    ignore_flag: 跟踪手势中手指的距离变化时忽略某些 feature 的变化
    
    函数将按
    fingersStraight 5
    fingersUp 5
    close_together 4
    thumb_close 4
    的顺序构建 flag 用于比对手势, ignore_flag 中的为 1 的位可以让函数在比对时忽略特定 feature 的变化
    
    可以使用 fingerLengthMeter.flagGenerator([[0, 0, 0, 0, 0], ..., [0, 0, 0, 0]]) 来生成填入
    
    measure_lm: 跟踪的两个手指 landmark
    '''
    def __init__(self, detector: htm.handDetector, gesture_tag: str, ignore_flag: int, measure_lm: tuple):
        self.detector = detector
        
        # access loaded gestures
        self.handness = 'Left'
        for gesture in hr.gestures:
            if gesture['tag'] == gesture_tag:
                if gesture.get('Left'):
                    self.gesture = gesture['Left']
                else:
                    self.gesture = gesture['Right']
                    self.handness = 'Right'
        self.ignore_flag = ignore_flag
        self.filter_flag = (2**18-1) ^ ignore_flag
        self.measure_lm = measure_lm

    def is_control(self, img):
        self.img = img
        # hand_num decided after find hands
        # self.hand_num = self.detector.hdDict[self.handness][0]
        # TODO: fix bug caused by mediapipe
        self.hand_num = 0
        # detector won't auto calculate feature
        cur_flag = self.flagGenerator([
            self.detector.fingersStraight(self.hand_num),
            self.detector.fingersUp(self.hand_num),
            self.detector.close_together(self.hand_num),
            self.detector.thumb_close(self.hand_num)
        ])
        tar_flag = self.flagGenerator([
            self.gesture['FStraight'],
            self.gesture['FUp'],
            self.gesture['FClose'],
            self.gesture['TClose']
        ])
        return (cur_flag ^ tar_flag)&self.filter_flag == 0
    
    def run_control(self, draw=True):
        '''
        Please wrap this funciton since it returns additional value
        '''
        dist = self.detector.findDistance(self.measure_lm[0], self.measure_lm[1])
        if draw:
            d1x, d1y = self.detector.lmList[self.hand_num*21 + self.measure_lm[0]][1:]
            d2x, d2y = self.detector.lmList[self.hand_num*21 + self.measure_lm[1]][1:]
            cv2.line(self.img, (d1x, d1y), (d2x, d2y), (0, 255, 255), 3)
        return self.img, dist

    @staticmethod
    def flagGenerator(sources: list):
        '''
        sources: list of lists containing only 0 and 1
        '''
        flag = 0
        concat_list = []
        for l in sources:
            concat_list.extend(l)
        for i in range(len(concat_list)):
            flag += concat_list[i] * (2 ** i)
        return flag

class systemVolumeControler:
    min_ratio = 12.5
    def __init__(self, detector: htm.handDetector) -> None:
        self.meter = fingerLengthMeter(detector, "volume", 0x4060, (4, 8))
        self.timeRatio = [0, self.min_ratio]
        self.vlc = volumeControler()
        self.d = detector

    def is_volume_control(self, img):
        # frame binded
        self.result = self.meter.is_control(img)
        return self.result

    def run_volume_control(self):
        img, dist = self.meter.run_control(draw=self.result)
        # if dist > 1 and self.result:
        #     if self.timeRatio and time.time() - self.timeRatio[0] < 0.2:
        #             # update time
        #             self.timeRatio[0] = time.time()
        #             new_perc = self.timeRatio[1]*(int(dist)-1)
        #             if new_perc > 100:
        #                 new_perc = 100
        #                 self.timeRatio[1] = 100/(dist - 1)
        #             if abs(self.vlc.getCurrentVolume() - new_perc) >= 1:
        #                 self.vlc.setVolume(new_perc)
        #     else:
        #         new_ratio = self.vlc.getCurrentVolume()/(dist - 1)
        #         self.timeRatio = [time.time(), new_ratio if new_ratio >= self.min_ratio else self.timeRatio[1]]
        if dist > 1 and self.result:
            new_perc = self.timeRatio[1]*(int(dist)-1)
            new_perc += 4
            if new_perc > 100:
                new_perc = 100
                self.timeRatio[1] = 100/(dist - 1)
            if abs(self.vlc.getCurrentVolume() - new_perc) >= 1:
                self.vlc.setVolume(new_perc)
            new_ratio = self.vlc.getCurrentVolume()/(dist - 1)
            self.timeRatio = [time.time(), new_ratio if new_ratio >= self.min_ratio else self.timeRatio[1]]
        return img

if __name__ == "__main__":
    import cv2
    import time
    from features_record import hand_features_record as hfr
    pTime = 0
    cap = cv2.VideoCapture(0)  # 若使用笔记本自带摄像头则编号为0  若使用外接摄像头 则更改为1或其他编号
    detector = htm.handDetector(maxHands=1)
    volume_control = systemVolumeControler(detector)
    while True:
        _, img = cap.read()
        img = detector.findHands(img)
        lmList = detector.findPosition(img, draw=False)
        if len(lmList) != 0:
            if volume_control.is_volume_control(img):
                img = volume_control.run_volume_control()

        # 终端输出手势信息
        # if len(lmList) != 0:
        #     curr_features = hfr.features_get(detector, 0)
        #     print(curr_features)
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, f'fps:{int(fps)}', [15, 25],
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)
        cv2.imshow("Image", img)
        cv2.waitKey(1)
