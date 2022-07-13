import pyautogui as pg
import time
from GLOBALS import GLOBAL_VALUES

class Env(object):
    assigned_window = 0
    window_manager = None
    age = 1
    ability_used = None
    money = 0
    available_slots = 1
    total_slots = 1
    slots = [0,None,None,None]
    turrets = [
        [0,0],
        [0,0],
        [0,0],
        [0,0]
    ]
    data_grabber = None

    TURRETS_COST = GLOBAL_VALUES['turrets']
    TROOPS_COST = GLOBAL_VALUES['troops']

    MOUSE_VALUES = GLOBAL_VALUES['mouse_values']

    def __init__(self, window_manager, assigned_window, data_grabber) -> None:
        self.window_manager = window_manager
        self.assigned_window = assigned_window
        self.data_grabber = data_grabber
        
    def go_back(self):
        pos = self.MOUSE_VALUES['back']
        pg.moveTo(*pos)
        pg.click()

    def upgrade_age(self):
        pos = self.MOUSE_VALUES['special']
        pg.moveTo(*pos)
        pg.click()
        self.age += 1
    
    def access_troops(self):
        pos = self.MOUSE_VALUES['train_units']
        pg.moveTo(*pos)
        pg.click()

    def spawn_troop(self, tier):
        if self.money > self.TROOPS_COST[self.age][f'tier{tier}']:
            self.access_troops()
            pos = self.MOUSE_VALUES[f'tier{tier}']
            pg.moveTo(*pos)
            pg.click()
            self.go_back()
            return True
        return False

    def access_turret(self):
        pos = self.MOUSE_VALUES['get_turret']
        pg.moveTo(*pos)
        pg.click()

    def spawn_turret(self, tier):
        if self.money > self.TURRETS_COST[self.age][f'tier{tier}'] and self.available_slots>0:
            self.access_turret()
            pos = self.MOUSE_VALUES[f'tier{tier}']
            pg.moveTo(*pos)
            pg.click()
            slot = None

            for i,x in enumerate(self.slots):
                if x == 0:
                    slot = i
                    break
            
            pos = self.MOUSE_VALUES[f'turret_spot{i}']
            pg.moveTo(*pos)
            pg.click()

            self.slots[i] = 1
            self.turrets[i] = [tier, self.age]
    

    def use_ability(self):

        if self.check_ability_avalability():
            self.ability_used = time.time()
            pos = self.MOUSE_VALUES['special']
            pg.moveTo(*pos)
            pg.click()

    def check_ability_avalability(self):
        if self.ability_used == None: return True
        seconds = time.time()
        if seconds - self.ability_used >= 60:
            return True
        return False

    def add_turret_slot(self):
        pos = self.MOUSE_VALUES['buy_spot']
        pg.moveTo(*pos)
        pg.click()

    def sell_turret_activate(self):
        pos = self.MOUSE_VALUES['sell_turret']
        pg.moveTo(*pos)
        pg.click()

    def sell_turretn(self, number = 0):
        self.sell_turret_activate()
        pos = self.MOUSE_VALUES[f'turret_spot{number}']
        pg.moveTo(*pos)
        pg.click()
        self.turrets[number] = [0,0]
        self.slots[number] = 0
        self.available_slots += 1

    def reset_everything(self):
        self.age = 1
        self.ability_used = None
        self.money = 0
        self.available_slots = 1
        self.total_slots = 1
        self.slots = [0,None,None,None]
        self.turrets = [
            [0,0],
            [0,0],
            [0,0],
            [0,0]
        ]

    def pass_actions(self, action):
        pass

    def get_inputs(self):
        inputs = self.data_grabber(self.assigned_window)
        return inputs

    
  
