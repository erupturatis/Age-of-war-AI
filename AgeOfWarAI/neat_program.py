import neat
import time
import numpy as np
class NeatClass(object):
    envs = None
    number_of_envs = None

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
                inputs = env.get_inputs()

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

    def neat_algorithm(self):
        self.random_actions()
