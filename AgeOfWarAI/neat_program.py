
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
    generation = 57
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
    

    def save_best(self, genomes, num = -1):
        fitness = 0
        mx = 0
        cnt = 0
        if num == -1:
            for i,g in enumerate(genomes):
                genome = g[1]
                fitness += genome.fitness
                if genome.fitness > mx:
                    mx = genome.fitness
                    cnt = i
            num = cnt

        self.fitness_med = (self.generation, fitness / len(genomes), mx, num)
            # print(self.population.best_genome)
            # print(self.population.best_genome[1])
            
        try:
            with open(f'winner-generation {self.generation}', 'wb') as f:
                pickle.dump(genomes[num], f)
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
    
    def process_data_neat_split(self, inputs):
        new_inputs = list()

        in_train, player_health, enemy_health, money, xp, battle_place, ability, player_troops_total, enemy_troops_total, slots_available, total_slots, age_index, enemy_age_index, turrets = inputs

        tier3_cost = GLOBAL_VALUES["troops"][age_index]["tier3"]

        t4_val = money / 150000
        money = money / tier3_cost

        divider =  GLOBAL_VALUES["experience"][age_index-1]
        xp = xp / divider

        in_train = np.array(in_train)/5
  
        t4_troops = player_troops_total[3]

 
        player_troops_total = np.array(player_troops_total)/5.0
        enemy_troops_total = np.array(enemy_troops_total)/5.0
          
        battle_place = battle_place * 5

        money = money + 1
        money = np.log(min(money, 50))
        xp = np.log(min(xp + 1, 20))
        new_turrets = list()

        for turret in turrets:
            tier,turr_age = turret[0], turret[1]
            
            if turr_age != 0:
                tier -= 1
                sig_tier = np.tanh(tier)
                new_turrets.append(sig_tier) # turret exists

                if turr_age == age_index:
                    new_turrets.append(turr_age)
                else:
                    new_turrets.append(-1)
            else:
                new_turrets.append(0)
                new_turrets.append(0)

        age = [0,0,0,0,0]
        age[age_index-1] = 1
        enemy_age = [0,0,0,0,0]
        enemy_age[enemy_age_index-1] = 1
        new_inputs = [in_train, player_health, enemy_health, money, xp, battle_place, ability, *player_troops_total, *enemy_troops_total, t4_troops, t4_val, slots_available, *age, *enemy_age, *new_turrets]        
        return new_inputs

    def preprocess_turrets(self, turrets):
        new_turrets = list()
        for turret in turrets:

            tier,turr_age = turret[0], turret[1]

            if turr_age != 0:
                tier += 1

            new_turrets.append([tier, turr_age])

        return new_turrets

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
            inputs, ended = env.get_inputs()
            print(inputs)
            inputs = self.process_data_neat_split(inputs)
            inputs[5] -= 1
            inputs[5] = max(inputs[5],0)
            print(inputs)
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
           

            action1 = action[0:7] # troop actions
            action2 = action[7:15] # turret actions
            action3 = action[15:17] # buy slot or not
            action4 = action[17:19] # ability or not
            action5 = action[19:21] # upgrade age or not
            action6 = action[21:24] # create super soldier or not
            print(action6)
          
            action1 = np.argmax(action1)
            action2 = np.argmax(action2)
            action3 = np.argmax(action3)
            action4 = np.argmax(action4)
            action5 = np.argmax(action5)
            action6 = np.argmax(action6)
            print([action1,action2,action3,action4,action5,action6])
            self.act += 1
            Taken = env.actions_manager(action1, action2, action3, action4, action5, action6)
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
                        money_val = money
                        t4_val = money_val / 150000
                        xp = int(mess[9])
                        original_xp = xp
                 
                        battle_place = float(mess[11])
                        ability = int(mess[13])
                        player_troops_total = [int(mess[15]), int(mess[16]), int(mess[17]), int(mess[18])]
                        t4_troops = player_troops_total[3]
                        enemy_troops_total = [int(mess[21]), int(mess[22]), int(mess[23]), int(mess[24])]
                        slots_available = int(mess[27])
                        turrets = [
                            [int(mess[33]),int(mess[34])],
                            [int(mess[35]),int(mess[36])],
                            [int(mess[37]),int(mess[38])],
                            [int(mess[39]),int(mess[40])],
                        ]
                        total_slots = int(mess[41])
                        #processing data
                        # note that turret tiers for original game are 1 2 3 while unity turrets are 0 1 2 so we need to preprocess them
                        turrets = self.preprocess_turrets(turrets)
                        inputs = (in_train, player_health, enemy_health, money, xp, battle_place, ability, player_troops_total, enemy_troops_total, slots_available, total_slots, player_agen, enemy_agen, turrets)
                        inputs = self.process_data_neat_split(inputs)
                      
                        network_num = i * self.env_batch_size + j
                        #network_num = 0
                        net = self.networks[network_num]
                        

                        if not add_fitness:
                            if finished_arr[j] == 0 :
                                if status == 2:
                                    self.genomes_list[network_num].fitness += 20000
                                    print(f"AI WON THE GAME {network_num}")
                                    cnt_win += 1
                                
                                finished_arr[j] = 1

                        action = net.activate(inputs)
                        action = np.array(action)

                        action1 = action[0:7] # troop actions
                        action2 = action[7:15] # turret actions
                        action3 = action[15:17] # buy slot or not
                        action4 = action[17:19] # ability or not
                        action5 = action[19:21] # upgrade age or not
                        action6 = action[21:24] # create super soldier or not
       
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

                        if original_xp > 7000000 or batch_ended :
                            # the ai hit a infinite loop so it will lose on purpose
                            # just waiting 
                            action5 = 0
                            action4 = 0
                            action3 = 0
                            action2 = random.choices([3,4,5,6],[1,1,1,1])[0]
                            action1 = 0
                            action6 = 0
                            batch_ended = True
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

        
        self.generation += 1
        
        if cnt_win >= 3:
            print(f"A NUMBER OF {cnt_win} AI WON")
            reset_hist = True

        return reset_hist        
            
    def save_genome_from_generation(self, population, number, config_name):
        from neat.six_util import iteritems
        genomes = list(iteritems(self.population))
        local_dir = os.path.dirname(__file__)
        config_path = os.path.join(local_dir, f'{config_name}')
        
    def main(self):
        
        local_dir = os.path.dirname(__file__)
        config_path = os.path.join(local_dir, 'config.txt')

        self.start_envs()
        #self.run(config_path, self.eval_genomes)
        self.run_winner(config_path, "winner-generation 57")

        # self.random_actions()
    
    def main_unity_split(self):
        local_dir = os.path.dirname(__file__)
        config_path = os.path.join(local_dir, 'config.txt')

        self.establish_connection()
        self.run(config_path, self.eval_genomes_unity_split_actions)
        

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

        p = neat.Population(config)

        p = neat.Checkpointer.restore_checkpoint("neat-checkpoint-56")
     
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
     