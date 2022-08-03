#numerical version of the game to speed up training, simulating a gym environment for age of war
from GLOBALS import GLOBAL_VALUES
import math
import time
from random import choices

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
            self.length = length # minimum distance between this troop and the one behind it
            self.tier = tier
            self.position = 0
            reward = GLOBAL_VALUES["troops"][age][f"tier{tier}"] * 1.33
            reward = int(reward)

        def die(self):
            return self.reward
            

    class Turret(object):
        damage = None
        range = None
        tier = None
        age = None

        def __init__(self, damage, range, age, tier) -> None:
            self.damage = damage
            self.range = range
            self.age = age
            self.tier = tier
    

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
    last_enemy_action = 0

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
    battle_place = 1

    player_age = 1
    enemy_age = 1
    
    player_base = 500
    enemy_base = 500
    in_training = list()
    available_slots = 1
    total_slots = 1
    enemy_slots = 1
    total_enemy_slots = 1
    ability_used = None
    iterations = 0

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

    def debug(self):
        print(f"player age {self.player_age}")
        print(f"player base {self.player_base}")
        print(f"player money {self.player_money}")
        print(f"player xp {self.player_xp}")
        print(f"player troops {self.player_troops}")
        print(f"player turrets {self.player_turrets}")
        
    
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
            turret = self.Turret(*obj, self.player_age, tier)
            self.player_turrets.append(
                turret
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
    
    def check_ability(self):
        if self.ability_used == None:
            return True
        
        if self.iterations - self.ability_used > 60:
            return True
        return False

    
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

    

    def get_inputs(self):
        player_hp = self.player_base/self.BASE_HP[self.player_age-1]
        enemy_hp = self.enemy_base/self.BASE_HP[self.enemy_age-1]
        tier3_cost = GLOBAL_VALUES["troops"][self.player_age]["tier3"]
        money = self.player_money/tier3_cost
        xp = self.player_xp/GLOBAL_VALUES["experience"][self.player_age-1]
        battle_place = self.battle_place
        ability = self.check_ability()
        ability = 1 if ability else 0
        player_troops_total = [0,0,0,0]
        for troop in self.player_troops:
            player_troops_total[troop.tier-1] += 1
        enemy_troops_total = [0,0,0,0]
        for troop in self.enemy_troops:
            enemy_troops_total[troop.tier-1] += 1
        slots_available = self.available_slots
        age = [0,0,0,0,0]
        age[self.player_age-1] = 1
        enemy_age = [0,0,0,0,0]
        enemy_age[self.enemy_age-1] = 1
        new_turrets = list()
        

        for turret in self.player_turrets:
            turr_age = turret.age
            tier = turret.tier
            if turr_age != 0:
                sig_tier = self.stable_sigmoid(tier)
                new_turrets.append(sig_tier) # turret exists
                if turr_age == self.player_age:
                    new_turrets.append(1)
                else:
                    new_turrets.append(-1)
            else:
                new_turrets.append(0)
                new_turrets.append(0)
        
        while len(new_turrets) != 8:
            new_turrets.append(0)

        inputs = (self.in_training, player_hp, enemy_hp, money, xp, battle_place, ability, *player_troops_total, *enemy_troops_total, slots_available, *age, *enemy_age, *new_turrets)

    def move_troops(self):
        if (self.enemy_troops[0].position - self.player_troops[0].position) <= 3:
            pass # they attack each other
        elif (self.enemy_troops[0].position - self.player_troops[0].position) <= 20:
            dif = (self.enemy_troops[0].position - self.player_troops[0].position)
            self.enemy_troops[0].position -= dif/2
            self.player_troops[0].position += dif/2
            self.enemy_troops[0].position += 1
            self.player_troops[0].position -= 1
        else:
            self.enemy_troops[0].position -= 10
            self.player_troops[0].position += 10
            # calculating positions of troops facing each other

        self.enemy_troops[0].position = max(0, self.enemy_troops[0].position)
        self.player_troops[0].position = min(100, self.player_troops[0].position)
        
        for i in range(len(self.enemy_troops)):
            # calculating positions for enemy troops
            if i == 0 : continue
            pos1 = self.enemy_troops[i-1].position
            pos2 = self.enemy_troops[i].position
            if pos2 - pos1 <= self.enemy_troops[i-1].length:
                pass
            elif pos2 - pos1 > self.enemy_troops[i-1].length and pos2 - pos1 <= 10 + self.enemy_troops[i-1].length:
                pos2 = pos1 + self.enemy_troops[i-1].length
            else:
                pos2 -= 10

            self.enemy_troops[i] = pos2

        for i in range(len(self.player_troops)):
            # calculating positions for player troops
            if i == 0 : continue
            pos1 = self.enemy_troops[i-1].position
            pos2 = self.enemy_troops[i].position
            if pos1 - pos2 <= self.enemy_troops[i-1].length:
                pass
            elif pos1 - pos2 > self.enemy_troops[i-1].length and pos1 - pos2 <= 10 + self.enemy_troops[i-1].length:
                pos2 = pos1 - self.enemy_troops[i-1].length
            else:
                pos2 += 10

            self.enemy_troops[i] = pos2        


    def attacks(self):
        # attacking bases
        if len(self.enemy_troops) == 0:
            for troop in self.player_troops:
                if 100 - troop.position <= troop.range:
                    self.enemy_base -= troop.damage

        if len(self.player_troops) == 0:
            for troop in self.enemy_troops:
                if troop.position <= troop.range:
                    self.player_base -= troop.damage

        # attacking enemy troops
        pos_enemy = self.enemy_troops[0]
        for troop in self.player_troops:
            if pos_enemy - troop.position <= troop.range:
                self.enemy_troops[0].hp -= troop.damage

        # attacking player troops
        pos_player = self.player_troops[0]
        for troop in self.enemy_troops:
            if troop.position - pos_player <= troop.range:
                self.player_troops[0].hp -= troop.damage
        
        # attacking turrets
        pos_enemy = self.enemy_troops[0]
        for turret in self.player_turrets:
            if pos_enemy <= turret.range:
                self.enemy_troops[0].hp -= turret.damage

        pos_player = self.player_troops[0]
        for turret in self.player_turrets:
            if 100 - pos_player <= turret.range:
                self.player_troops[0].hp -= turret.damage

        # eliminating dead troops
        if self.player_troops[0].hp < 0:
            self.player_troops.pop(0)
        if self.enemy_troops[0].hp < 0:
            self.enemy_troops.pop(0)
        


    def enemy_action(self):
        # enemy taking action
        if self.enemy_age != 5:
            if self.player_xp / GLOBAL_VALUES[self.player_age-1] > 0.8:
                self.enemy_age += 1
                return 

        ACTION = {
            0: self.spawn_troop_enemy,
            1: self.add_slot_enemy,
            2: self.spawn_turret_enemy,
            3: self.sell_turret_enemy,
            4: self.upgrade_age
        }
        if len(self.enemy_troops) == 0 :
            population = [0,1,2,3,4,5]
            actions = []
            action = choices(population, action)


    def step(self):
        # will step 1 second in time
        # before this function the player will take an action
        self.enemy_action()
        self.move_troops()
        self.attacks()
        




