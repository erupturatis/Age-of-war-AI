import numpy as np
import cv2
import pyautogui
from utils import *


class GameVision(object):

    ocr = None
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
        result = self.get_position(img=img, template=template, treshold=0.85)

        if len(result) > 0:
            return True
        return False
    
    def check_victory(self):
        img = self.screenshot
        template = cv2.imread(f'AgeOfWarAI/assets/misc/victory.png')
        result = self.get_position(img=img, template=template, treshold=0.7)

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
        # img3 = img[100:-700,680:-1680]
        img2 = img[70:-490,650:-800]
        img = img[:-450,500:-1150]
        
        result = self.get_position(img=img, template=template, treshold=0.95)
        if len(result) == 0:
            raise("Game Paused") 
            
        img = cv2.resize(img, (img.shape[0]*2, img.shape[1]*2))
        ocr = self.ocr

        result = ocr.ocr(img, cls=True)
        txts = [line[1][0] for line in result]

        result2 = ocr.ocr(img2, cls=True)
        txts2 = [line[1][0] for line in result2]

        try:
            money_1 = txts[0]
            cnt = 0
            print(txts)
            for i,c in enumerate(txts[1]):
                if c<='9' and c >='0':
                    cnt = i
                    break
            xp_1 = txts[1][cnt:]
            money_finale = self.env.money
            xp_finale = self.env.xp
            money_1 = int(money_1)
            xp_1 = int(xp_1)

            print(self.env.enemy_age)
                
            money_finale = money_1
            xp_finale = xp_1
        except:
            money_finale = self.env.money
            xp_finale = self.env.xp


        troop_player = [0,0,0,0]
        troop_enemy = [0,0,0,0]
        battle_place = 1
        print(txts2)
        try:
            troops = txts2[0].split('-')
       
            troop_player = (int(troops[0]),int(troops[1]),int(troops[2]),int(troops[3]))
            troop_enemy = (int(troops[4]),int(troops[5]),int(troops[6]),0)
            self.prev = troop_player
            
            battle_place = float(troops[7])
            self.prb = battle_place
        except:
            battle_place = 1
            troop_player = [0,0,0,0]


        print(money_finale)


        return money_finale, xp_finale, troop_player, troop_enemy, battle_place

    
    def click_game(self):
        pyautogui.click(700,300)

    def initial_scan_health(self):
        self.player_health_position = (515, 194)
        self.enemy_health_position = (1692, 194)

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
        try:
            if player_counts[0][1] < player_counts[1][1]:
                player_hp = player_counts[1][0]/(player_counts[0][0]+player_counts[1][0])
            else:
                player_hp = player_counts[0][0]/(player_counts[0][0]+player_counts[1][0])

            if enemy_counts[0][1] < enemy_counts[1][1]:
                enemy_hp = enemy_counts[1][0]/(enemy_counts[0][0]+enemy_counts[1][0])
            else:
                enemy_hp = enemy_counts[0][0]/(enemy_counts[0][0]+enemy_counts[1][0])
        except:
            player_hp = None
            enemy_hp = None

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

        img = img[:-500,750:-600]
        result = cv2.matchTemplate(img, template, cv2.TM_SQDIFF_NORMED)
        locations = np.where(result <= .001)
        locations = list(zip(*locations[::-1]))
        locations = self.clustering_values(locations, 3, 1)
        locations = self.clustering_values(locations, 3, 0)

        return len(locations)
    
    def scan_age(self, flip = False):
        img = self.screenshot
        #img = cv2.imread('AgeOfWarAI/assets/tests/test00.png')
        template1 = cv2.imread('AgeOfWarAI/assets/misc/age1base.png')
        template2 = cv2.imread('AgeOfWarAI/assets/misc/age2base.png')
        template3 = cv2.imread('AgeOfWarAI/assets/misc/age3base.png')
        template4 = cv2.imread('AgeOfWarAI/assets/misc/age4base.png')
        template5 = cv2.imread('AgeOfWarAI/assets/misc/age5base.png')

        img = img[350:,400:]
        if flip:
            img = cv2.flip(img,1)
        
        img = img[:,:-1000]
        result = self.get_position(img, template1, 0.70)
        #self.visualize_locations(img , result)
        if len(result)>=1:
            return 1
        result = self.get_position(img, template2, 0.70)
        if len(result)>=1:
            return 2
        result = self.get_position(img, template3, 0.70)
        if len(result)>=1:
            return 3
        result = self.get_position(img, template4, 0.70)
        if len(result)>=1:
            return 4
        result = self.get_position(img, template5, 0.70)
        if len(result)>=1:
            return 5



if __name__ == "__main__":

    #obj1.screenshot()

    obj = GameVision()
    obj.scan_money_and_xp()

    pass

