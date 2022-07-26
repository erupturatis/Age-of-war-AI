import pyautogui as pg
import time
from GLOBALS import GLOBAL_VALUES

class Env(object):
    difficulty = 1
    assigned_window = 0
    age = 1
    enemy_age = 1
    player_aged_recently = 0 # also scanning the previous age for this amount of times
    enemy_aged_recently = 0

    ability_used = None
    money = 175
    xp = 0
    available_slots = 1
    total_slots = 1
    slots = [0,None,None,None]
    prev_money = -1
    printing = False
    costly_action_taken = -1

    turrets = [
        [0,0],
        [0,0],
        [0,0],
        [0,0]
    ]
    data_grabber = None
    screenshot_grabber = None

    TURRETS_COST = GLOBAL_VALUES['turrets']
    TROOPS_COST = GLOBAL_VALUES['troops']

    MOUSE_VALUES = GLOBAL_VALUES['mouse_values']

    ACTIONS = [
        "troop_tier1", "troop_tier2", "troop_tier3", "troop_tier4",
        "buy_turret_slot",
        "turret_tier1","turret_tier2","turret_tier3",
        "sell_turret1","sell_turret2","sell_turret3","sell_turret4",
        #"ability",
        "evolve",
        "wait",
    ]
    

    def __init__(self, window_manager, assigned_window, master) -> None:
        self.window_manager = window_manager
        self.assigned_window = assigned_window
        self.master = master
        
    def go_back(self):
        pos = self.MOUSE_VALUES['back']
        pg.moveTo(*pos)
        pg.click()

    def revert_turret_buying(self):
        if self.prev_money != -1:
            if self.money > self.prev_money * 1.5:
                print("reverted turret buying once")
                self.slots[self.total_slots-1] = None
                self.turrets[self.total_slots-1] = [0,0]
                self.available_slots -= 1
                self.total_slots -= 1

            if self.money != self.prev_money:
                self.prev_money = -1
        

    def upgrade_age(self):
        cost = GLOBAL_VALUES["experience"][self.age-1]
        if(cost == None):
            return False
        if self.xp >= cost:
            pos = self.MOUSE_VALUES['evolve']
            pg.moveTo(*pos)
            pg.click()
            self.player_aged_recently = 5
            self.age += 1
            return True
        return False
        
    def access_troops(self):
        pos = self.MOUSE_VALUES['train_units']
        pg.moveTo(*pos)
        pg.click()

    def spawn_troop(self, tier):

        if self.money >= self.TROOPS_COST[self.age][f'tier{tier}']:
            self.costly_action_taken = 1
            self.access_troops()
           # print("troops accesed")
            self.money -= self.TROOPS_COST[self.age][f'tier{tier}']
            pos = self.MOUSE_VALUES[f'tier{tier}']
            pg.moveTo(*pos)
            pg.click()
            #print("clicked")
            self.go_back()
            return True
        return False

    def spawn_troop1(self):
        return self.spawn_troop(1)
    
    def spawn_troop2(self):
        return self.spawn_troop(2)
    
    def spawn_troop3(self):
        return self.spawn_troop(3)

    def spawn_troop4(self):
        if self.age == 5:
            return self.spawn_troop(4)
        return False

    def access_turret(self):
        pos = self.MOUSE_VALUES['get_turret']
        pg.moveTo(*pos)
        pg.click()

    def spawn_turret(self, tier):

        if self.money >= self.TURRETS_COST[self.age][f'tier{tier}'] and self.available_slots > 0:
            #print(self.available_slots)
            self.access_turret()
            self.costly_action_taken = 1
            self.money -= self.TURRETS_COST[self.age][f'tier{tier}']
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

            self.slots[slot] = 1
            
      
            self.turrets[slot] = [tier, self.age]
            self.available_slots -= 1
            return True
        return False
    
    def spawn_turret1(self):
        return self.spawn_turret(1)
    
    def spawn_turret2(self):
        return self.spawn_turret(2)

    def spawn_turret3(self):
        return self.spawn_turret(3)
    

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
        if GLOBAL_VALUES["turret_slots"][self.total_slots-1] == None:
            return False
        if self.money >= GLOBAL_VALUES["turret_slots"][self.total_slots-1]:
            #print(f"money buying slot {self.money}")
            self.costly_action_taken = 1
            #self.money -= GLOBAL_VALUES["turret_slots"][self.total_slots-1]
            self.prev_money = self.money
            self.money -= GLOBAL_VALUES["turret_slots"][self.total_slots-1]
            pos = self.MOUSE_VALUES['buy_spot']
            pg.moveTo(*pos)
            pg.click()
            self.available_slots += 1
            self.total_slots += 1
            self.slots [self.total_slots-1] = 0
            return True
        return False

    def sell_turret_activate(self):
        pos = self.MOUSE_VALUES['sell_turret']
        pg.moveTo(*pos)
        pg.click()

    def sell_turretn(self, number = 0):
        if self.slots[number] == 1:
            self.sell_turret_activate()
            pos = self.MOUSE_VALUES[f'turret_spot{number}']
            # print(f"selling turret on slot {number}")
            pg.moveTo(*pos)
            pg.click()
            self.turrets[number] = [0,0]
            self.slots[number] = 0
            self.available_slots += 1
            return True
        return False
    
    def sell_turret1(self):
        return self.sell_turretn(0)

    def sell_turret2(self):
        return self.sell_turretn(1)

    def sell_turret3(self):
        return self.sell_turretn(2)

    def sell_turret4(self):
        return self.sell_turretn(3)

    def reset_everything(self):
        self.age = 1
        self.ability_used = None
        self.money = 175
        self.available_slots = 1
        self.total_slots = 1
        self.slots = [0,None,None,None]
        self.xp = 0
        self.enemy_aged_recently = 0
        self.player_aged_recently = 0
        self.enemy_age = 1
        self.age = 1

        self.turrets = [
            [0,0],
            [0,0],
            [0,0],
            [0,0]
        ]

    def take_action(self, action):
        action = self.ACTIONS[action]
        if self.printing:
            print(f"trying to do action {action}")
        ACTIONS_DICT = {
            "troop_tier1":self.spawn_troop1, 
            "troop_tier2":self.spawn_troop2, 
            "troop_tier3":self.spawn_troop3, 
            "troop_tier4":self.spawn_troop4,
            "buy_turret_slot":self.add_turret_slot,
            "turret_tier1":self.spawn_turret1,
            "turret_tier2":self.spawn_turret2,
            "turret_tier3":self.spawn_turret3,
            "sell_turret1":self.sell_turret1,
            "sell_turret2":self.sell_turret2,
            "sell_turret3":self.sell_turret3,
            "sell_turret4":self.sell_turret4,
            "evolve":self.upgrade_age,
            #"ability":self.use_ability,
            "wait":self.nothing,
        }
        #print(f"{self.assigned_window} with action {action}")
        action = ACTIONS_DICT[action]
        res = action()
        return res


    def nothing(self):
        return True


    def get_inputs(self):
        inputs = self.master.data_for_window(self.assigned_window)
        return inputs


    def screenshot(self):
        screenshot = self.master.screenshot(self.assigned_window)
        return screenshot


    def focus(self):
        self.master.focus(self.assigned_window)


    def defocus(self):
        self.master.defocus(self.assigned_window)

    def start_game(self):
        #print("starting game")
        self.reset_everything()
        pg.moveTo(*GLOBAL_VALUES["play"])
        pg.click()
        #print("moved to play")
        difficulty = self.difficulty
        pg.moveTo(*GLOBAL_VALUES[f"diff{difficulty}"])
        pg.click()

    def restart_game(self):
        self.reset_everything()
        pg.moveTo(*GLOBAL_VALUES[f"restart"])
        pg.click()

        pg.moveTo(*GLOBAL_VALUES["play"])
        pg.click()
        difficulty = self.difficulty
        pg.moveTo(*GLOBAL_VALUES[f"diff{difficulty}"])
        pg.click()


    
  
