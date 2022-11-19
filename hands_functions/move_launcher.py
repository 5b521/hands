import autopy
from utils.key_controller import KeyController

def page_move_for_gesture(str):
    if str == 'Throw up':
        autopy.key.tap(autopy.key.Code.PAGE_UP) 
    elif str == 'Throw down':
        autopy.key.tap(autopy.key.Code.PAGE_DOWN) 
    elif str == 'Throw left':
        autopy.key.tap(autopy.key.Code.RIGHT_ARROW) 
    elif str == 'Throw right':
        autopy.key.tap(autopy.key.Code.LEFT_ARROW) 
    # print(str)

def zoom_out_in(str):
    kc = KeyController()
    if str == 'Zoom in':
        kc.key_click(['ctrl', '+'])
    elif str == "Zoom out":
        kc.key_click(['ctrl', '-'])

def open_twice(str):
    kc = KeyController()
    kc.key_click(['ctrl', 'w'])