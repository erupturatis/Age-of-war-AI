import neat
import time
import numpy as np
import os
import pickle


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

    def __init__(self, envs) -> None:
        self.number_of_envs = len(envs)
        self.envs = envs

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

        for i in range(self.number_of_envs):
            env = self.envs[i]
            env.focus()
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

        interations = 0
        while evaluating:

            interations += 1
            if interations % 10 == 0:
                self.master.save_all_data_packets()
            print(self.number_of_envs)
            print(f"finished_envs {finished_envs}")
            print(f"inactive_envs {self.inactive_envs}")
            print(f"next neural network {self.next_nn}")
            for i in range(self.number_of_envs):
                if self.inactive_envs[i] == 1:
                    continue
                env = self.envs[i]
                # screenshot = env.screenshot()
                env.focus()
                inputs, ended = env.get_inputs()
                # print(inputs, ended)
                if ended:
                    if self.next_nn == self.POP_SIZE:
                        finished_envs += 1
                        self.inactive_envs[i] = 1
                        if finished_envs == self.number_of_envs:
                            evaluating = False
                        continue

                    env.restart_game()
                    self.networks_training[i] = self.next_nn
                    self.next_nn += 1
                    continue

                self.genomes_list[self.networks_training[i]].fitness += 0.1 # reward because the game hasn't ended

                net = self.networks[self.networks_training[i]]
                #print(inputs)
                #print(len(inputs))
                action = net.activate(inputs)
                #print(action)
                action = np.argmax(action)
                Taken = env.take_action(action)

                if Taken == True:
                    self.genomes_list[self.networks_training[i]].fitness += 1

                env.defocus()
              
          
       
        self.generation += 1


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
        p.add_reporter(neat.Checkpointer(2,1800))

        winner = p.run(self.eval_genomes, 10)
        with open('winner-feedforward', 'wb') as f:
            pickle.dump(winner, f)

        print('\n Best genome:\n{!s}'.format(winner))
        print(stats)