import os
from features_record import hand_recognition
class run_exe_file():

    def __init__(self,path,detector) :
        self.Executed = False
        self.path = path
        self.detector = detector
        self.FUp = None

    def lock_func(self,img):
        self.img = img
        if not self.FUp:
            self.FUp = self.detector.FUp
        if self.FUp != self.detector.FUp:
            self.Executed = False
            return False
        else:
            return True
        
    
    def Execute(self):
        # path =  repr(self.str)
        if not self.Executed:
            print('execute')
            os.startfile(self.path)
            self.Executed = True
        return self.img

    def handleEnd(self):
        self.Executed = False
        
