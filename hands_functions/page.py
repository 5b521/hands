import autopy


def page_move(res):
    if res.result == '垂直向上':
        autopy.key.toggle(autopy.key.Code.PAGE_UP, True, []) 
        autopy.key.toggle(autopy.key.Code.PAGE_UP, False, [])
    elif res.result == '垂直向下':
        autopy.key.toggle(autopy.key.Code.PAGE_DOWN, True, []) 
        autopy.key.toggle(autopy.key.Code.PAGE_DOWN, False, [])
    elif res.result == '水平向右':
        autopy.key.toggle(autopy.key.Code.RIGHT_ARROW, True, []) 
        autopy.key.toggle(autopy.key.Code.RIGHT_ARROW, False, [])
    elif res.result == '水平向左':
        autopy.key.toggle(autopy.key.Code.LEFT_ARROW, True, []) 
        autopy.key.toggle(autopy.key.Code.LEFT_ARROW, False, [])
    print(res.result)