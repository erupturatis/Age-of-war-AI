from utils import *
from game_environment import Env
from game_vision import GameVision
from neat_program import NeatClass
from time import time
import time
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

    def __init__(self, number_windows = 1) -> None:

        self.number_windows = number_windows
        self.wm = WindowManagement()
        
        for i in range(number_windows):
            gm = GameVision()
            env = Env(self.wm, i, self.data_for_window, self.screenshot)

            self.envs.append(env)
            self.gms.append(gm)
            self.screenshots.append(1)
            self.data.append(None)


    def start_game(self, window_num):
        pass

    def play_again(self, window_num):
        pass
    
    def save_data_packets(self, window_num):
        img = self.screenshots[window_num]
        data = self.data[window_num]
        cv2.imwrite(f"data_samples/image{self.scans}.png", img)
        with open(f'data_samples//data{self.scans}.txt', 'w') as f:
            for elem in data:
                f.write(f"{elem}")
                f.write("\n")
        f.close()
    
    def screenshot(self, window_num):
        self.wm.focus_window(window_num)
        screenshot = self.wm.screenshot()
        self.screenshots[window_num] = screenshot
        self.wm.defocus_window(window_num)

    def data_for_window(self, window_num):
        time1 = time.time()
        gm = self.gms[window_num] 
        gm.screenshot = self.screenshots[window_num]
        in_train = gm.scan_training()
        
        gm.initial_scan_health()
        
        player_health, enemy_health = gm.scan_health() # not meaningful time
        
        env = self.envs[window_num]
        
        money, xp = gm.scan_money_and_xp(env) # 0.5 from 2 analysis pytesseract
        
        ability = env.check_ability_avalability()
        
        
        
        arr1,arr2 = gm.scan_troops(False, env.age)
        max_player = gm.maximum / gm.width
        gm.maximum = 0
        
        player_troops_total = list()
        # about 0.4-0.5 seconds
        
        for i in range(3):
            player_troops_total.append(arr1[i] + arr2[i])

        if env.age == 5:
            player_troops_total.append(arr2[3])
        else:
            player_troops_total.append(0)
        
        arr1,arr2 = gm.scan_troops(True)
        max_enemy = gm.maximum / gm.width
        gm.maximum = 0

        enemy_troops_total = list()
        for i in range(3):
            enemy_troops_total.append(arr1[i] + arr2[i])

        if env.age == 5:
            enemy_troops_total.append(arr2[3])
        else:
            enemy_troops_total.append(0)

        battle_place = min(max_player, 1-max_enemy)

        slots_available = env.available_slots

        turrets = env.turrets

        age = [0,0,0,0,0]
        age[env.age-1] = 1

        self.wm.defocus_window(window_num)
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
            ["turrets", turrets],
        ]
        self.data[window_num] = data_packet
        self.save_data_packets(window_num)

        env.money = money
        env.xp = xp
        
        self.scans += 1
    


if __name__ == "__main__":
    number_of_windows = 1
    master = Master(number_of_windows)
    neats = NeatClass(master.envs)
    neats.neat_algorithm()


    





