
import HandTrackingModule
import cv2
import autopy
import numpy as np
import time
import os
import json
import keyboard as key
import sys
sys.path.append('..')

absolutepath = os.path.abspath(__file__)
file_dir = os.path.dirname(absolutepath)

Path = os.path.join(file_dir, 'hand_features.json')
# a = {'b':'c' , 'k':'p'}
# b = {'b':'c' , 'k':'p'}

# json_str = json.dumps(a)
# json_str2 = json.dumps(b)

# with open(Path,"w") as f:
#     f.write(json_str)
#     f.write('\n')
#     f.write(json_str2)
#     print("success")

# dict = {}

# with open(Path,encoding= 'utf-8',mode='r') as f:
#     for pinyin_str in f.readlines():
#         dict = json.loads(pinyin_str)

# print(dict)


print(sys.path)
