import neat
import time
import numpy as np
import os
import pickle
from random import choices
from scipy.stats import stats

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
    generation = 0
    master = None
    valid_actions_streak = list()
    generations_fitnesses = list()
    act = 0
    fitness_med = list()

    def __init__(self, envs) -> None:
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

            if interations % 50 == 0:
                self.master.save_all_data_packets()
            # print(self.number_of_envs)
            # print(f"finished_envs {finished_envs}")
            # print(f"inactive_envs {self.inactive_envs}")
            # print(f"next neural network {self.next_nn}")
            # print(f"atributed networks {self.networks_training}")

            for i in range(self.number_of_envs):
                if self.inactive_envs[i] == 1:
                    time.sleep(0.25)
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
                        self.genomes_list[self.networks_training[i]].fitness += 10000

                    #print(f"FITNESS: {self.genomes_list[self.networks_training[i]].fitness}")
                    env.restart_game()
                    self.networks_training[i] = self.next_nn
                    self.next_nn += 1
                    env.defocus()
                    continue

                self.genomes_list[self.networks_training[i]].fitness += 0.2 # reward because the game hasn't ended

                net = self.networks[self.networks_training[i]]

                #print(inputs)
                #print(len(inputs))
                action = net.activate(inputs)
                action = np.array(action)
                self.master.data[env.assigned_window].append(action)

                #print(f"actions before Zscore {action}")
                action = stats.zscore(action)
                #print(f"actions after Zscore {action}")
                action = self.softmax(action)

                #print(f"ACTIONS AFTER SOFTMAX {action}")
                population = [0,1,2,3,4,5,6,7,8,9,10,11,12,13]
                action = choices(population, action)
                #action = [12]
                self.act += 1
                
                Taken = env.take_action(*action)
                # print(Taken)
                # print("--------------------------")
                if Taken == True:
                    self.valid_actions_streak[i] += 1
                    if self.valid_actions_streak[i] > 4:
                        self.valid_actions_streak[i] = 4
                    self.genomes_list[self.networks_training[i]].fitness += 0.05 * self.valid_actions_streak[i]
                    # bonus for taking a valid action
                else:
                    self.valid_actions_streak[i] = 0


                env.defocus()

        for g in genomes:
            genome = g[1]
            fitness += genome.fitness
        
            self.fitness_med.append((self.generation, fitness))
        

       
        self.generation += 1
        try:
            with open('fitness_scores.txt', 'w') as f:
                f.write(f"{self.fitness_med}")
            f.close()
        except:
            pass

        time2 = time.time()
        print(f"time taken per gen {time2-time1}")


    def main(self):
        

        local_dir = os.path.dirname(__file__)
        config_path = os.path.join(local_dir, 'config-feedforward.txt')

        self.start_envs()
        self.run(config_path)

        # self.random_actions()


    def run(self, config_file):
        
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
       
        # Add a stdout reporter to show progress in the terminal.
        p.add_reporter(neat.StdOutReporter(True))
 
        stats = neat.StatisticsReporter()
        p.add_reporter(stats)
        p.add_reporter(neat.Checkpointer(1))

        time1 = time.time()
        #p = neat.Checkpointer().restore_checkpoint("neat-checkpoint-1")
        winner = p.run(self.eval_genomes, 50)
        time2 = time.time()

        with open('winner-feedforward', 'wb') as f:
            pickle.dump(winner, f)
        
        with open('stats-feedforward', 'wb') as f:
            pickle.dump(stats, f)

        print('\n Best genome:\n{!s}'.format(winner))
        print(stats)
        print(f"everthing took about {time2-time1}")