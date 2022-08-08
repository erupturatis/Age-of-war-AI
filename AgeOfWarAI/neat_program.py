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
from age_of_war_numerical import Game
import random



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
    generation = 24
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

    

    def random_actions(self):
        for i in range(100):
            time1 = time.time()
            for i in range(self.number_of_envs):
                
                env = self.envs[i]
                # screenshot = env.screenshot()
                env.focus()
                inputs, ended = env.get_inputs()
                # print(inputs, ended)
                if ended:
                    env.restart_game()
                    self.networks_training[i] = self.next_nn
                    self.next_nn += 1
                    continue

                action = [] # pseudocode
                action = np.random.rand(14)
          
                action[2] += 5
                action = np.argmax(action)
                Taken = env.take_action(action)
                print(Taken)
                env.defocus()
                print("defocused")
                print("\n")
            # print(f"time taken for 1action {time.time()-time1}")
            time.sleep(0.5)
        print("finished actions")

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
        mx = 0
        cnt = 0
        for i,g in enumerate(genomes):
            genome = g[1]
            fitness += genome.fitness
            if genome.fitness > mx:
                mx = genome.fitness
                cnt = i
        
        self.fitness_med = (self.generation, fitness / len(genomes), mx)
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

        self.generation += 1

    def eval_genomes_numerical(self, genomes, config):
        self.POP_SIZE = len(genomes)

        evaluating = True
        fitness = 0

        time1 = time.time()

        for g in genomes:

            genome = g[1]
            net = neat.nn.FeedForwardNetwork.create(genome, config) 
            genome.fitness = 0
            game = Game()

            game.step()
            inputs = game.get_inputs()

            action = net.activate(inputs)
            action = np.array(action)
            action = stats.zscore(action)
            action = self.softmax(action)
            population = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]

            action = choices(population, action)
            Taken = game.take_action(*action)
            game.debug()
        
        

        mx = 0
        cnt = 0
        for i,g in enumerate(genomes):
            genome = g[1]
            fitness += genome.fitness
            if genome.fitness > mx:
                mx = genome.fitness
                cnt = i
        
        self.fitness_med = (self.generation, fitness / len(genomes), mx)
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
        
            interations += 1

            # if interations % 10 == 0:
            #     self.master.save_all_data_packets()

            env = self.envs[0]
            env.focus()
            env.printing = True
            inputs, ended = env.get_inputs()
      
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
            
            Taken = env.take_action(*action)

            if Taken == True:
                valid_actions_streak += 1
                if valid_actions_streak > 4:
                    valid_actions_streak = 4
                local_fitness += 0.05 * valid_actions_streak
                # bonus for taking a valid action
            else:
                valid_actions_streak = 0

        
            self.master.save_all_data_packets()

    def eval_genomes_unity(self, genomes, config):
        print("got to eval unity")
        import socket

        HOST = "192.168.100.11"
        PORT = 9090

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((HOST, PORT))

        server.listen(100)

        self.POP_SIZE = len(genomes)
        iterations_num = int(self.POP_SIZE / self.env_batch_size)

        communication_socket, address = server.accept()
        print("after connect")
        for i in range( iterations_num ):
            print(f"incremented i {i}")
            # training a batch of networks
            
            print(f"Connected to {address}")
            message = communication_socket.recv(4096).decode('utf-8')
            print(f"message from cliet is {message}")
            communication_socket.send("message from server to client with corresponding actions".encode("utf-8"))
            
            # processing data and taking actions
            # returning actions




    def main(self):
        
        local_dir = os.path.dirname(__file__)
        config_path = os.path.join(local_dir, 'config-feedforward.txt')

        self.start_envs()
        self.run(config_path, self.eval_genomes)
        #self.run_winner(config_path, "winner-generation 6")

        # self.random_actions()
    
    def main_unity(self):
        local_dir = os.path.dirname(__file__)
        config_path = os.path.join(local_dir, 'config-feedforward.txt')

        self.run(config_path, self.eval_genomes_unity)

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

        p = neat.Population(config)

        #p = neat.Checkpointer.restore_checkpoint("neat-checkpoint-17")
        p.add_reporter(neat.StdOutReporter(True))
 
        stats = neat.StatisticsReporter()
        p.add_reporter(stats)
        p.add_reporter(neat.Checkpointer(1))

        winner = p.run(eval_func, 50)

        # with open('winner-feedforward', 'wb') as f:
        #     pickle.dump(winner, f)
        
        # with open('stats-feedforward', 'wb') as f:
        #     pickle.dump(stats, f)

        # print('\n Best genome:\n{!s}'.format(winner))
        # print(stats)
     
