import ray
import ray.rllib.agents.ppo as ppo

ray.init()
config = ppo.DEFAULT_CONFIG.copy()
agent = ppo.PPOAgent(config=config, env="CartPole-v0")