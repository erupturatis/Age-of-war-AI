
from ast import Global
import neat
import time
import numpy as np
import os
import pickle
from random import choices
from scipy.stats import stats
import math
import pyautogui
#import visualize
import random
from GLOBALS import GLOBAL_VALUES
import socket

class NeatClass(object):
    envs = None
    number_of_envs = None
    rewards = None
    networks_training = list()
    next_nn = 0
    networks_number = 0
    genomes_list = list()
    networks = list()
    POP_SIZE = None
    inactive_envs = list()
    generation = 1120
    master = None
    valid_actions_streak = list()
    generations_fitnesses = list()
    act = 0
    fitness_med = list()
    population = None
    env_batch_size = 1
 

    def __init__(self, envs = []) -> None:
        self.number_of_envs = len(envs)
        self.envs = envs

    def softmax(self, x):
        """Compute softmax values for each sets of scores in x."""
        e_x = np.exp(x - np.max(x))
        return e_x / e_x.sum()

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

    def start_envs(self):
        for i in range(self.networks_number):
            self.rewards.append(0)

        for i in range(self.number_of_envs):
            
            self.networks_training.append(self.next_nn)
            self.inactive_envs.append(0)

            self.next_nn += 1
            env = self.envs[i]
            env.focus()
            env.start_game()
            env.defocus()
    

    def save_best(self, genomes):
        fitness = 0
        mx = 0
        cnt = 0
        for i,g in enumerate(genomes):
            genome = g[1]
            fitness += genome.fitness
            if genome.fitness > mx:
                mx = genome.fitness
                cnt = i
        
        self.fitness_med = (self.generation, fitness / len(genomes), mx, cnt)
        # print(self.population.best_genome)
        # print(self.population.best_genome[1])

        try:
            with open(f'winner-generation {self.generation}', 'wb') as f:
                pickle.dump(genomes[cnt], f)
        except:
            pass
        
        try:
            with open(f'fitness_scores{self.generation}.txt', 'w') as f:
                f.write(f"{self.fitness_med}")
            f.close()
        except:
            pass

    def eval_genomes(self, genomes, config):
        self.POP_SIZE = len(genomes)

        evaluating = True
        self.genomes_list = list()
        self.networks = list()
        self.inactive_envs = list()
        self.valid_actions_streak = list()
        self.next_nn = 0
        fitness = 0

        time1 = time.time()
        for i in range(self.number_of_envs):
            env = self.envs[i]
            env.focus()
            self.networks_training[i] = self.next_nn
            self.next_nn += 1
            env.restart_game()
            env.defocus()
      
        finished_envs = 0

        for g in genomes:
            genome = g[1]
            net = neat.nn.FeedForwardNetwork.create(genome, config)
            self.networks.append(net) 
            genome.fitness = 0
            self.genomes_list.append(genome)
        

        for i in range(self.number_of_envs):
            self.inactive_envs.append(0)
            self.inactive_envs[i] = 0
            self.valid_actions_streak.append(0)

        interations = 0
        while evaluating:

            interations += 1

            if interations % 100 == 0:
                self.master.save_all_data_packets()

            for i in range(self.number_of_envs):
                if self.inactive_envs[i] == 1:
                    time.sleep(1.3)
                    continue
                env = self.envs[i]

                env.focus()
                inputs, ended = env.get_inputs()
      
                if ended:
                    if self.next_nn >= self.POP_SIZE:
                        finished_envs += 1
                        
                        self.inactive_envs[i] = 1
                        env.defocus()
                     
                        if finished_envs == self.number_of_envs:
                            evaluating = False
                        continue

                    if inputs == True:
                        print("AI WON")
                        self.genomes_list[self.networks_training[i]].fitness += 1000

                    #print(f"FITNESS: {self.genomes_list[self.networks_training[i]].fitness}")
                    env.restart_game()
                    self.networks_training[i] = self.next_nn
                    self.next_nn += 1
                    #print(f"got to {self.next_nn} network")
                    env.defocus()
                    continue

                self.genomes_list[self.networks_training[i]].fitness += 0.2 # reward because the game hasn't ended

                net = self.networks[self.networks_training[i]]


                action = net.activate(inputs)
                action = np.array(action)
                self.master.data[env.assigned_window].append(action)

                action = stats.zscore(action)
                self.master.data[env.assigned_window].append(action)

                action = self.softmax(action)
                population = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]

                if env.xp > 6500000 :
                    # the ai hit a infinite loop so it will lose on purpose
                    # 11 10 9 8 13 heavily increasing probabilities for waiting and selling turrets
                    action[8] += 10
                    action[9] += 10
                    action[10] += 10
                    action[11] += 10
                    action[13] += 10
                    action = random.randint(8,11)
                    
                action = choices(population, action)
               

                self.act += 1
                if action[0] == 13:
                    self.genomes_list[self.networks_training[i]].fitness += 0.1

                if env.check_ability_time() < 6.5 :
                    pyautogui.moveTo(500,500) # recentering screen
                    time.sleep(.25)

                #env.printing = True
                Taken = env.take_action(*action)
                
                # print("--------------------------")
                if Taken == True:
                    self.valid_actions_streak[i] += 1
                    if self.valid_actions_streak[i] > 4:
                        self.valid_actions_streak[i] = 4
                    self.genomes_list[self.networks_training[i]].fitness += 0.015 * self.valid_actions_streak[i]
                    # bonus for taking a valid action
                else:
                    self.valid_actions_streak[i] = 0

                self.master.add_to_data_packet(i, self.generation)

                env.defocus()
       
        
        self.save_best(genomes)

        self.generation += 1
    
    def run_winner(self, config_file, winner):

        config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                            neat.DefaultSpeciesSet, neat.DefaultStagnation,
                            config_file)

        with open(f"{winner}", "rb") as f:
            genome = pickle.load(f)

        net = neat.nn.FeedForwardNetwork.create(genome[1], config)
        print("loaded network")

        evaluating = True
        local_fitness = 0
        valid_actions_streak = 0
        interations = 0
        while evaluating:
            time1 = time.time()
            interations += 1

            # if interations % 10 == 0:
            #     self.master.save_all_data_packets()

            env = self.envs[0]
            env.focus()
            env.printing = True
            inputs, ended, total = env.get_inputs()
      
            if ended:
                if inputs == True:
                    print("AI WON")
                    local_fitness += 10000

                #print(f"FITNESS: {self.genomes_list[self.networks_training[i]].fitness}")
                evaluating = False
                print(f"evaluating ended with fitness {local_fitness}")
                continue

            local_fitness += 0.2 # reward because the game hasn't ended

            action = net.activate(inputs)
            action = np.array(action)
            self.master.data[env.assigned_window].append(action)

            action = stats.zscore(action)
            action = self.softmax(action)

            population = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]
            action = choices(population, action)
            

            self.act += 1
            if total > 6 and action[0] <= 3:
                Taken = False
            else:
                Taken = env.take_action(*action)
            print(Taken)
            print(f"TOTAL TIME {time.time() - time1}")

            if Taken == True:
                valid_actions_streak += 1
                if valid_actions_streak > 4:
                    valid_actions_streak = 4
                local_fitness += 0.00 * valid_actions_streak
                # bonus for taking a valid action
            else:
                valid_actions_streak = 0

        
            self.master.save_all_data_packets()



    def receive_message(self, communication_socket):
   
        s = communication_socket
        full_msg = ''
        new_msg = True
        cp = False
        #print("entr func")
        while True:
       
            msg = s.recv(100)
            if(cp):
                print(f"{msg} bcs of cp")
         
            if new_msg:
                #print("new msg len:",msg)
              
                msg = msg.decode("utf-8")
                bar = msg.find('.')
                try:
                    msglen = int(msg[:bar])
                except:
                    cp = True
                    print("cplm are")
                    if msg[0] == '1':
                        msglen = 1
                    else:
                        msglen = 120
                    print(msg)
                    print(msglen)
                    time.sleep(.25)
                   
                    #raise("problem")

                new_msg = False
            
            try:
                full_msg += msg.decode("utf-8")
            except:
                full_msg += msg
                
            if len(full_msg) >= msglen:
                if cp:
                    print(f"{msglen} len cp")
                    print(f"{full_msg} full msg")
                break

        full_msg = full_msg[full_msg.find('.')+1:]
        return full_msg

    def establish_connection(self):
        HOST = "192.168.100.11"
        PORT = 9090

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((HOST, PORT))

        server.listen(1)
        self.server = server
        communication_socket, address = self.server.accept()
        self.communication_socket = communication_socket


    def run_winner_unity_split(self, config_file, winner):
        #print("got to eval unity")
        config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                            neat.DefaultSpeciesSet, neat.DefaultStagnation,
                            config_file)

        with open(f"{winner}", "rb") as f:
            genome = pickle.load(f)

        net = neat.nn.FeedForwardNetwork.create(genome[1], config)
        print("loaded network")
      
        finished = list()
        fitnesses = list()
        for i in range(self.env_batch_size):
            finished.append(0)
            fitnesses.append(0)

        

        while True :

            #print(f"actions taken per batch {iter} with finished {finished_envs}")
            message = self.receive_message(self.communication_socket)
            #finished = message.count('*')
            message = message.split('|')
            #print(len(message))
            #print(message)
            '''
            '', ' 0 php 1.000 ehp 1.000 mn 17500 xp 999999 bp 0.500 ab 1 ptrps 0 0 0 0  etrps 0 0 0 0  slots 1 age 1 eage 1 turrets 0 0 0 0 0 0 0 0 ', ' 0 php 1.000 ehp 1.000 mn 17500 xp 999999 bp 0.500 ab 1 ptrps 0 0 0 0  etrps 0 0 0 
0  slots 1 age 1 eage 1 turrets 0 0 0 0 0 0 0 0 '

            '''
            message = message[1:]
            actions = ""
            
            
            

            for j in range(self.env_batch_size):
                # processing the network i*50 + j and j environment
                # processing inputs
                mess = message[j] 
                inp = False
                if mess.count('*') != 0:
                    inp = True
                    if finished[j] == 0:
                        finished[j] = 1
                        print(f"FITNESS FOR {j} IS {fitnesses[j]}")

                inp = True
                mess = mess.split(' ')
                #print(mess)
                '''
                ['', '0', 'php', '1.000', 'ehp', '1.000', 'mn', '17500', 'xp', '999999', 'bp', '0.500', 'ab', '1', 'ptrps', '0', '0', '0', '0', '', 'etrps', '0', '0', '0', '0', '', 'slots', '1', 'age', '1', 'eage', '1', 'turrets', '0', '0', '0', '0', '0', '0', '0', '0', '']
                '''
                player_agen = int(mess[29])
                enemy_agen = int(mess[31])

                in_train = int(mess[1])
                player_health = float(mess[3])
                enemy_health = float(mess[5])

                

                money = int(mess[7])
                tier3_cost = GLOBAL_VALUES["troops"][player_agen]["tier3"]
                money = money / tier3_cost
                xp = int(mess[9])
                original_xp = xp
                divider =  GLOBAL_VALUES["experience"][player_agen-1]
                if divider == None:
                    xp = 0
                else:
                    xp = xp / divider
                battle_place = float(mess[11])
                ability = int(mess[13])
                player_troops_total = [int(mess[15]), int(mess[16]), int(mess[17]), int(mess[18])]
                enemy_troops_total = [int(mess[21]), int(mess[22]), int(mess[23]), int(mess[24])]
                slots_available = int(mess[27])
                turrets = [
                    [int(mess[33]),int(mess[34])],
                    [int(mess[35]),int(mess[36])],
                    [int(mess[37]),int(mess[38])],
                    [int(mess[39]),int(mess[40])],
                ]
                #processing data

                new_turrets = list()
                for turret in turrets:
                    tier,turr_age = turret[0], turret[1]
                    
                    if turr_age != 0:
                        sig_tier = np.tanh(tier)
                        new_turrets.append(sig_tier) # turret exists
                        if turr_age == player_agen:
                            new_turrets.append(1)
                        else:
                            new_turrets.append(-1)
                    else:
                        new_turrets.append(0)
                        new_turrets.append(0)

                in_train = np.array(in_train)/5
                player_troops_total = np.array(player_troops_total)/5
                enemy_troops_total = np.array(enemy_troops_total)/5

                # in_train = np.tanh(in_train)
                # player_troops_total = np.tanh(player_troops_total)
                # enemy_troops_total = np.tanh(enemy_troops_total)
                # slots_available = np.tanh(slots_available)

                age = [0,0,0,0,0]
                age[player_agen-1] = 1

                enemy_age = [0,0,0,0,0]
                enemy_age[enemy_agen-1] = 1
                tot_tr = np.sum(player_troops_total)


                money = money + 1
                money = np.log(min(money, 50))
                xp = np.log(min(xp + 1, 20))

                inputs = (in_train, player_health, enemy_health, money, xp, battle_place, ability, *player_troops_total, *enemy_troops_total, slots_available, *age, *enemy_age, *new_turrets)
        
                fitnesses[j] += 0.2 # reward because the game hasn't ended

                #net = self.networks[network_num]
                action = net.activate(inputs)
                action = np.array(action)
           

                action1 = action[0:5] # troop actions
                action2 = action[5:13] # turret actions
                action3 = action[13:15] # buy slot or not
                action4 = action[15:17] # ability or not
                action5 = action[17:19] # upgrade age or not

                if original_xp > 5000000 :
                    # the ai hit a infinite loop so it will lose on purpose
                    # 11 10 9 8 13 heavily increasing probabilities for waiting and selling turrets
                    action2[3] += 100
                    action2[4] += 100
                    action2[5] += 100
                    action2[6] += 100
                    action1[4] += 100
                    reset_hist = True

                action1 = np.argmax(action1)
                action2 = np.argmax(action2)
                action3 = np.argmax(action3)
                action4 = np.argmax(action4)
                action5 = np.argmax(action5)
                
                # population = [0,1,2,3]
                # action3 = stats.zscore(action3)
                # action3 = self.softmax(action3)
                # action3 = random.choices(population, action3)[0]
                '''
                action = np.argmax(action)
                if np.isnan(val):
                    action = 13
                '''
                
                actions += f"{action1}{action2}{action3}{action4}{action5} "

            time2 = time.time()
            
                
            #print(actions)
            #print(time2-time1)
            self.communication_socket.send(f"{actions}".encode("utf-8"))
            #print(finished)
            if finished == 50:
                break
                   
        self.generation += 1
        return reset_hist
    
        


    def run_winner_unity(self, config_file, winner):
        #print("got to eval unity")
        config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                            neat.DefaultSpeciesSet, neat.DefaultStagnation,
                            config_file)

        with open(f"{winner}", "rb") as f:
            genome = pickle.load(f)

        net = neat.nn.FeedForwardNetwork.create(genome[1], config)
        print("loaded network")
      
        finished = list()
        fitnesses = list()
        for i in range(self.env_batch_size):
            finished.append(0)
            fitnesses.append(0)

        

        while True :

            #print(f"actions taken per batch {iter} with finished {finished_envs}")
            message = self.receive_message(self.communication_socket)
            #finished = message.count('*')
            message = message.split('|')
            #print(len(message))
            #print(message)
            '''
            '', ' 0 php 1.000 ehp 1.000 mn 17500 xp 999999 bp 0.500 ab 1 ptrps 0 0 0 0  etrps 0 0 0 0  slots 1 age 1 eage 1 turrets 0 0 0 0 0 0 0 0 ', ' 0 php 1.000 ehp 1.000 mn 17500 xp 999999 bp 0.500 ab 1 ptrps 0 0 0 0  etrps 0 0 0 
0  slots 1 age 1 eage 1 turrets 0 0 0 0 0 0 0 0 '

            '''
            message = message[1:]
            actions = ""
            
            
            

            for j in range(self.env_batch_size):
                # processing the network i*50 + j and j environment
                # processing inputs
                mess = message[j] 
                inp = False
                if mess.count('*') != 0:
                    inp = True
                    if finished[j] == 0:
                        finished[j] = 1
                        print(f"FITNESS FOR {j} IS {fitnesses[j]}")

                inp = True
                mess = mess.split(' ')
                #print(mess)
                '''
                ['', '0', 'php', '1.000', 'ehp', '1.000', 'mn', '17500', 'xp', '999999', 'bp', '0.500', 'ab', '1', 'ptrps', '0', '0', '0', '0', '', 'etrps', '0', '0', '0', '0', '', 'slots', '1', 'age', '1', 'eage', '1', 'turrets', '0', '0', '0', '0', '0', '0', '0', '0', '']
                '''
                player_agen = int(mess[29])
                enemy_agen = int(mess[31])

                in_train = int(mess[1])
                player_health = float(mess[3])
                enemy_health = float(mess[5])

                

                money = int(mess[7])
                tier3_cost = GLOBAL_VALUES["troops"][player_agen]["tier3"]
                money = money / tier3_cost
                xp = int(mess[9])
                original_xp = xp
                divider =  GLOBAL_VALUES["experience"][player_agen-1]
                if divider == None:
                    xp = 0
                else:
                    xp = xp / divider
                battle_place = float(mess[11])
                ability = int(mess[13])
                player_troops_total = [int(mess[15]), int(mess[16]), int(mess[17]), int(mess[18])]
                enemy_troops_total = [int(mess[21]), int(mess[22]), int(mess[23]), int(mess[24])]
                slots_available = int(mess[27])
                turrets = [
                    [int(mess[33]),int(mess[34])],
                    [int(mess[35]),int(mess[36])],
                    [int(mess[37]),int(mess[38])],
                    [int(mess[39]),int(mess[40])],
                ]
                #processing data

                new_turrets = list()
                for turret in turrets:
                    tier,turr_age = turret[0], turret[1]
                    
                    if turr_age != 0:
                        sig_tier = np.tanh(tier)
                        new_turrets.append(sig_tier) # turret exists
                        if turr_age == player_agen:
                            new_turrets.append(1)
                        else:
                            new_turrets.append(-1)
                    else:
                        new_turrets.append(0)
                        new_turrets.append(0)

                in_train = np.tanh(in_train)
                player_troops_total = np.tanh(player_troops_total)
                enemy_troops_total = np.tanh(enemy_troops_total)
                slots_available = np.tanh(slots_available)

                age = [0,0,0,0,0]
                age[player_agen-1] = 1

                enemy_age = [0,0,0,0,0]
                enemy_age[enemy_agen-1] = 1

                inputs = (in_train, player_health, enemy_health, money, xp, battle_place, ability, *player_troops_total, *enemy_troops_total, slots_available, *age, *enemy_age, *new_turrets)
        
                fitnesses[j] += 0.2 # reward because the game hasn't ended

                #net = self.networks[network_num]
                print("INPUTS")
                print(inputs)
                action = net.activate(inputs)
                action = np.array(action)
                print("ACTION")
                print(action)
                action = stats.zscore(action) * 1.5
                action = self.softmax(action)
                
                population = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]
                

                
                if original_xp > 5000000 :
                    # the ai hit a infinite loop so it will lose on purpose
                    # 11 10 9 8 13 heavily increasing probabilities for waiting and selling turrets
                    action[8] += 10
                    action[9] += 10
                    action[10] += 10
                    action[11] += 10
                    action[13] += 10
                    reset_hist = True

                val = action[np.argmax(action)]
                '''
                action = np.argmax(action)
                if np.isnan(val):
                    action = 13
                '''
                if np.isnan(val):
                    action = 13
                else:
                    #action = np.argmax(action)
                    action = choices(population, action)
                    action = action[0]
                    
                if inp:
                    print(action)
                    pass

                actions += f"{action} "

            time2 = time.time()
            
                
            #print(actions)
            #print(time2-time1)
            self.communication_socket.send(f"{actions}".encode("utf-8"))
            #print(finished)
            if finished == 50:
                break
                   
        self.generation += 1
        return reset_hist
    
        #print("GOT TO THE END OF THE FUNCTION")

    def sample_action(self, action):
        lng = len(action)
        population = [i for i in range(lng)]
        
        action = random.choices(population, action)
        return action[0]

    def eval_genomes_unity_split_actions(self, genomes, config):
        #print("got to eval unity")
        self.POP_SIZE = len(genomes)
        iterations_num = int(self.POP_SIZE / self.env_batch_size)

        self.networks = list()
        self.genomes_list = list()
        reset_hist = False
        
        for g in genomes:
            genome = g[1]
            net = neat.nn.FeedForwardNetwork.create(genome, config)
            self.networks.append(net) 
            genome.fitness = 0
            self.genomes_list.append(genome)
      
        
        #print("after connect")
        confidence_training = 1
        cnt_win = 0
        for p in range (confidence_training):
            # running the same generation more times to account for the stochasticity
            
            for i in range( iterations_num ):
                # training a batch of networks of 50
                iter = 0
                finished_envs = 0
                finished_arr = list()
                for j in range(self.env_batch_size):
                    finished_arr.append(0)
                batch_ended = 0

                while True :
                    # training until all envs int the batch is finished
                    time1 = time.time()
                    iter += 1

                    message = self.receive_message(self.communication_socket)
                    finished = message.count('*')
                    message = message.split('|')

                    '''
                    '', ' 0 php 1.000 ehp 1.000 mn 17500 xp 999999 bp 0.500 ab 1 ptrps 0 0 0 0  etrps 0 0 0 0  slots 1 age 1 eage 1 turrets 0 0 0 0 0 0 0 0 ', ' 0 php 1.000 ehp 1.000 mn 17500 xp 999999 bp 0.500 ab 1 ptrps 0 0 0 0  etrps 0 0 0 
    0  slots 1 age 1 eage 1 turrets 0 0 0 0 0 0 0 0 '
                    the structure of a message
                    '''
                    message = message[1:]
                    actions = ""

                    for j in range(self.env_batch_size):
                        # processing the network i* self.env_batch_size + j and j environment
                        # processing inputs
                        mess = message[j] 
                        inp = False
                        add_fitness = False
                        if mess.count('*') == 0:
                            inp = True
                            add_fitness = True
                       
                        
                        if finished < 45:
                            inp = False
                        inp = False
                        if inp:
                            print(f"ENVIRONMENT IS {i * 50 + j}")
                            pass
                            
                        
                        mess = mess.split(' ')
                       
                        status = int(mess[-1])
                        
                        #print(mess)
                        '''
                        ['', '0', 'php', '1.000', 'ehp', '1.000', 'mn', '17500', 'xp', '999999', 'bp', '0.500', 'ab', '1', 'ptrps', '0', '0', '0', '0', '', 'etrps', '0', '0', '0', '0', '', 'slots', '1', 'age', '1', 'eage', '1', 'turrets', '0', '0', '0', '0', '0', '0', '0', '0', '']
                        '''
                        player_agen = int(mess[29])
                        enemy_agen = int(mess[31])

                        in_train = int(mess[1])
                        player_health = float(mess[3])
                        enemy_health = float(mess[5])

                        

                        money = int(mess[7])

                        tier3_cost = GLOBAL_VALUES["troops"][player_agen]["tier3"]
                
                        money_val = money
                        money = money / tier3_cost

                        xp = int(mess[9])
                        original_xp = xp
                        divider =  GLOBAL_VALUES["experience"][player_agen-1]
                        if divider == None:
                            xp = xp / 200000
                        else:
                            xp = xp / divider
                        battle_place = float(mess[11])
                        ability = int(mess[13])
                        player_troops_total = [int(mess[15]), int(mess[16]), int(mess[17]), int(mess[18])]
                        enemy_troops_total = [int(mess[21]), int(mess[22]), int(mess[23]), int(mess[24])]
                        slots_available = int(mess[27])
                        turrets = [
                            [int(mess[33]),int(mess[34])],
                            [int(mess[35]),int(mess[36])],
                            [int(mess[37]),int(mess[38])],
                            [int(mess[39]),int(mess[40])],
                        ]
                        #processing data

                        new_turrets = list()
                        for turret in turrets:
                            tier,turr_age = turret[0], turret[1]
                            
                            if turr_age != 0:
                                sig_tier = np.tanh(tier)
                                new_turrets.append(sig_tier) # turret exists
                                if turr_age == player_agen:
                                    new_turrets.append(1)
                                else:
                                    new_turrets.append(-1)
                            else:
                                new_turrets.append(0)
                                new_turrets.append(0)

                        
                        in_train = np.array(in_train)/5
                        t4_troops = player_troops_total[3]

                        player_troops_total = np.array(player_troops_total)/5.0
                        enemy_troops_total = np.array(enemy_troops_total)/5.0

                        player_troops_total = np.sum(player_troops_total)
                        enemy_troops_total = np.sum(enemy_troops_total)

                        # in_train = np.tanh(in_train)
                        # player_troops_total = np.tanh(player_troops_total)
                        # enemy_troops_total = np.tanh(enemy_troops_total)
                        # slots_available = np.tanh(slots_available)

                        age = [0,0,0,0,0]
                        age[player_agen-1] = 1

                        enemy_age = [0,0,0,0,0]
                        enemy_age[enemy_agen-1] = 1
                        tot_tr = np.sum(player_troops_total)
                
                        
                        money = money + 1
                        money = np.log(min(money, 50))
                        xp = np.log(min(xp + 1, 20))


                        battle_place = battle_place * 5
                        t4_val = money_val / GLOBAL_VALUES["troops"][5]["tier4"]
                     
                        inputs = (in_train, player_health, enemy_health, money, xp, battle_place, ability, player_troops_total, enemy_troops_total, t4_troops, t4_val, slots_available, *age, *enemy_age, *new_turrets)
                   
                        network_num = i * self.env_batch_size + j
            
                        net = self.networks[network_num]

                        if not add_fitness:
                            if finished_arr[j] == 0 :
                                if status == 2:
                                    self.genomes_list[network_num].fitness += 10000
                                    print("AI WON THE GAME")
                                    cnt_win += 1
                                
                                finished_arr[j] = 1

                        action = net.activate(inputs)
                        action = np.array(action)

                        action1 = action[0:4] # troop actions
                        action2 = action[4:12] # turret actions
                        action3 = action[12:14] # buy slot or not
                        action4 = action[14:16] # ability or not
                        action5 = action[16:18] # upgrade age or not
                        action6 = action[18:20] # create super soldier or not
    
                        action1 = np.argmax(action1)
                        action2 = np.argmax(action2)
                        action3 = np.argmax(action3)
                        action4 = np.argmax(action4)
                        action5 = np.argmax(action5)
                        action6 = np.argmax(action6)

                        if add_fitness:
                            self.genomes_list[network_num].fitness += 0.2 # reward because the game hasn't ended
                            saved_money = money_val / GLOBAL_VALUES["troops"][enemy_agen]["tier3"]
                            self.genomes_list[network_num].fitness += 0.4 * np.tanh(saved_money/4.0) # reward to incentivize stacking money
                            self.genomes_list[network_num].fitness += 0.4 * np.tanh(t4_val/4.0) # reward to incentivize stacking money
                       
                            if action1 == 0:
                                self.genomes_list[network_num].fitness += 0.6

                            if t4_troops > 0:
                                self.genomes_list[network_num].fitness += 0.02 * (10**min(t4_troops,3.5))
          
                        # action1 = self.sample_action(action1)
                        # action2 = self.sample_action(action2)
                        # action3 = self.sample_action(action3)
                        # action4 = self.sample_action(action4)
                        # action5 = self.sample_action(action5)

                        if original_xp > 5500000 or batch_ended :
                            # the ai hit a infinite loop so it will lose on purpose
                            # just waiting 
                            action5 = 0
                            action4 = 0
                            action3 = 0
                            action2 = random.choices([3,4,5,6],[1,1,1,1])[0]
                            action1 = 0
                            action6 = 0
                            #batch_ended = True
                            #reset_hist = True

                        

                   
                        '''
                        action = np.argmax(action)
                        if np.isnan(val):
                            action = 13
                        '''
                     
                        actions += f"{action1}{action2}{action3}{action4}{action5}{action6} "

                    #print(actions)
                    self.communication_socket.send(f"{actions}".encode("utf-8"))
                    #print(finished)
                    if finished == self.env_batch_size:
                        break

        for i,g in enumerate(genomes):
            genome = g[1]
            #print(f"fitness for {i} is {genome.fitness}")
            genome.fitness /= confidence_training

        self.save_best(genomes)
        self.generation += 1
        
        if cnt_win >= 3:
            print(f"A NUMBER OF {cnt_win} AI WON")
            reset_hist = True

        return reset_hist


    def eval_genomes_unity(self, genomes, config):
        #print("got to eval unity")
        self.POP_SIZE = len(genomes)
        iterations_num = int(self.POP_SIZE / self.env_batch_size)

        self.networks = list()
        self.genomes_list = list()
        reset_hist = False
        
        for g in genomes:
            genome = g[1]
            net = neat.nn.FeedForwardNetwork.create(genome, config)
            self.networks.append(net) 
            genome.fitness = 0
            self.genomes_list.append(genome)
      
        
        #print("after connect")
        confidence_training = 1
        for p in range (confidence_training):
            # running the same generation more times to account for the stochasticity
            for i in range( iterations_num ):
                # training a batch of networks of 50
                iter = 0
                finished_envs = 0
                finished_arr = list()
                for j in range(self.env_batch_size):
                    finished_arr.append(0)

                while True :
                    # training until all envs int the batch is finished
                    time1 = time.time()
                    iter += 1

                    message = self.receive_message(self.communication_socket)
                    finished = message.count('*')
                    message = message.split('|')

                    '''
                    '', ' 0 php 1.000 ehp 1.000 mn 17500 xp 999999 bp 0.500 ab 1 ptrps 0 0 0 0  etrps 0 0 0 0  slots 1 age 1 eage 1 turrets 0 0 0 0 0 0 0 0 ', ' 0 php 1.000 ehp 1.000 mn 17500 xp 999999 bp 0.500 ab 1 ptrps 0 0 0 0  etrps 0 0 0 
    0  slots 1 age 1 eage 1 turrets 0 0 0 0 0 0 0 0 '
                    the structure of a message
                    '''
                    message = message[1:]
                    actions = ""

                    for j in range(self.env_batch_size):
                        # processing the network i* self.env_batch_size + j and j environment
                        # processing inputs
                        mess = message[j] 
                        inp = False
                        add_fitness = False
                        if mess.count('*') == 0:
                            inp = True
                            add_fitness = True
                       
                        
                        if finished < 47:
                            inp = False
                        inp = False
                        if inp:
                            print(f"ENVIRONMENT IS {i * 50 + j}")
                            pass
                            
                        
                        mess = mess.split(' ')
                        status = mess[-1]
                        #print(mess)
                        '''
                        ['', '0', 'php', '1.000', 'ehp', '1.000', 'mn', '17500', 'xp', '999999', 'bp', '0.500', 'ab', '1', 'ptrps', '0', '0', '0', '0', '', 'etrps', '0', '0', '0', '0', '', 'slots', '1', 'age', '1', 'eage', '1', 'turrets', '0', '0', '0', '0', '0', '0', '0', '0', '']
                        '''
                        player_agen = int(mess[29])
                        enemy_agen = int(mess[31])

                        in_train = int(mess[1])
                        player_health = float(mess[3])
                        enemy_health = float(mess[5])

                        

                        money = int(mess[7])
                        tier3_cost = GLOBAL_VALUES["troops"][player_agen]["tier3"]
                        incentive = money / GLOBAL_VALUES["troops"][enemy_agen]["tier3"]
                        money = money / tier3_cost
                        xp = int(mess[9])
                        original_xp = xp
                        divider =  GLOBAL_VALUES["experience"][player_agen-1]
                        if divider == None:
                            xp = 0
                        else:
                            xp = xp / divider
                        battle_place = float(mess[11])
                        ability = int(mess[13])
                        player_troops_total = [int(mess[15]), int(mess[16]), int(mess[17]), int(mess[18])]
                        enemy_troops_total = [int(mess[21]), int(mess[22]), int(mess[23]), int(mess[24])]
                        slots_available = int(mess[27])
                        turrets = [
                            [int(mess[33]),int(mess[34])],
                            [int(mess[35]),int(mess[36])],
                            [int(mess[37]),int(mess[38])],
                            [int(mess[39]),int(mess[40])],
                        ]
                        #processing data

                        new_turrets = list()
                        for turret in turrets:
                            tier,turr_age = turret[0], turret[1]
                            
                            if turr_age != 0:
                                sig_tier = np.tanh(tier)
                                new_turrets.append(sig_tier) # turret exists
                                if turr_age == player_agen:
                                    new_turrets.append(1)
                                else:
                                    new_turrets.append(-1)
                            else:
                                new_turrets.append(0)
                                new_turrets.append(0)

                        in_train = np.tanh(in_train)

                        player_troops_total = np.array(player_troops_total)/3
                        enemy_troops_total = np.array(enemy_troops_total)/3

                        player_troops_total = np.tanh(player_troops_total)
                        enemy_troops_total = np.tanh(enemy_troops_total)
                        slots_available = np.tanh(slots_available)

                        age = [0,0,0,0,0]
                        age[player_agen-1] = 1

                        enemy_age = [0,0,0,0,0]
                        enemy_age[enemy_agen-1] = 1
                        tot_tr = np.sum(player_troops_total)

                        inputs = (in_train, player_health, enemy_health, money, xp, battle_place, ability, *player_troops_total, *enemy_troops_total, slots_available, *age, *enemy_age, *new_turrets)
                
                        network_num = i * self.env_batch_size + j
                        

                        if add_fitness:
                            self.genomes_list[network_num].fitness += 0.2 # reward because the game hasn't ended
                            self.genomes_list[network_num].fitness += 0.02 * np.tanh(incentive/5) # incetiving the ai to save money
                        
                        net = self.networks[network_num]

                        if not add_fitness:
                            if finished_arr[j] == 0 :
                                if status == 2:
                                    self.genomes_list[network_num].fitness += 10000
                                finished_arr[j] = 1

                        action = net.activate(inputs)
                        action = np.array(action)

                        if inp:
                            #print(f"before process {action}")
                            pass
                        action = stats.zscore(action) * 1.5
                        action = self.softmax(action)
                        if inp:
                            #print(f"after process {action}")
                            pass
                        population = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]
                        

                        
                        if original_xp > 5000000 :
                            # the ai hit a infinite loop so it will lose on purpose
                            # 11 10 9 8 13 heavily increasing probabilities for waiting and selling turrets
                            action[8] += 10
                            action[9] += 10
                            action[10] += 10
                            action[11] += 10
                            action[13] += 10
                            reset_hist = True

                        val = action[np.argmax(action)]
                        '''
                        action = np.argmax(action)
                        if np.isnan(val):
                            action = 13
                        '''
                        if np.isnan(val):
                            action = 13
                        else:
                            # action = np.argmax(action)
                            action = choices(population, action)
                            action = action[0]
                        
                        if inp:
                            
                            #print(action)
                            pass
                        
                        if add_fitness and action == 13:
                            self.genomes_list[network_num].fitness += 0.1

                        actions += f"{action} "

                    #print(actions)
                    #print(time2-time1)
                    self.communication_socket.send(f"{actions}".encode("utf-8"))
                    #print(finished)
                    if finished == self.env_batch_size:
                        break

        for i,g in enumerate(genomes):
            genome = g[1]
            #print(f"fitness for {i} is {genome.fitness}")
            genome.fitness /= confidence_training

        self.save_best(genomes)
        self.generation += 1
        reset_hist = False
        return reset_hist
    
        #print("GOT TO THE END OF THE FUNCTION")
                
            
            
    def save_genome_from_generation(self, population, number, config_name):
        from neat.six_util import iteritems
        genomes = list(iteritems(self.population))
        local_dir = os.path.dirname(__file__)
        config_path = os.path.join(local_dir, f'{config_name}')
        


    def main(self):
        
        local_dir = os.path.dirname(__file__)
        config_path = os.path.join(local_dir, 'config-feedforward.txt')

        self.start_envs()
        #self.run(config_path, self.eval_genomes)
        self.run_winner(config_path, "best")

        # self.random_actions()
    
    def main_unity(self):
        local_dir = os.path.dirname(__file__)
        config_path = os.path.join(local_dir, 'config-feedforward.txt')

        self.establish_connection()
        self.run(config_path, self.eval_genomes_unity)
        #self.run_winner_unity(config_path, "winner-generation 150")
    
    def main_unity_split(self):
        local_dir = os.path.dirname(__file__)
        config_path = os.path.join(local_dir, 'config-feedforward split3.txt')

        self.establish_connection()
        self.run(config_path, self.eval_genomes_unity_split_actions)
        #self.run_winner_unity_split(config_path, "wn11")
        

    def vis_winner(self):
        winner = "winner-generation 19"
        with open(f"{winner}", "rb") as f:
            genome = pickle.load(f)

        winner = genome
        print(winner[1].fitness)
        visualize.draw_net(config, winner[1], True)


    def run(self, config_file, eval_func):
        
        """
        runs the NEAT algorithm to train a neural network to play Age of war
        :param config_file: location of config file
        :return: None
        """
        config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                            neat.DefaultSpeciesSet, neat.DefaultStagnation,
                            config_file)

        # Create the population, which is the top-level object for a NEAT run.

        #p = neat.Population(config)

        p = neat.Checkpointer.restore_checkpoint("neat-checkpoint-80")
     
        p.add_reporter(neat.StdOutReporter(True))
        
 
        stats = neat.StatisticsReporter()
        p.add_reporter(stats)
        p.add_reporter(neat.Checkpointer(1))
    
        winner = p.run(eval_func, 1000)

        # with open('winner-feedforward', 'wb') as f:
        #     pickle.dump(winner, f)
        
        # with open('stats-feedforward', 'wb') as f:
        #     pickle.dump(stats, f)

        # print('\n Best genome:\n{!s}'.format(winner))
        # print(stats)
     