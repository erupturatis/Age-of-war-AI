from utils import *
from game_environment import Env
from game_vision import GameVision
from neat_program import NeatClass
from time import time
from GLOBALS import GLOBAL_VALUES
import time
import os
from paddleocr import PaddleOCR
import math
# about 0.25 seconds per screenshot
# 4 windows would mean an action per second which should be enough

class Master(object):

    number_windows = 1
    wm = None
    ocr = None
    gms = list()
    envs = list()
    screenshots = list()
    data = list()

    scans = 0

    def __init__(self, number_windows = 1, difficulty = 1) -> None:

        self.number_windows = number_windows
        self.wm = WindowManagement()

        ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False) # need to run only once to download and load model into memory
        self.ocr = ocr

        

        for i in range(number_windows):
            gm = GameVision()
            env = Env(self.wm, i, self)
            env.difficulty = difficulty
            
            self.envs.append(env)
            self.gms.append(gm)
            self.screenshots.append(1)
            self.data.append(list())


    def stable_sigmoid(self, x):
        if type(x) == list:
            x_new = [self.stable_sigmoid(i) for i in x]
            return x_new
        else:
            if x >= 0:
                z = math.exp(-x)
                sig = 1 / (1 + z)
                return sig
            else:
                z = math.exp(x)
                sig = z / (1 + z)
                return sig

    def save_all_data_packets(self):
        for window_num in range(len(self.envs)):
            img = self.screenshots[window_num]
            data = self.data[window_num]
            if not os.path.exists(f"data_samples/sample{self.scans}"):
                os.makedirs(f"data_samples/sample{self.scans}")

            cv2.imwrite(f"data_samples/sample{self.scans}/image{window_num} {self.scans}.png", img)
            with open(f'data_samples/sample{self.scans}/data{window_num} {self.scans}.txt', 'w') as f:
                for elem in data:
                    f.write(f"{elem}")
                    f.write("\n")
            f.close()


    def add_to_data_packet(self, window_num, data):
        
        self.data[window_num].append(data)


    def save_data_packets(self, window_num):
        img = self.screenshots[window_num]
        data = self.data[window_num]
        if not os.path.exists(f"data_samples/sample{self.scans}"):
            os.makedirs(f"data_samples/sample{self.scans}")

        cv2.imwrite(f"data_samples/sample{self.scans}/image{self.scans}.png", img)
        with open(f'data_samples/sample{self.scans}/data{self.scans}.txt', 'w') as f:
            for elem in data:
                f.write(f"{elem}")
                f.write("\n")
        f.close()
    
    def screenshot(self, window_num):
        self.wm.focus_window(window_num)
        screenshot = self.wm.screenshot()
        self.screenshots[window_num] = screenshot
        self.wm.defocus_window(window_num)
        return screenshot

    def focus(self, window_num):
        self.wm.focus_window(window_num)
    
    def defocus(self, window_num):
        self.wm.defocus_window(window_num)

    def data_for_window(self, window_num):
        # screenshot included in data flow
        
        env = self.envs[window_num]
        
        screenshot = self.wm.screenshot()
        self.screenshots[window_num] = screenshot
        
        gm = self.gms[window_num] 
        gm.screenshot = self.screenshots[window_num]
        gm.ocr = self.ocr
       
        
        ended = gm.check_if_ended() # can be cut down when visualizing winner
        
        
        if ended:
            victory = gm.check_victory()
            return victory, True

        
        
        if env.check_ability_time() > 6.5 :
            player_age_index = gm.scan_age(flip = False)
            in_train = gm.scan_training()
            gm.initial_scan_health()
            player_health, enemy_health = gm.scan_health() # not meaningful time
            if player_health == None or enemy_health == None:
                player_health = env.hp
                enemy_health = env.enemy_hp
            enemy_age_index = gm.scan_age(flip = True)
        else:
            player_age_index = env.age
            in_train = 0
            player_health = env.hp
            enemy_health = env.enemy_hp
            enemy_age_index = env.enemy_age

        money, xp = gm.scan_money_and_xp(env) 
        
        ability = env.check_ability_avalability()

        Error = gm.scan_cancel()
        if Error:
            pyautogui.click(1675,100)
        if player_age_index != None:
            env.age = player_age_index

        max_player = 1
        max_enemy = 0
        enemy_troops_total = [0,0,0,0]
        player_troops_total = [0,0,0,0]


        if env.player_aged_recently > 0:
            # also checks for troops from previous age
            env.player_aged_recently -= 1 
            try:
                arr1,arr2 = gm.scan_troops(False, env.age, True)
            except:
                arr1 = [0,0,0,0]
                arr2 = [0,0,0,0]
            if gm.maximum != 0:
                max_player = gm.maximum / gm.width
                gm.maximum = 0
            
            player_troops_total = list()
            for i in range(3):
                player_troops_total.append(arr1[i] + arr2[i])

            if env.age == 5:
                player_troops_total.append(arr2[3])
            else:
                player_troops_total.append(0)
        else:
            arr1 = gm.scan_troops(False, env.age, False)
            if gm.maximum != 0:
                max_player = gm.maximum / gm.width
                gm.maximum = 0

            player_troops_total = arr1

            if env.age != 5:
                player_troops_total.append(0)


        if env.enemy_aged_recently > 0:
            env.enemy_aged_recently -= 1
            try:
                arr1,arr2 = gm.scan_troops(True, env.enemy_age, True)
            except:
                arr1=[0,0,0,0]
                arr2=[0,0,0,0]
            if gm.maximum != -0:
                max_enemy = gm.maximum / gm.width
                gm.maximum = 0

                enemy_troops_total = list()
                for i in range(3):
                    enemy_troops_total.append(arr1[i] + arr2[i])

                if env.enemy_age == 5:
                    enemy_troops_total.append(arr2[3])
                else:
                    enemy_troops_total.append(0)
          
            
        else:
            arr1 = gm.scan_troops(True, env.enemy_age, False)
            if gm.maximum != -0:
                max_enemy = gm.maximum / gm.width
                gm.maximum = 0

            enemy_troops_total = arr1
            
            if env.enemy_age != 5:
                enemy_troops_total.append(0)
       
                

        battle_place = min(max_player, 1-max_enemy)
      

        slots_available = env.available_slots

        turrets = env.turrets

        new_turrets = list()
        for turret in turrets:
            tier,turr_age = turret[0], turret[1]
            
            if turr_age != 0:
                sig_tier = self.stable_sigmoid(tier)
                new_turrets.append(sig_tier) # turret exists
                if turr_age == env.age:
                    new_turrets.append(1)
                else:
                    new_turrets.append(-1)
            else:
                new_turrets.append(0)
                new_turrets.append(0)

        
        age = [0,0,0,0,0]
        age[env.age-1] = 1
     
        

        if env.enemy_age != enemy_age_index:
            env.enemy_age = enemy_age_index
            env.enemy_aged_recently = 5

        enemy_age = [0,0,0,0,0]
        if enemy_age_index == None:
            enemy_age_index = env.age
            
        enemy_age[enemy_age_index-1] = 1

        #self.wm.defocus_window(window_num)
        time2 = time.time()

  
        data_packet = [
            ["number of troops in training", in_train],
            ["player hp percent", player_health],
            ["enemy hp percent", enemy_health],
            ["money", money],
            ["xp", xp],
            ["battle taking place", battle_place],
            ["can activate ability",ability],
            ["player troops", player_troops_total],
            ["enemy troops",enemy_troops_total],
            ["available slots", slots_available],
            ["player age", age],
            ["enemy age",enemy_age],
            ["enemy age recently", env.enemy_aged_recently],
            ["new turrets", new_turrets],
            ["turrets", turrets],
        ]
        env.hp = player_health
        env.enemy_hp = enemy_health
        # normalizing money value to age
        tier3_cost = GLOBAL_VALUES["troops"][env.age]["tier3"]
        
        env.money = money
        env.xp = xp

        money = money / tier3_cost

        divider =  GLOBAL_VALUES["experience"][env.age-1]
        if divider == None:
            xp = 0
        else:
            xp = xp / divider

        if ability == True:
            ability = 1
        else:
            ability = 0

        total_troops = np.sum(player_troops_total)

        in_train = np.tanh(in_train)
        player_troops_total = np.tanh(player_troops_total)
        enemy_troops_total = np.tanh(enemy_troops_total)
        slots_available = np.tanh(slots_available)

        inputs = (in_train, player_health, enemy_health, money, xp, battle_place, ability, *player_troops_total, *enemy_troops_total, slots_available, *age, *enemy_age, *new_turrets)
        data_packet.append(["inputs in network", inputs])
        self.data[window_num] = data_packet
        # if self.scans % 25 == 0:
        #     self.save_data_packets(window_num)
        self.scans += 1
        return inputs, False, total_troops
        
def run():
    number_of_windows = 1
    difficulty = 1
    
    master = Master(number_of_windows, difficulty)
    neats = NeatClass(master.envs)
    neats.master = master
    neats.main()

def run_unity():
    neats = NeatClass()
    neats.env_batch_size = 50
    neats.main_unity()

if __name__ == "__main__":
    run()


