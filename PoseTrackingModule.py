import cv2
from keyboard import wait
import mediapipe as mp
import time
import autopy
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_pose = mp.solutions.pose


import ctypes

SendInput = ctypes.windll.user32.SendInput

# C struct redefinitions 
PUL = ctypes.POINTER(ctypes.c_ulong)
class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time",ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                 ("mi", MouseInput),
                 ("hi", HardwareInput)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]

# Actuals Functions

def PressKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput( 0, hexKeyCode, 0x0008, 0, ctypes.pointer(extra) )
    x = Input( ctypes.c_ulong(1), ii_ )
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

def ReleaseKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput( 0, hexKeyCode, 0x0008 | 0x0002, 0, ctypes.pointer(extra) )
    x = Input( ctypes.c_ulong(1), ii_ )
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


def handle_direction(lm):
    '''
    处理头部方向
    '''
    # print(f'lm[0](nose)={lm[0]}')
    # print(f'lm[2](left_eye)={lm[2]}')
    # print(f'lm[5](right_eye)={lm[5]}')
    # print(f'lm[7](left_ear)={lm[7]}')
    # print(f'lm[8](right_ear)={lm[8]}')
    # print(f'lm[9](mouse_left)={lm[9]}')
    # print(f'lm[10](mouse_right)={lm[10]}')

    # 耳朵之间的距离
    ear_distance = abs(lm[7].x - lm[8].x)
    # 眼嘴之间的距离
    me_distance = abs(lm[9].x - lm[10].x)
    # 上容错比例
    up_error_rate = 0.1
    # 下容错比例
    down_error_rate = 0.3
    # 左右容错比例
    lr_error_rate = 0.2
    if lm[0].y < (lm[2].y + me_distance * up_error_rate):
        print('Up')
        return 'Up'
    elif lm[0].y > (lm[7].y + me_distance * down_error_rate):
        print('Down')
        return 'Down'
    elif lm[0].x > (lm[7].x - ear_distance * lr_error_rate):
        # lm[0] x 轴方向大于 lm[7] x 轴方向，说明头部向左转
        print('Left')
        return 'Left'
    elif lm[0].x < (lm[8].x + ear_distance * lr_error_rate):
        # lm[0] x 轴方向小于 lm[8] x 轴方向，说明头部向右转
        print('Right')
        return 'Right'
    else:
        return 'Center'


# 是否初始化
is_init = True
# 最后的开始时间
last_begin_time = time.time()
# 最高的 y 与最低的 y
max_y = 0
min_y = 0
# 是否正在跑步
is_running = False
def handle_running_and_jump(lm):
    '''
    处理静止, 跑步与跳跃
    '''
    global is_init
    global last_begin_time
    global max_y
    global min_y
    global is_running
    # print(f'lm[0](nose)={lm[0]}')
    # print(f'lm[7](left_ear)={lm[7]}')
    # print(f'lm[8](right_ear)={lm[8]}')

    # 间隔时间
    interval_time = 0.15
    # 跑步阈值
    run_threshold = 0.05
    # 跳跃阈值
    jump_threshold = 0.7

    # 耳朵之间的距离
    ear_distance = abs(lm[7].x - lm[8].x)

    # 获取 y 值
    _y = (lm[11].y + lm[12].y) / 2

    # 初始化
    if is_init:
        is_init = False
        last_begin_time = time.time()
        max_y = _y
        min_y = _y

    # 在间隔时间内, 记录最高的 y 与最低的 y
    if time.time() - last_begin_time < interval_time:
        max_y = max(max_y, _y)
        min_y = min(min_y, _y)
    else:
        # 超过间隔时间, 重新初始化与进行判断
        is_init = True
        # 处理是否正在跑步
        if max_y - min_y > ear_distance * jump_threshold:
            # print('Jump')
            # press('space')
            if is_running:
                ReleaseKey(0x11)
                is_running = False
            # time.sleep(0.1)
            # press('space')
            PressKey(0x39)
            ReleaseKey(0x39)
            return 'Jump'
        elif max_y - min_y > ear_distance * run_threshold:
            # print('Run')
            # autopy.key.toggle('w', True, []) 
            if not is_running:
                PressKey(0x11)
                is_running = True
            return 'Run'
        else:
            # autopy.key.toggle('w', False, [])
            if is_running:
                ReleaseKey(0x11)
                is_running = False
            print('Stand')
            return 'Stand'


pTime = 0
# For webcam input:
cap = cv2.VideoCapture(0)
with mp_pose.Pose(
    model_complexity=1,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5) as pose:
  while cap.isOpened():
    success, image = cap.read()
    if not success:
      print("Ignoring empty camera frame.")
      # If loading a video, use 'break' instead of 'continue'.
      continue

    # To improve performance, optionally mark the image as not writeable to
    # pass by reference.
    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(image)

    if results.pose_landmarks:
        lm = results.pose_landmarks.landmark
        handle_direction(lm)
        handle_running_and_jump(lm)

    # Draw the pose annotation on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    mp_drawing.draw_landmarks(
        image,
        results.pose_landmarks,
        mp_pose.POSE_CONNECTIONS,
        landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())

    # Flip the image horizontally for a selfie-view display.
    image = cv2.flip(image, 1)
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(image, f'fps:{int(fps)}', [15, 25],
                cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 255), 2)
    cv2.imshow('MediaPipe Pose', image)
    if cv2.waitKey(5) & 0xFF == 27:
      break
cap.release()