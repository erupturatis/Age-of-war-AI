from utils import *
from game_environment import Env
from game_vision import GameVision
from neat_program import NeatClass
from time import time
# about 0.25 seconds per screenshot
# 4 windows would mean an action per second which should be enough

class Master(object):

    number_windows = 1
    wm = None
    gm = None
    envs = list()
    scans = 0

    def __init__(self, number_windows = 1) -> None:
        self.number_windows = number_windows
        self.wm = WindowManagement()
        self.gm = GameVision()
        for i in range(number_windows):
            env = Env(self.wm, i, self.data_for_window)
            self.envs.append(env)

    def start_game(self, window_num):
        pass

    def play_again(self, window_num):
        pass

    def data_for_window(self, window_num):

        self.wm.focus_window(window_num)
        screenshot = self.wm.screenshot()
        self.gm.screenshot = screenshot

        in_train = self.gm.scan_training()
        if self.scans == 0 :
            self.gm.initial_scan_health()
        player_health, enemy_health = self.gm.scan_health()
        print("player hp")
        print(player_health)
        print("enemy hp")
        print(enemy_health)
        self.wm.defocus_window(window_num)
        self.scans += 1
    


if __name__ == "__main__":
    number_of_windows = 1
    master = Master(number_of_windows)
    neats = NeatClass(master.envs)
    neats.neat_algorithm()


    





