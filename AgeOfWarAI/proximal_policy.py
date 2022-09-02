
import time
import numpy as np
import os
import math
#import visualize
import socket
from AgeOfWarAPI import take_action

class ProximalPolicy(object):
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
        print("here")
        HOST = "192.168.100.5"
        PORT = 9090

        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((HOST, PORT))

        server.listen(1)
        self.server = server
        communication_socket, address = self.server.accept()
        self.communication_socket = communication_socket


    def run_winner(self):
        
        self.start_envs()
        print("started envs and connected to unity")

        evaluating = True
        while evaluating:
            # getting inputs


            env = self.envs[0]
            env.focus()
            env.printing = True
 
            time1 = time.time()
            inputs, ended = env.get_inputs()
            print(f"TIME INPUTS {time.time() - time1}")
            # sending inputs
            print(inputs)
            print("sending inputs")
            time1 = time.time()
            self.communication_socket.send(f"{inputs}".encode("utf-8"))
            # getting outputs
            action = self.receive_message(self.communication_socket)
            print(action)
            # playing output

            #env.take_action(int(action))
            if int(action) > 14:
                take_action(int(action))
            else:
                env.take_action(int(action))
 
            pass

        

    
    def main(self):
        local_dir = os.path.dirname(__file__)
        self.establish_connection()
        self.run_winner()
        #self.run_winner_unity_split(config_path, "wn11")
        



  
