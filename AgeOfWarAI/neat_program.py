import neat
import time
import threading

class NeatClass(object):
    envs = None
    number_of_envs = None

    def __init__(self, envs) -> None:
        self.number_of_envs = len(envs)
        self.envs = envs

    def neat_algorithm(self):
        time1 = time.time()
        
        for i in range(self.number_of_envs):
            
            env = self.envs[i]
            screenshot = env.screenshot()
            
            #print(f"{i} and input {inputs}")
        #takes 0.25 per screenshot
        #takes 0.15 er windows focus and defocus
        time2 = time.time()
        print(f'total time for screenshots {time2 - time1} to {i}')

        for i in range(2):
            for i in range(self.number_of_envs):
                print(f"startedt {i} environment")
                env = self.envs[i]
                inputs = env.get_inputs()


            
        print("finished neat")
