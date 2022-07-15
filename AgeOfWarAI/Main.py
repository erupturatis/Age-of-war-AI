from utils import *
from game_environment import Env
from game_vision import GameVision
from neat_program import NeatClass
from time import time
from GLOBALS import GLOBAL_VALUES
import time
import os
# about 0.25 seconds per screenshot
# 4 windows would mean an action per second which should be enough

class Master(object):

    number_windows = 1
    wm = None

    gms = list()
    envs = list()
    screenshots = list()
    data = list()

    scans = 0

    def __init__(self, number_windows = 1, difficulty = 1) -> None:

        self.number_windows = number_windows
        self.wm = WindowManagement()
        
        for i in range(number_windows):
            gm = GameVision()
            env = Env(self.wm, i, self)
            env.difficulty = difficulty

            self.envs.append(env)
            self.gms.append(gm)
            self.screenshots.append(1)
            self.data.append(None)


    def start_game(self, window_num):
        pass

    def play_again(self, window_num):
        pass
    
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
        
        screenshot = self.wm.screenshot()
        self.screenshots[window_num] = screenshot
        env = self.envs[window_num]
        time1 = time.time()
        gm = self.gms[window_num] 
        gm.screenshot = self.screenshots[window_num]

        ended = gm.check_if_ended()
        # print(ended)
        if ended:
            return None, True
        money, xp = gm.scan_money_and_xp(env) # 0.5 from 2 analysis pytesseract

        in_train = gm.scan_training()

        gm.initial_scan_health()

        player_health, enemy_health = gm.scan_health() # not meaningful time
        
        env = self.envs[window_num]
        
        
        
        ability = env.check_ability_avalability()
        
        max_player = 1
        max_enemy = 0
        if env.player_aged_recently > 0:
            # also checks for troops from previous age
            env.player_aged_recently -= 1 
            arr1,arr2 = gm.scan_troops(False, env.age, True)
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

            if env.age == 5:
                player_troops_total.append(arr1[3])
            else:
                player_troops_total.append(0)
        
        if env.enemy_aged_recently > 0:
            env.enemy_aged_recently -= 1
            arr1,arr2 = gm.scan_troops(True, env.enemy_age, True)
            if gm.maximum != -0:
                max_enemy = gm.maximum / gm.width
                gm.maximum = 0

            enemy_troops_total = list()
            for i in range(3):
                enemy_troops_total.append(arr1[i] + arr2[i])

            if env.age == 5:
                enemy_troops_total.append(arr2[3])
            else:
                enemy_troops_total.append(0)
        else:
            arr1 = gm.scan_troops(True, env.enemy_age, False)
            if gm.maximum != -0:
                max_enemy = gm.maximum / gm.width
                gm.maximum = 0

            enemy_troops_total = arr1
            
            if env.age == 5:
                enemy_troops_total.append(arr1[3])
            else:
                enemy_troops_total.append(0)

        battle_place = min(max_player, 1-max_enemy)
      

        slots_available = env.available_slots

        turrets = env.turrets

        age = [0,0,0,0,0]
        age[env.age-1] = 1

        enemy_age_index = gm.scan_age(flip = True)

        if env.enemy_age != enemy_age_index:
            env.enemy_age = enemy_age_index
            env.enemy_aged_recently = 5

        enemy_age = [0,0,0,0,0]
        enemy_age[enemy_age_index-1] = 1

        #self.wm.defocus_window(window_num)
        time2 = time.time()
        # print(time2-time1)
  
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
            ["turrets", turrets],
        ]
        # normalizing money value to age
        tier1_cost = GLOBAL_VALUES["troops"][env.age]["tier1"]
        
        env.money = money
        env.xp = xp

        money = money / tier1_cost
        xp = xp / GLOBAL_VALUES["experience"][env.age-1]
        if ability == True:
            ability = 1
        else:
            ability = 0
        new_turrets = list()
        for turret in turrets:
            tier,turr_age = turret[0], turret[1]
            new_turrets.append(tier)
            new_turrets.append(turr_age)
        
       
        
        inputs = (in_train, player_health, enemy_health, money,xp, battle_place, ability, *player_troops_total, *enemy_troops_total, slots_available, *age, *enemy_age, *new_turrets)
        data_packet.append(["inputs in network", inputs])
        self.data[window_num] = data_packet
        # if self.scans % 25 == 0:
        #     self.save_data_packets(window_num)
        self.scans += 1
        return inputs, False
        
    

if __name__ == "__main__":
    number_of_windows = 2
    difficulty = 3
    master = Master(number_of_windows, difficulty)
    neats = NeatClass(master.envs)
    neats.master = master
    neats.main()


    





