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
    envs = list()

    def __init__(self, number_windows = 1) -> None:
        self.number_windows = number_windows
        self.wm = WindowManagement()
        for i in range(number_windows):
            env = Env(self.wm, i, self.data_for_window)
            self.envs.append(env)


    def data_for_window(self, window_num):
        return [window_num]
        self.wm.focus_window(window_num)
        screenshot = self.wm.screenshot()
    
    def get_environments(self):
        return self.envs

    

if __name__ == "__main__":
    number_of_windows = 1
    master = Master(1)
    neats = NeatClass(master.envs)
    neats.neat_algorithm()


    





