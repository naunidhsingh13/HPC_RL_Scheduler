import ray
from ray import tune
from ray.tune import grid_search
from ray.rllib.models import ModelCatalog

from CqSim.model import Net
from CqSim.Gym import CqsimEnv

import pickle

def train(modules, window, job_cols):
    ray.init()

    ModelCatalog.register_custom_model(
        "modelv0", Net)

    config = {
        "env": CqsimEnv,
        "env_config": {
            "module": modules,
            "window": window,
            "job_cols": job_cols,
        },
        "num_gpus": 1,
        "model": {
            "custom_model": "modelv0",
            "vf_share_layers": True,
        },
        "lr": grid_search([1e-2, 1e-4, 1e-6]),
        "num_workers": 1,
        "framework": "tf",
    }

    results = tune.run("PG", config=config, stop={"training_iteration": 10})
