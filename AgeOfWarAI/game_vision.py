import numpy as np
import cv2
import pyautogui
from pytesseract import pytesseract
from pytesseract import Output

class GameVision(object):

    env = None
    screenshoot = None

    def __init__(self) -> None:
        pass
    
    def __call__(self, *args):
        dict = {
            # dict with different types of identifiers
            "battle_position":self.battle,
        }
        return dict[args[0]](args[1:])

    def battle(self, *args):
        # game input
        img = self.screenshoot 
        # standard coin identifier
        template = cv2.imread('AgeOfWarAI/assets/coin.png')
        h, w, c = template.shape
        h_img, w_img, c_img = img.shape
        # image dimensions
        method = cv2.TM_SQDIFF_NORMED # best method so far

        result = cv2.matchTemplate(img, template, method)
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

    def scan_money(self):
        pass

    def scan_xp(self):
        pass
    
    def scan_enemy_health(self):
        pass

    def scan_enemy_age(self):
        pass

    def scan_enemy_troops(self):

        def first_age():
            #gets clubman and slingers together
            img = cv2.imread('AgeOfWarAI/assets/game1.png')
            template = cv2.imread('AgeOfWarAI/assets/enemy/clubman6.png')
            threshhold = 0.65

            method = cv2.TM_CCOEFF_NORMED # best method so far
            result = cv2.matchTemplate(img, template, method)

            locations = np.where(result >= threshhold)
            locations = list(zip(*locations[::-1]))

            if locations:
                template_w = template.shape[1]
                template_h = template.shape[0]
                line_color = (0, 255, 0)
                # clustering the clone values into 1
                new_locations = list()
                locations.sort()
                for i in range(len(locations)-1):
                    if abs(locations[i][0] - locations[i+1][0]) < 10 or not(locations[i][1]>500 and locations[i][1]<530) or locations[i][0] < 600 or locations[i][0] > 1550:
                        continue
                    else:
                        new_locations.append(locations[i])
                    
                print(len(new_locations))
                print(len(locations))
                for loc in new_locations:
                    print(loc)
                    top_left = loc
                    bottom_right = (top_left[0] + template_w, top_left[1] + template_h)

                    cv2.rectangle(img, top_left, bottom_right, line_color)
                
                cv2.imshow('Matches', img)
                cv2.waitKey()
        

    def scan_player_heath(self):
        img = self.screenshoot
        print(img)


class WindowManagement(object):

    def __init__(self) -> None:
        pass

    def initial_setup(self):
        a = pyautogui.getWindowsWithTitle("Adobe Flash Player 13")
        window = a[0]
        window.move(-window.left, -window.top)
        window.maximize()
        window.resize(-window.size[0]+1800,-window.size[1]+600)

    def visualize_image(img):
        cv2.imshow("img", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def screenshot(self):
        im = pyautogui.screenshot(region=(0,45,1700,525))
        opencvImage = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)
        return opencvImage
        


if __name__ == "__main__":
    img = cv2.imread("AgeOfWarAI/assets/game2.png")
    pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
    image_data = pytesseract.image_to_data(img, output_type=Output.DICT)
    print(image_data)

