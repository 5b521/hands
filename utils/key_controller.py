import ctypes

SendInput = ctypes.windll.user32.SendInput

PUL = ctypes.POINTER(ctypes.c_ulong)

# DirectInput Key Code Table
keycode_map = {
    'esc': 0x01,
    'space': 0x39,
    'enter': 0x1C,
    'tab': 0x0F,
    'backspace': 0x0E,
    'ctrl': 0x1D,
    'shift': 0x2A,
    'alt': 0x38,
    'capslock': 0x3A,
    'capital': 0x3A,
    'cap': 0x3A,
    'pageup': 0xc9,
    'pagedown': 0xd1,
    'left': 0xcb,
    'up': 0xc8,
    'right': 0xcd,
    'down': 0xd0,
    'insert': 0xd2,
    'delete': 0xd3,
    'home': 0xc7,
    'end': 0xcf,
    'numlock': 0x45,
    'scrolllock': 0x46,
    'printscreen': 0xb7,
    'pause': 0xc5,

    '0': 0x0B,
    '1': 0x02,
    '2': 0x03,
    '3': 0x04,
    '4': 0x05,
    '5': 0x06,
    '6': 0x07,
    '7': 0x08,
    '8': 0x09,
    '9': 0x0A,
    '0': 0x0B,
    'a': 0x1E,
    'b': 0x30,
    'c': 0x2E,
    'd': 0x20,
    'e': 0x12,
    'f': 0x21,
    'g': 0x22,
    'h': 0x23,
    'i': 0x17,
    'j': 0x24,
    'k': 0x25,
    'l': 0x26,
    'm': 0x32,
    'n': 0x31,
    'o': 0x18,
    'p': 0x19,
    'q': 0x10,
    'r': 0x13,
    's': 0x1F,
    't': 0x14,
    'u': 0x16,
    'v': 0x2F,
    'w': 0x11,
    'x': 0x2D,
    'y': 0x15,
    'z': 0x2C,
    'A': 0x1E,
    'B': 0x30,
    'C': 0x2E,
    'D': 0x20,
    'E': 0x12,
    'F': 0x21,
    'G': 0x22,
    'H': 0x23,
    'I': 0x17,
    'J': 0x24,
    'K': 0x25,
    'L': 0x26,
    'M': 0x32,
    'N': 0x31,
    'O': 0x18,
    'P': 0x19,
    'Q': 0x10,
    'R': 0x13,
    'S': 0x1F,
    'T': 0x14,
    'U': 0x16,
    'V': 0x2F,
    'W': 0x11,
    'X': 0x2D,
    'Y': 0x15,
    'Z': 0x2C,
    'f1': 0x3B,
    'f2': 0x3C,
    'f3': 0x3D,
    'f4': 0x3E,
    'f5': 0x3F,
    'f6': 0x40,
    'f7': 0x41,
    'f8': 0x42,
    'f9': 0x43,
    'f10': 0x44,
    'f11': 0x57,
    'f12': 0x58,
}

# C struct redefinitions 

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

class KeyController:

    # init
    def __init__(self) -> None:
        self.conflicting_keys_map = {}
        self.pressed_keys = set()

    # conflicting_keys
    def register_conflicting_keys(self, name, conflicting_keys):
        '''
        注册冲突按键
        例如可以使用 register_conflicting_keys('left_right', ['a', 'd']) 注册左右冲突按键
        '''
        assert name != 'all'
        assert isinstance(conflicting_keys, list) and len(conflicting_keys) > 0
        self.conflicting_keys_map[name] = {
                'keys': conflicting_keys,
                'last_pressed_key': None
            }

    def unregister_conflicting_keys(self, name='all'):
        '''
        注销冲突按键
        例如可以使用 unregister_conflicting_keys('left_right') 注销左右冲突按键
        留空或者 name = 'all' 会注销所有冲突按键
        '''
        if name == 'all':
            self.conflicting_keys_map = {}
        else:
            self.conflicting_keys_map.pop(name)

    def get_conflicting_keys(self, name='all'):
        '''
        获取冲突按键
        例如可以使用 get_conflicting_keys('left_right') 获取左右冲突按键
        留空或者 name = 'all' 会获取所有冲突按键
        '''
        if name == 'all':
            return self.conflicting_keys_map
        else:
            return self.conflicting_keys_map[name]

    def get_last_pressed_key(self, name):
        '''
        获取最后按下的按键
        例如可以使用 get_last_pressed_key('left_right') 获取左右冲突按键的最后按下的按键
        '''
        return self.conflicting_keys_map[name]['last_pressed_key']

    def release_conflicting_keys(self, name):
        '''
        松开冲突按键里的所有按键
        '''
        pressed_keys = self.pressed_keys.copy()
        for key in self.conflicting_keys_map[name]['keys']:
            if key in pressed_keys:
                self.keyup(key)

    # Actuals Functions
    def keydown(self, key):
        '''
        按下按键
        '''
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        hexKeyCode = keycode_map[key]
        ii_.ki = KeyBdInput( 0, hexKeyCode, 0x0008, 0, ctypes.pointer(extra))
        x = Input( ctypes.c_ulong(1), ii_)
        SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
        # print(f'keydown({key})')
        # 应对冲突按键
        for name in self.conflicting_keys_map:
            if key in self.conflicting_keys_map[name]['keys']:
                self.release_conflicting_keys(name)
                self.conflicting_keys_map[name]['last_pressed_key'] = key
        # 记录按键
        self.pressed_keys.add(key)


    def keyup(self, key):
        '''
        放开按键
        '''
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        hexKeyCode = keycode_map[key]
        ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008 | 0x0002, 0, ctypes.pointer(extra))
        x = Input(ctypes.c_ulong(1), ii_)
        SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
        # print(f'keyup({key})')
        # 记录按键
        if key in self.pressed_keys:
            self.pressed_keys.remove(key)

    def is_keydown(self, key):
        '''
        判断按键是否按下
        '''
        return key in self.pressed_keys


    def key_click(self, key):
        '''
        单击按键
        '''
        self.keydown(key)
        self.keyup(key)

        
    