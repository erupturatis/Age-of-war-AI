import numpy as np
import cv2
import pyautogui
from PIL import Image, ImageOps, ImageFilter
from pytesseract import pytesseract
from pytesseract import Output
from utils import *
import warnings
from game_environment import Env
import time

class GameVision(object):

    env = None
    screenshot = None
    player_health_position = None
    enemy_health_position = None
    maximum = 0
    width = 0

    def __init__(self) -> None:
        pass
    
    def __call__(self, *args):
        dict = {
            # dict with different types of identifiers
            "battle_position":self.battle,
        }
        return dict[args[0]](args[1:])

    def scan_coins(self, *args):
        # game input
        img = cv2.imread('AgeOfWarAI/assets/environment/test4.png') # change
        img = img[600:-100,875:-250]
        # standard coin identifier
        template1 = cv2.imread('AgeOfWarAI/assets/misc/coin1.png')
        template2 = cv2.imread('AgeOfWarAI/assets/misc/coin2.png')

        h, w, c = template1.shape
        h_img, w_img, c_img = img.shape
        # image dimensions
        method = cv2.TM_SQDIFF_NORMED # best method so far

        treshold = .04

        result = cv2.matchTemplate(img, template1, method)
        locations1 = np.where(result <= treshold)
        locations1 = list(zip(*locations1[::-1]))

        result = cv2.matchTemplate(img, template2, method)
        locations2 = np.where(result <= treshold)
        locations2 = list(zip(*locations2[::-1]))

        locations1 = self.clustering_values(locations1)
        locations2 = self.clustering_values(locations2)

        locations = None

        if len(locations1) == 0:
            locations = locations2
        elif len(locations2) == 0:
            locations = locations1
        else:
            locations = np.concatenate((locations1,locations2))

        # for loc in locations:
        #     print(loc)
        #     cv2.rectangle(img, (loc[0],loc[1]),(loc[0] + w, loc[1] + h), (0,255,0),5)

        # cv2.imshow('Match', img)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        if len(locations) == 0:
            return None
        else:
            locations = sorted(locations, key = lambda x : x[0])
            locations = np.array(locations)
            return locations[0][0]/w_img
     

    def analyzie_image(self, img):
        #img = cv2.imread("AgeOfWarAI/assets/game2.png")
        pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
        image_data = pytesseract.image_to_string(img, output_type=Output.DICT)
        return image_data


    def get_position(self, img, template, treshold, method = cv2.TM_CCOEFF_NORMED):

        result = cv2.matchTemplate(img, template, method)

        if method == cv2.TM_SQDIFF_NORMED:
            locations = np.where(result <= treshold)
            locations = list(zip(*locations[::-1]))
        else:
            locations = np.where(result >= treshold)
            locations = list(zip(*locations[::-1]))

        return locations


    def check_if_ended(self):
        img = self.screenshot
        template = cv2.imread(f'AgeOfWarAI/assets/misc/defeat.png')
        result = self.get_position(img=img, template=template, treshold=0.9)

        if len(result) > 0:
            return True
        return False


    def scan_money_and_xp(self, env = None):
        if env == None:
            class Dummy(object):
                money = 175
                xp = 0
            env = Dummy()

        self.env = env
        template = cv2.imread(f'AgeOfWarAI/assets/misc/coin_and_exp.png')
        
        img = self.screenshot
        img = img[:-700,600:-1400]

        # img = cv2.imread('0.png') # change

        #cv2.imwrite("game0",img)

        result = self.get_position(img=img, template=template, treshold=0.95)
   
        if len(result) == 0:
            raise("Game Paused")    
                
            
        result = result[0]
        
      

        top_left = result
        bottom_right = (result[0] + 150, result[1] + 75)

        img_money = img[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]]
        img_money_gray = cv2.cvtColor(img_money, cv2.COLOR_BGR2GRAY)
        img_money_gray = cv2.resize(img_money_gray, (img_money_gray.shape[1]*3,img_money_gray.shape[0]*2) )
       

        
        result1 = self.analyzie_image(img_money_gray) # 0.25sec
        
        indices_aux = np.where((img_money_gray<70))
        img_money_gray[indices_aux] = 182

        indices_first = np.where(img_money_gray>200)
        indices_second = np.where((img_money_gray>75)&(img_money_gray<120) )
       
        #time1 = time.time()
        img_money_gray[:,:] = 255
        
        img_money_gray[indices_first] = 0
        img_money_gray[indices_second] = 0

        #time2 = time.time()
        

        result2 = self.analyzie_image(img_money_gray) # 0.25sec
  
        result1 = result1['text']
        result2 = result2['text']

        money_1 = self.env.money
        money_2 = self.env.money

        xp_1 = self.env.xp
        xp_2 = self.env.xp
        # print("results1")
        # print(result1)
        # print("results2")
        # print(result2)
        

        result1 = result1.replace("@","0")
        result1 = result1.replace("©","0")

        result2 = result2.replace("@","0")
        result2 = result2.replace("©","0")


        try:
            money_1,xp_1 = result1.split()[1],result1.split()[3]
        except:
            money_1 = self.env.money
            xp_1 = self.env.xp
        
        try:
            money_2,xp_2 = result2.split()[1],result2.split()[3]
        except:
            money_2 = self.env.money
            xp_2 = self.env.xp

        money_finale = self.env.money
        xp_finale = self.env.xp

        try:
            money_1 = int(money_1)
        except:
            money_1 = -9999

        try:
            money_2 = int(money_2)
        except:
            money_2 = -9999

        
        try:
            xp_1 = int(xp_1)
        except:
            xp_1 = -9999

        try:
            xp_2 = int(xp_2)
        except:
            xp_2 = -9999

        # print(f"money {money_1}  {money_2}")
        # print(f"xp {xp_1}  {xp_2} \n")
        
        if money_2 < money_1:
            money_2 = money_1 # you never get values bigger than the actual value

        money_finale = money_2
        # money1 is consistently more accurate
        if xp_1 > xp_finale:
            xp_finale = xp_1

        if money_finale == -9999: money_finale = self.env.money
        if xp_finale == -9999: xp_finale = self.env.xp
        
        
        return money_finale, xp_finale
        
        #since the scan is not perfect we match the results


        
        # color_coverted = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2RGB)
        # cv2.imshow("OpenCV Image", opencv_image)

        # pil_image = Image.fromarray(color_coverted)
        # pil_image.show()
    

    def initial_scan_health(self):
        self.player_health_position = (700, 279)
        self.enemy_health_position = (2530, 279)
        return
        template = cv2.imread(f'AgeOfWarAI/assets/misc/hpbar.png')
        img = self.screenshot # change
        #img = cv2.imread(f'AgeOfWarAI/assets/tests/test1.png')

        positions = self.get_position(img, template, 0.01, cv2.TM_SQDIFF_NORMED)
        positions.sort()
        #self.visualize_locations(img, positions)
        #print(len(positions))

        new_positions = list()
        positions.append((9999,9999))
        new_positions.sort()
        for i in range(len(positions)-1):
            if abs(positions[i][0] - positions[i+1][0]) < 10:
                continue
            else:
                new_positions.append(positions[i])
        if len(new_positions) >= 2:
            self.player_health_position = new_positions[0]
            self.enemy_health_position = new_positions[1]
        else:
            pass
        # print(new_positions[0])
        # print(new_positions[1])
        # print("new")


    def scan_health(self):
        template = cv2.imread(f'AgeOfWarAI/assets/misc/hpbar.png')
        # img = cv2.imread('AgeOfWarAI/assets/game6.png') # change
        img = self.screenshot

        # I am adding an offset to eliminate some potentially hazardous values

        top_left = (5 + self.player_health_position[0],self.player_health_position[1])
        bottom_right = (-5 + self.player_health_position[0] + template.shape[1],self.player_health_position[1]+ template.shape[0])
        
        player_health_bar = img[top_left[1]:bottom_right[1],top_left[0]:bottom_right[0]]

        player_health_bar = cv2.cvtColor(player_health_bar, cv2.COLOR_BGR2GRAY)
        (unique, counts) = np.unique(player_health_bar, return_counts=True)
        # getting the most common pixel values by sorting
        counts = np.stack((counts,unique), axis=-1)
        counts = sorted(counts, key = lambda x : x[0])
        counts = np.array(counts)
        
        player_counts = counts[::-1]


        top_left = (5 + self.enemy_health_position[0],self.enemy_health_position[1])
        bottom_right = (-5 + self.enemy_health_position[0] + template.shape[1],self.enemy_health_position[1]+ template.shape[0])
        #same for the enemy
        enemy_health_bar = img[top_left[1]:bottom_right[1],top_left[0]:bottom_right[0]]
      
        enemy_health_bar  = cv2.cvtColor(enemy_health_bar , cv2.COLOR_BGR2GRAY)
        (unique, counts) = np.unique(enemy_health_bar , return_counts=True)

        counts = np.stack((counts,unique), axis=-1)
        counts = sorted(counts, key = lambda x : x[0])
        counts = np.array(counts)

        enemy_counts = counts[::-1]

        player_hp = None
        enemy_hp = None
        # calculating hp, checking if the values closer to black (the missing hp)
        # are appearing more than the others
        if player_counts[0][1] < player_counts[1][1]:
            player_hp = player_counts[1][0]/(player_counts[0][0]+player_counts[1][0])
        else:
            player_hp = player_counts[0][0]/(player_counts[0][0]+player_counts[1][0])

        if enemy_counts[0][1] < enemy_counts[1][1]:
            enemy_hp = enemy_counts[1][0]/(enemy_counts[0][0]+enemy_counts[1][0])
        else:
            enemy_hp = enemy_counts[0][0]/(enemy_counts[0][0]+enemy_counts[1][0])


        return player_hp, enemy_hp

    def clustering_values(self, locations, treshold = 10, dimension = 0):
        new_locations = list()
     
        locations.append((9999,9999))
        locations = sorted(locations, key = lambda x : x[0])
        locations = np.array(locations)
        appended = False

        for i in range(len(locations)-1):
            if abs(locations[i][dimension] - locations[i+1][dimension]) < treshold:
                continue
            else:
                new_locations.append(locations[i])
                appended = True
        
        return new_locations

    def filter_height(self, locations, floor):
        new_locations = list()

        for i in range(len(locations)):
          
            if locations[i][1] > floor:
                new_locations.append(locations[i])

        return new_locations


    def visualize_locations(self, img, locations):
        for loc in locations:
            top_left = loc
            bottom_right = (top_left[0] + 20, top_left[1] + 20)

            cv2.rectangle(img, top_left, bottom_right,(0,255,0),2)
            
        cv2.imshow('Matches', img)
        cv2.waitKey()
    
    def maximum_width(self, array):
        mx = 0
        for i in array:
            mx = max(mx,i[0])
        return mx


    def scan_troops(self, flip = False, age = 1, aged_recently = False):
        img = self.screenshot
        # img = cv2.imread('game0.png') # change
        img = img[600:-90,850:-200]
        if flip:
            img = cv2.flip(img, 1)

        # cv2.imshow("",img)
        # cv2.waitKey()
        
  

        def first_age():
            #gets clubman and slinger together
            #img = cv2.imread('AgeOfWarAI/assets/environment/age1troops.png') # change
            #img = img[400:-50,800:-150]


            template_tier_1 = cv2.imread('AgeOfWarAI/assets/player/age1tier1.png')
            template_tier_2 = cv2.imread('AgeOfWarAI/assets/player/age1tier2.png')
            template_tier_3 = cv2.imread('AgeOfWarAI/assets/player/age1tier3.png')

            threshold = 0.9

            locations_tier_1 = self.get_position(img, template_tier_1, threshold -.02 )
            locations_tier_1 = self.clustering_values(locations_tier_1)

            locations_tier_2 = self.get_position(img, template_tier_2, threshold -.1)
            locations_tier_2 = self.clustering_values(locations_tier_2)
       

            locations_tier_3 = self.get_position(img, template_tier_3, threshold -.15 )
            locations_tier_3 = self.clustering_values(locations_tier_3)
            
            self.maximum = max(self.maximum,self.maximum_width(locations_tier_1),self.maximum_width(locations_tier_2),self.maximum_width(locations_tier_3))
            # self.visualize_locations(img, locations_tier_3)

            return [len(locations_tier_1), len(locations_tier_2), len(locations_tier_3)]
        
        def second_age():
            #img = cv2.imread('AgeOfWarAI/assets/environment/age2troops.png') # change
            #img = img[400:-50,800:-150]

            template_tier_1 = cv2.imread('AgeOfWarAI/assets/player/age2tier1.png')
            template_tier_2 = cv2.imread('AgeOfWarAI/assets/player/age2tier2.png')
            template_tier_3 = cv2.imread('AgeOfWarAI/assets/player/age2tier3.png')

            threshold = 0.9

            locations_tier_1 = self.get_position(img, template_tier_1, threshold - .1)
            locations_tier_1 = self.clustering_values(locations_tier_1)
            locations_tier_1 = self.filter_height(locations_tier_1, floor=120)

            locations_tier_2 = self.get_position(img, template_tier_2, threshold - .2)
            locations_tier_2 = self.clustering_values(locations_tier_2)

            locations_tier_3 = self.get_position(img, template_tier_3, threshold -.15)
            locations_tier_3 = self.clustering_values(locations_tier_3)
            #self.visualize_locations(img, locations_tier_1)
            self.maximum = max(self.maximum,self.maximum_width(locations_tier_1),self.maximum_width(locations_tier_2),self.maximum_width(locations_tier_3))
            
            return [len(locations_tier_1), len(locations_tier_2), len(locations_tier_3)]

        def third_age():
            #img = cv2.imread('AgeOfWarAI/assets/environment/age3troops.png') # change
            #img = img[400:-50,800:-150]
            
            template_tier_1 = cv2.imread('AgeOfWarAI/assets/player/age3tier1.png')
            template_tier_2 = cv2.imread('AgeOfWarAI/assets/player/age3tier2.png')
            template_tier_3 = cv2.imread('AgeOfWarAI/assets/player/age3tier3.png')

            threshold = 0.9

            locations_tier_1 = self.get_position(img, template_tier_1, threshold + .05)
            locations_tier_1 = self.clustering_values(locations_tier_1)

            locations_tier_2 = self.get_position(img, template_tier_2, threshold - .08)
            locations_tier_2 = self.clustering_values(locations_tier_2)
            
            locations_tier_3 = self.get_position(img, template_tier_3, threshold - .05)
            locations_tier_3 = self.clustering_values(locations_tier_3)

            self.maximum = max(self.maximum,self.maximum_width(locations_tier_1),self.maximum_width(locations_tier_2),self.maximum_width(locations_tier_3))
            #self.visualize_locations(img, locations_tier_3)

            return [len(locations_tier_1), len(locations_tier_2), len(locations_tier_3)]

        def fourth_age():
            #img = cv2.imread('AgeOfWarAI/assets/environment/age4troops.png') # change
            #img = img[400:-50,800:-150]

            template_tier_1 = cv2.imread('AgeOfWarAI/assets/player/age4tier12.png')
            template_tier_2 = cv2.imread('AgeOfWarAI/assets/player/age4tier2.png')
            template_tier_3 = cv2.imread('AgeOfWarAI/assets/player/age4tier3.png')

            threshold = 0.9

            locations_tier_1 = self.get_position(img, template_tier_1, threshold -.25)
            locations_tier_1 = self.clustering_values(locations_tier_1)

            locations_tier_2 = self.get_position(img, template_tier_2, threshold - .2)
            locations_tier_2 = self.clustering_values(locations_tier_2)

            locations_tier_3 = self.get_position(img, template_tier_3, threshold)
            locations_tier_3 = self.clustering_values(locations_tier_3)

            self.maximum = max(self.maximum,self.maximum_width(locations_tier_1),self.maximum_width(locations_tier_2),self.maximum_width(locations_tier_3))#self.visualize_locations(img, locations_tier_2)
            first_tier = max(0,len(locations_tier_1) - len(locations_tier_2))
            return [first_tier, len(locations_tier_2), len(locations_tier_3)]

        def fifth_age():
            #img = cv2.imread('AgeOfWarAI/assets/environment/age5troops.png') # change
            #img = img[400:-50,800:-150]

            template_tier_1 = cv2.imread('AgeOfWarAI/assets/player/age5tier1.png')
            template_tier_2 = cv2.imread('AgeOfWarAI/assets/player/age5tier2.png')
            template_tier_3 = cv2.imread('AgeOfWarAI/assets/player/age5tier3.png')
            template_tier_4 = cv2.imread('AgeOfWarAI/assets/player/age5tier4.png')

            threshold = 0.9

            locations_tier_1 = self.get_position(img, template_tier_1, threshold -.2)
            locations_tier_1 = self.clustering_values(locations_tier_1)

            locations_tier_2 = self.get_position(img, template_tier_2, threshold -.2)
            locations_tier_2 = self.clustering_values(locations_tier_2)

            locations_tier_3 = self.get_position(img, template_tier_3, threshold -.05)
            locations_tier_3 = self.clustering_values(locations_tier_3)

            locations_tier_4 = self.get_position(img, template_tier_4, threshold -.15)
            locations_tier_4 = self.clustering_values(locations_tier_4)
           
            self.maximum = max(self.maximum,self.maximum_width(locations_tier_1),self.maximum_width(locations_tier_2),self.maximum_width(locations_tier_3))         #self.visualize_locations(img, locations_tier_2)

            return [len(locations_tier_1), len(locations_tier_2), len(locations_tier_3), len(locations_tier_4)]
       
        res = None
        if aged_recently:
            if age == 1:
                res = [0,0,0], first_age()
            elif age == 2:
                res = first_age(), second_age()
            elif age == 3:
                res = second_age(), third_age()
            elif age == 4:
                res = third_age(), fourth_age()
            elif age == 5:
                res = fourth_age(), fifth_age()
        else:
            if age == 1:
                res = first_age()
            elif age == 2:
                res = second_age()
            elif age == 3:
                res =  third_age()
            elif age == 4:
                res =  fourth_age()
            elif age == 5:
                res =  fifth_age()

        self.width = img.shape[1]
        #print(res)
        return res
        


    def scan_training(self):
        img = self.screenshot # change
        #img = cv2.imread('AgeOfWarAI/assets/tests/test1.png')
        template = cv2.imread('AgeOfWarAI/assets/misc/training.png')

        img = img[:-800,800:-800]



        result = cv2.matchTemplate(img, template, cv2.TM_SQDIFF_NORMED)
        locations = np.where(result <= .001)
        locations = list(zip(*locations[::-1]))
        locations = self.clustering_values(locations, 3, 1)
        locations = self.clustering_values(locations, 3, 0)
        # print(locations)
        # for loc in locations:
        #     cv2.rectangle(img, loc, (loc[0]+10,loc[1]+10),(0,255,0),3)
    
        # cv2.imshow("img",img)
        # cv2.waitKey()
        return len(locations)
    
    def scan_age(self, flip = False):
        img = self.screenshot
        #img = cv2.imread('AgeOfWarAI/assets/tests/test00.png')
        template1 = cv2.imread('AgeOfWarAI/assets/misc/age1base.png')
        template2 = cv2.imread('AgeOfWarAI/assets/misc/age2base.png')
        template3 = cv2.imread('AgeOfWarAI/assets/misc/age3base.png')
        template4 = cv2.imread('AgeOfWarAI/assets/misc/age4base.png')
        template5 = cv2.imread('AgeOfWarAI/assets/misc/age5base.png')

        img = img[700:,600:]
        if flip:
            img = cv2.flip(img,1)
        
        img = img[:,:-1600]
        result = self.get_position(img, template1, 0.8)
        #self.visualize_locations(img , result)
        if len(result)>=1:
            return 1
        result = self.get_position(img, template2, 0.8)
        if len(result)>=1:
            return 2
        result = self.get_position(img, template3, 0.8)
        if len(result)>=1:
            return 3
        result = self.get_position(img, template4, 0.8)
        if len(result)>=1:
            return 4
        result = self.get_position(img, template5, 0.8)
        if len(result)>=1:
            return 5



if __name__ == "__main__":

    #obj1.screenshot()

    obj = GameVision()
    print(obj.scan_age(True))

    pass

