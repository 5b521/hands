import autopy

def page_move_for_gesture(str):
    if str == 'Throw up':
        autopy.key.tap(autopy.key.Code.PAGE_UP) 
    elif str == 'Throw down':
        autopy.key.tap(autopy.key.Code.PAGE_DOWN) 
    elif str == 'Throw right':
        autopy.key.tap(autopy.key.Code.RIGHT_ARROW) 
    elif str == 'Throw left':
        autopy.key.tap(autopy.key.Code.LEFT_ARROW) 
    print(str)