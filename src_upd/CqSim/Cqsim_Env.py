import gym
from CqSim.Cqsim_sim import Cqsim_sim


class Cqsim_Env(gym.Env, Cqsim_sim):

    def __init__(self, module, debug=None):

        Cqsim_sim.__init__(self, module, debug)
        self.done = self.cqsim_sim()

        # self.action_space = <gym.Space>
        # self.observation_space = <gym.Space>

    def render(self, mode='human'):
        pass

    def reset(self):
        self.reset_sim(self.module, self.debug)
        return []  # <obs>

    def get_action(self):

        return self.module['job'].wait_list()

    def step(self, action):

        # call Start Scan to initiate.

        if not self.done:

            # take decsion
            # self.event_job(self.current_event['para'])
            self.done = self.start_scan(action)

            if self.done:
                self.done = self.scan_event()
            # self.score_calculate() # Will be activated when working on actual AC model.

        return [], 0, self.done, {}


