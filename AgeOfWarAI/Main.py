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


    def start_game(self, window_num):
        pass

    def play_again(self, window_num):
        pass
    
    def save_data_packets(self, img, data):
        pass
    
    def screenshot(self, window_num):
        self.wm.focus_window(window_num)
        screenshot = self.wm.screenshot()
        self.screenshots[window_num] = screenshot
        self.wm.defocus_window(window_num)

    def data_for_window(self, window_num):

        gm = self.gms[window_num] 
        gm.screenshot = self.screenshots[window_num]
        in_train = gm.scan_training()
        
        gm.initial_scan_health()
        
        player_health, enemy_health = gm.scan_health() # not meaningful time
        
        env = self.envs[window_num]
        
        money, xp = gm.scan_money_and_xp(env) # 0.5 from 2 analysis pytesseract
        
        ability = env.check_ability_avalability()
        
        time1 = time.time()

        troops_age1, troops_age2, troops_age3, troops_age4, troops_age5 = gm.scan_troops(False)
        player_troops_total = list()
        # about 0.4-0.5 seconds
        time2 = time.time()
        for i in range(3):
            player_troops_total.append(troops_age1[i] + troops_age2[i] + troops_age3[i] + troops_age4[i] + troops_age5[i])

        if env.age == 5:
            player_troops_total.append(troops_age5[3])
        else:
            player_troops_total.append(0)

        troops_age1, troops_age2, troops_age3, troops_age4, troops_age5 = gm.scan_troops(True)
        enemy_troops_total = list()
        for i in range(3):
            enemy_troops_total.append(troops_age1[i] + troops_age2[i] + troops_age3[i] + troops_age4[i] + troops_age5[i])

        if env.age == 5:
            enemy_troops_total.append(troops_age5[3])
        else:
            enemy_troops_total.append(0)

        slots_available = env.available_slots

        turrets = env.turrets

        age = [0,0,0,0,0]
        age[env.age-1] = 1

        self.wm.defocus_window(window_num)
        self.scans += 1
    


if __name__ == "__main__":
    number_of_windows = 5
    master = Master(number_of_windows)
    neats = NeatClass(master.envs)
    neats.neat_algorithm()


    





