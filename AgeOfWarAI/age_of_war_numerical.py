#numerical version of the game to speed up training, simulating a gym environment for age of war
from GLOBALS import GLOBAL_VALUES

class Game(object):
    printing = False
    class Troop(object):

        hp = None
        damage = None
        range = None
        length = None
        age = None
        tier = None
        reward = None
        position = None


        def __init__(self, hp, damage, range, length, age, tier) -> None:
            self.hp = hp
            self.damage = damage
            self.range = range
            self.age = age
            self.length = length
            self.tier = tier
            self.position = 0
            reward = GLOBAL_VALUES["troops"][age][f"tier{tier}"] * 1.33
            reward = int(reward)

        def die(self):
            return self.reward
            

    class Turret(object):
        damage = None
        range = None

        def __init__(self, damage, range) -> None:
            self.damage = damage
            self.range = range
    

    TURRETS_COST = GLOBAL_VALUES['turrets']
    TROOPS_COST = GLOBAL_VALUES['troops']

    ACTIONS = [
        "troop_tier1", "troop_tier2", "troop_tier3", "troop_tier4",
        "buy_turret_slot",
        "turret_tier1","turret_tier2","turret_tier3",
        "sell_turret1","sell_turret2","sell_turret3","sell_turret4",
        "evolve",
        "wait",
        "ability",
    ]
    BASE_HP = [500, 1100, 2000, 3200, 4700]

    TURRET_MATCHER = {
        # matching by age and tier
        # return damage, range
        "1":{
            "1": (16, 20),
            "2": (20, 20),
            "3": (30, 20)
        },
        "2":{
            "1": (25, 20),
            "2": (40, 20),
            "3": (200, 5)
        },
        "3":{
            "1": (50, 40),
            "2": (100, 40),
            "3": (200, 40)
        },
        "4":{
            "1": (300,40),
            "2": (400,40),
            "3": (700,40)
        },
        "5":{
            "1": (800,50),
            "2": (1500,60),
            "3": (2500,75),
        }
    }

    TROOP_MATCHER = {
        # matching by age and tier
        # return hp, damage, range and length 
        "1":{
            "1": (60,15,3,5),
            "2": (40,12,15,5),
            "3": (135,25,3,10)
        },
        "2":{
            "1": (100,25,3,5),
            "2": (70,20,15,5),
            "3": (500,40,3,10)
        },
        "3":{
            "1": (250,40,3,5),
            "2": (150,20,15,5),
            "3": (1000,80,3,5)
        },
        "4":{
            "1": (750,100,3,5),
            "2": (500,80,15,5),
            "3": (5000,200,3,5)
        },
        "5":{
            "1": (900,200,3,5),
            "2": (500,180,15,5),
            "3": (4000,450,3,5),
            "4": (80000,1000,15,5),
        }
    }

    player_turrets = list()
    enemy_turrets = list()
    player_troops = list()
    enemy_troops = list()

    player_money = 175
    player_xp = 0

    player_age = 1
    enemy_age = 1
    
    player_base = 500
    enemy_base = 500
    in_training = list()
    available_slots = 1
    total_slots = 1
    enemy_slots = 1
    total_enemy_slots = 1

    def training(self):
        if len(self.in_training) > 0:
            self.in_training[0]["time"] -= 1
            if self.in_training[0]["time"] <= 0:

                age = self.in_training[0]["age"]
                tier =  self.in_training[0]["tier"]
                obj = self.TROOP_MATCHER[f"{age}"][f"{tier}"]
                self.player_troops.append(
                    self.Troop(*obj, age, tier)
                )
            self.in_training.pop(0)
    


    def __init__(self) -> None:
        pass

    def debug(self):
        print(f"player age {self.player_age}")
        print(f"player base {self.player_base}")
        print(f"player money {self.player_money}")
        print(f"player troops {self.player_troops}")
        print(f"player turrets {self.player_turrets}")
        print(f"player xp {self.player_xp}")
    
    def spawn_troop(self, tier):
        if self.player_money >= self.TROOPS_COST[self.age][f'tier{tier}']:
            self.player_money -= self.TROOPS_COST[self.age][f'tier{tier}']
            self.in_training.append(
                {
                    "time": self.player_age * tier / 2,
                    "tier": tier,
                    "age": self.player_age
                }
            )
            return True
        return False

    def add_turret_slot(self):
        if GLOBAL_VALUES["turret_slots"][self.total_slots-1] == None:
            return False
        if self.player_money >= GLOBAL_VALUES["turret_slots"][self.total_slots-1]:
            self.player_money -= GLOBAL_VALUES["turret_slots"][self.total_slots-1]
            self.available_slots += 1
            self.total_slots += 1
            return True
        return False
    
    def spawn_turret(self, tier):
        if self.player_money >= self.TURRETS_COST[self.player_age][f'tier{tier}'] and self.available_slots > 0:
            self.money -= self.TURRETS_COST[self.player_age][f'tier{tier}']
            obj = self.TURRET_MATCHER[f"{self.player_age}"][f"{tier}"] # matching with the stats
            self.player_turrets.append(
                (obj, tier, self.player_age)
            )
            self.available_slots -= 1
            return True
        return False
    
    def sell_turret(self, number):

        if len(self.player_turrets) >= number:
            turret_age = self.player_turrets[number-1][2]
            turret_tier = self.player_turrets[number-1][1]

            self.player_turrets.pop(number-1)
            self.available_slots += 1
            self.player_money += self.TURRETS_COST[turret_age][f'tier{turret_tier}']/2
            return True

        return False

    def upgrade_age(self):
        cost = GLOBAL_VALUES["experience"][self.player_age-1]
        if(cost == None):
            return False
        if self.player_xp >= cost:
            self.player_age += 1
            return True
        return False
    
    def nothing(self):
        return True
    
    def use_ability(self):
        i = len(self.enemy_troops)-1
        while i >= 1:
            money = self.enemy_troops.die()
            self.player_money += money
            self.player_xp += money * 2
            self.enemy_troops.pop(i)
            i -= 2


    def spawn_troop1(self):
        return self.spawn_troop(1)
    
    def spawn_troop2(self):
        return self.spawn_troop(2)

    def spawn_troop3(self):
        return self.spawn_troop(3)
    
    def spawn_troop4(self):
        if self.player_age == 5:
            return self.spawn_troop(4)
        return False
    
    def spawn_turret1(self):
        return self.spawn_turret(1)
    
    def spawn_turret2(self):
        return self.spawn_turret(2)

    def spawn_turret3(self):
        return self.spawn_turret(3)

    def sell_turret1(self):
        return self.sell_turret(1)

    def sell_turret2(self):
        return self.sell_turret(2)

    def sell_turret3(self):
        return self.sell_turret(3)

    def sell_turret4(self):
        return self.sell_turret(4)

    
    def take_action(self, action):
        # player taking action
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
            "wait":self.nothing,
            "ability":self.use_ability,
        }
        #print(f"{self.assigned_window} with action {action}")
        action = ACTIONS_DICT[action]
        res = action()
        return res
    
    def spawn_troop_enemy(self, tier):

        age = self.enemy_age
        obj = self.TROOP_MATCHER[f"{age}"][f"{tier}"]
        troop = self.Troop(*obj, age, tier)
        troop.position = 100
        self.enemy_troops.append(troop)
        return True 

    def spawn_turret_enemy(self, tier):
        if self.enemy_slots >= 1:
            age = self.enemy_age
            obj = self.TURRET_MATCHER[f"{age}"][f"{tier}"]
            self.enemy_turrets.append(obj)
            self.enemy_slots -= 1
    
    def sell_turret_enemy(self):
        self.enemy_turrets.pop(0)
    
    def add_slot_enemy(self):
        self.total_enemy_slots += 1
        self.enemy_slots += 1

    def enemy_action(self):
        # enemy taking action
        pass

    def get_inputs(self):
        inputs = (self.in_training, self.player_base )

    def move_troops(self):
        pass

    def shoot_turrets(self):
        pass

    def step(self):
        # will step 1 second in time
        # before thisthe player will take an action
        self.enemy_action()
        self.move_troops()
        self.shoot_turrets()
        self.debug()




