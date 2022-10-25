from handTracking import handTrack
from hands_functions import AiVirtualMouse as mouse
from hands_functions import handsMove
from hands_functions import volumeControl
from hands_functions import page
from hands_functions import game_control_car
from hands_functions import launcher


def register_map(cap, detector):
    wCam = int(cap.get(3))
    hCam = int(cap.get(4))

    return {
        'mouse': mouse.Mouse(detector, wCam, hCam),
        'palm': handsMove.HandsMove(detector, page.page_move, lambda img: detector.fingersStraight()[1] == 1, True),
        'volume': volumeControl.systemVolumeControler(detector),
        'car': game_control_car.car_controller(detector),
        'QQ': launcher.exe_file_launcher(detector, r'D:\tencent\Bin\QQScLauncher.exe'),
        'key': launcher.key_launcher(detector, ['ctrl', 'w']),
        'web': {
            'mouse': launcher.webbrowser_launcher(detector, r'https://cn.bing.com/'),
            'two': launcher.webbrowser_launcher(detector, r'https://www.bilibili.com/'),
            'exit': 'key',
        },
    }


if __name__ == '__main__':
    handTrack(register_map, 'game')
