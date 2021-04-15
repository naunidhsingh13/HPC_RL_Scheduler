from CqSim.Cqsim_sim import Cqsim_sim
from gym import spaces
from gym import Env
import numpy as np


class CqsimEnv(Env):

    def __init__(self, config):
        Env.__init__(self)
        self.simulator = Cqsim_sim(config)
        self.simulator.start()
        self.window_size = config["window"]
        self.job_cols = config["job_cols"]
        self.action_space = spaces.Discrete(self.window_size)
        self.observation_space = spaces.Box(
            shape=(1,self.simulator.module['node'].get_tot() + self.window_size * self.job_cols,2),
            dtype=np.float32, low=0.0, high=1.0)


    def reset(self):
        self.simulator.reset()
        return self.next_observation()

    def render(self, mode='human'):
        pass

    def get_state(self):
        self.simulator.is_producer_paused()
        return self.simulator.state

    def step(self, action):
        if action:
            ind = self.simulator.state.index(action)
            self.simulator.state = self.simulator.state[:ind] + \
                                             self.simulator.state[ind + 1:] + \
                                             [self.simulator.state[ind]]
        self.simulator.pause_producer()
        return self.next_observation(), self.reward(), self.done()

    def observation_jobs(self):
        sim = self.simulator
        wait_list = sim.module['job'].wait_list().copy()

        if len(wait_list) > self.window_size:
            window = wait_list[0:self.window_size]
        else:
            window = wait_list

        job_info = []

        for i in range(len(window)):
            job = sim.module['job'].job_info(window[i])
            job_info.append({"index": window[i], "proc": job['reqProc'], "node": job['reqProc'],
                             "run": job['run'], "score": job['score']})

        if sim.backfill:
            job_info = sim.module['backfill'].backfill(job_info, {'time': sim.currentTime})

        job_info = [job for job in job_info if job['index'] != sim.reserve_job_id]

        job_input = []
        for i in range(len(job_info)):
            s = float(job_info[i]['submit'])
            t = float(job_info[i]['reqTime'])
            n = float(job_info[i]['reqProc'])
            w = int(sim.currentTime - s)
            a = int(job_info[i]['award'])
            info = [[n, t], [a, w]]
            job_input.append(info)

        return job_input

    def next_observation(self):
        jobs = self.observation_jobs()
        nodes = self.simulator.module['alg'].preprocessing_system_status(self.simulator.module['node'].get_nodeStruc(),
                                                                         self.simulator.currentTime)

        return self.simulator.module['alg'].make_feature_vector(jobs, nodes, self.job_cols, self.window_size)

    def reward(self, job_info, max_job_wait_time):
        sim = self.simulator

        if sim.reward_type == '2':
            selected_job_wait_time = sim.currentTime - job_info['submit']
            wait_times_ratio = 1
            if max_job_wait_time > 0:
                wait_times_ratio = selected_job_wait_time / max_job_wait_time
            return wait_times_ratio
        elif sim.reward_type == '5':
            tmp_reward = 0

            tot = sim.module['node'].get_tot()
            idle = sim.module['node'].get_idle()
            running = tot - idle
            selected_job_requested_nodes = job_info['reqProc']
            selected_job_wait_time = sim.currentTime - job_info['submit']

            selected_job_priority = selected_job_requested_nodes / tot
            w1, w2, w3 = 1 / 3, 1 / 3, 1 / 3

            if idle < selected_job_requested_nodes:
                tmp_reward += running / tot * w1
            else:
                tmp_reward += (selected_job_requested_nodes + running) / tot * w1

            # 6 hours 60%
            if max_job_wait_time >= 21600:
                tmp_reward += selected_job_wait_time / max_job_wait_time * w2
            else:
                tmp_reward += selected_job_wait_time / 21600 * w2

            tmp_reward = selected_job_priority * w3
            return tmp_reward
        elif sim.reward_type == '6':
            return job_info['reqProc']
        else:
            # uti
            tot = sim.module['node'].get_tot()
            idle = sim.module['node'].get_idle()
            uti = float(tot - idle) / tot
            return max(0.0, uti)
