from handTracking import handTrack
from hands_functions import AiVirtualMouse as mouse
from hands_functions import handsMove
from hands_functions import volumeControl
from hands_functions import page
from hands_functions import game_control_car
from hands_functions import launcher
from hands_functions import move_launcher


def register_map(cap, detector):
    wCam = int(cap.get(3))
    hCam = int(cap.get(4))

    return {
        'mouse': mouse.Mouse(detector, wCam, hCam),
        # 'palm': handsMove.HandsMove(detector, page.page_move, lambda img: detector.fingersStraight()[1] == 1, True),
        'volume': volumeControl.systemVolumeControler(detector),
        'car': game_control_car.car_controller(detector),
        'QQ': launcher.exe_file_launcher(detector, r'D:\tencent\Bin\QQScLauncher.exe'),
        'key': launcher.key_launcher(detector, ['ctrl', 'w']),
        'three': launcher.webbrowser_launcher(detector, r'https://www.bilibili.com/v/tech/'),
        'Throw up':move_launcher.page_move_for_gesture,
        'Throw down':move_launcher.page_move_for_gesture,
        'Throw right':move_launcher.page_move_for_gesture,
        'Throw left':move_launcher.page_move_for_gesture,
        'Zoom in': move_launcher.zoom_out_in,
        'Zoom out': move_launcher.zoom_out_in,
        'Open twice':move_launcher.open_twice,
        'two':launcher.webbrowser_launcher(detector, r'https://cn.bing.com/'),
        # 'web': {
        #     # 'mouse': mouse.Mouse(detector, wCam, hCam),
        #     'Throw up':move_launcher.page_move_for_gesture,
        #     'Throw down':move_launcher.page_move_for_gesture,
        #     'Throw right':move_launcher.page_move_for_gesture,
        #     'Throw left':move_launcher.page_move_for_gesture,
        #     'Zoom in': move_launcher.zoom_out_in,
        #     'Zoom out': move_launcher.zoom_out_in,
        #     'mouse': launcher.webbrowser_launcher(detector, r'https://cn.bing.com/'),
        #     'exit': 'key',
        # },
    }


if __name__ == '__main__':
    handTrack(register_map, 'office')
