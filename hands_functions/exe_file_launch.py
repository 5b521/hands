import os
from features_record import hand_recognition
class run_exe_file():

    def __init__(self,path) :
        self.Executed = False
        self.path = path

    def lock_func(self,img):
        self.img = img
        
        
        if self.Executed == True:
            self.count = 0
            self.Executed = False
            return self.Executed
        return not self.Executed
    
    def Execute(self):
        # path =  repr(self.str)
        os.startfile(self.path)
        self.Executed = True
        return self.img
