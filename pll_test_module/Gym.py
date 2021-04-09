from Sim import Sim
import random

class Gym:

    def __init__(self):
        # Acts as the producer
        self.sim = Sim()
        self.sim.start()

    def get_actions(self):
        self.sim.is_producer_paused()
        return self.sim.wait_list

    def step(self, action):

        ind = self.sim.wait_list.index(action)
        self.sim.wait_list = self.sim.wait_list[:ind] + self.sim.wait_list[ind+1:] + [self.sim.wait_list[ind]]
        self.sim.pause_producer()
        return self.sim.wait_list, self.sim.is_simulation_complete


if __name__ == '__main__':

    gym = Gym()

    action = random.sample(gym.get_actions(), 1)[0]
    print("Actions selected by model : %d" % action)
    done = False

    while not done:
        actions, done = gym.step(action)
        action = random.sample(actions, 1)[0]
        print("Actions selected by model : ", action)
