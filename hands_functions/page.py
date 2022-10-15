import autopy


def page_move(res):
    if res.result == '垂直向上':
        autopy.key.tap(autopy.key.Code.PAGE_UP) 
    elif res.result == '垂直向下':
        autopy.key.tap(autopy.key.Code.PAGE_DOWN) 
    elif res.result == '水平向右':
        autopy.key.tap(autopy.key.Code.RIGHT_ARROW) 
    elif res.result == '水平向左':
        autopy.key.tap(autopy.key.Code.LEFT_ARROW) 
    print(res.result)