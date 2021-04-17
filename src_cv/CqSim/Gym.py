from CqSim.Cqsim_sim import Cqsim_sim
from gym import Env


class CqsimEnv(Env):

    def __init__(self, module, debug=None):
        Env.__init__(self)
        self.simulator = Cqsim_sim(module, debug=debug)
        self.simulator.start()

    def reset(self):
        pass

    def render(self, mode='human'):
        pass

    def get_state(self):
        self.simulator.is_producer_paused()
        return self.simulator.simulator_state

    def step(self, action):
        if action:
            ind = self.simulator.simulator_state.index(action)
            self.simulator.simulator_state = self.simulator.simulator_state[:ind] + \
                                             self.simulator.simulator_state[ind + 1:] + \
                                             [self.simulator.simulator_state[ind]]
        self.simulator.pause_producer()
        return self.simulator.simulator_state, self.simulator.is_simulation_complete
