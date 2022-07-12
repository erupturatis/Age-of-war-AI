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

    turrets_cost = GLOBAL_VALUES['turrets']
    troops_cost = GLOBAL_VALUES['troops']

    mouse_values = GLOBAL_VALUES['mouse_values']

    def __init__(self, window_manager, assigned_window) -> None:
        self.window_manager = window_manager
        self.assigned_window = assigned_window
        
    def go_back(self):
        pos = self.mouse_values['back']
        pg.moveTo(*pos)
        pg.click()

    def upgrade_age(self):
        pos = self.mouse_values['special']
        pg.moveTo(*pos)
        pg.click()
    
    def access_troops(self):
        pos = self.mouse_values['train_units']
        pg.moveTo(*pos)
        pg.click()

    def spawn_troop(self, tier):
        if self.money > self.troops_cost[self.age][f'tier{tier}']:
            self.access_troops()
            pos = self.mouse_values[f'tier{tier}']
            pg.moveTo(*pos)
            pg.click()
            self.go_back()
            return True
        return False

    def access_turret(self):
        pos = self.mouse_values['get_turret']
        pg.moveTo(*pos)
        pg.click()

    def spawn_turret(self, tier):
        if self.money > self.turrets_cost[self.age][f'tier{tier}'] and self.available_slots>0:
            self.access_turret()
            pos = self.mouse_values[f'tier{tier}']
            pg.moveTo(*pos)
            pg.click()
            slot = None

            for i,x in enumerate(self.slots):
                if x == 0:
                    slot = i
                    break
            
            pos = self.mouse_values[f'turret_spot{i}']
            pg.moveTo(*pos)
            pg.click()

            self.slots[i] = 1
            self.turrets[i] = [tier, self.age]
    

    def use_ability(self):

        if self.check_ability_avalability():
            self.ability_used = time.time()
            pos = self.mouse_values['special']
            pg.moveTo(*pos)
            pg.click()

    def check_ability_avalability(self):
        if self.ability_used == None: return True
        seconds = time.time()
        if seconds - self.ability_used >= 60:
            return True
        return False

    def add_turret_slot(self):
        pos = self.mouse_values['buy_spot']
        pg.moveTo(*pos)
        pg.click()

    def sell_turret_activate(self):
        pos = self.mouse_values['sell_turret']
        pg.moveTo(*pos)
        pg.click()

    def sell_turretn(self, number = 0):
        self.sell_turret_activate()
        pos = self.mouse_values[f'turret_spot{number}']
        pg.moveTo(*pos)
        pg.click()
        self.turrets[number] = [0,0]
        self.slots[number] = 0
        self.available_slots += 1

    def get_inputs(self):
        pass

    def screenshot_environment(self):
        pass

    
  
