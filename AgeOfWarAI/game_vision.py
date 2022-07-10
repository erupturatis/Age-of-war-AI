import numpy as np
import cv2

class GameVision(object):
    
    def __init__(self) -> None:
        pass
    
    def __call__(self, *args):
        dict = {
            # dict with different types of identifiers
            "battle_position":self.battle,
        }
        return dict[args[0]](args[1:])

    def battle(self, *args):
        img = cv2.imread('AgeOfWarAI/assets/game1.png') # here goes game input
        template = cv2.imread('AgeOfWarAI/assets/coin.png') # here goes standard coin identifier
        h, w, c = template.shape
        h_img, w_img, c_img = img.shape
        # image dimensions
        method = cv2.TM_SQDIFF_NORMED # best method so far

        img2 = img.copy()
        result = cv2.matchTemplate(img2, template, method)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        location = min_loc
        bottom_right = (location[0] + w, location[1] + h)   
        # location of best match
        if min_val > .01:
            # didn't found any coin
            return None
        else:
            # return at what % of the map the battle took place 1 meaning the enemy base
            # the script will take the position of multiple coins and get the left most position
            return bottom_right[0] / w_img


        # cv2.rectangle(img2, location, bottom_right, 255, 5)
        # cv2.imshow('Match', img2)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows())

    @staticmethod
    def test():
        pass

import pyautogui
import cv2
import numpy as np

class WindowManagement(object):

    def __init__(self) -> None:
        pass

    def initial_setup(self):
        a = pyautogui.getWindowsWithTitle("Adobe Flash Player 13")
        window = a[0]
        window.move(-window.left, -window.top)
        window.maximize()
        window.resize(-window.size[0]+1800,-window.size[1]+600)

    def screenshoot(self):
        im = pyautogui.screenshot(region=(0,45,1700,525))
        opencvImage = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)
        cv2.imshow("img", opencvImage)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

if __name__ == "__main__":
    obj = WindowManagement()
    obj.screenshoot()
