from utils import *
from game_environment import Env
from time import time
# about 0.25 seconds per screenshot
# 4 windows would mean an action per second which should be enough
if __name__ == "__main__":
    
    # env = Env()
    # env.use_ability()
    sec = time()
    WM = WindowManagement()
    WM.focus_window(0)
    WM.screenshot("img1")
    WM.defocus_window(0)
    

    WM.focus_window(1)
    WM.screenshot("img2")
    WM.defocus_window(1)


    WM.focus_window(0)
    WM.screenshot("img3")
    WM.defocus_window(0)
    

    WM.focus_window(1)
    WM.screenshot("img4")
    WM.defocus_window(1)




    sec2 = time()
    print(sec2 - sec)

    





