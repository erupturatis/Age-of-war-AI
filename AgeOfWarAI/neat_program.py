import neat


class NeatClass(object):
    envs = None
    number_of_envs = None

    def __init__(self, envs) -> None:
        self.number_of_envs = len(envs)
        self.envs = envs

    def neat_algorithm(self):
        for i in range(self.number_of_envs):
            env = self.envs[i]
            inputs = env.get_inputs()
            print(inputs)
            
        print("finished neat")
