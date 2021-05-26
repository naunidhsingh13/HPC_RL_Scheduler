from CqGym.Gym import CqsimEnv
from Models.PG import PG
import tensorflow.compat.v1 as tf
import numpy as np

tf.disable_v2_behavior()


def get_action_from_output_vector(output_vector, wait_queue_size, is_training):
    def softmax(z):
        return np.exp(z) / np.sum(np.exp(z))
    action_p = softmax(output_vector.flatten()[:wait_queue_size])
    if is_training == 1:
        wait_queue_ind = np.random.choice(len(action_p), p=action_p)
    else:
        wait_queue_ind = np.argmax(action_p)
    return wait_queue_ind


def model_training(env, weights_file=None, is_training=False, output_file=None):

    sess = tf.Session()
    tf.keras.backend.set_session(sess)
    pg = PG(env, sess)

    if weights_file is not None:
        pg.load(weights_file)

    obs = env.get_state().feature_vector
    done = False

    while not done:

        env.render()
        output_vector = pg.act(obs)

        action = get_action_from_output_vector(output_vector, obs.wait_que_size, is_training)
        new_obs, done, reward = env.step(0)
        pg.remember(obs, output_vector, reward, new_obs)
        pg.train()
        obs = new_obs

    if output_file is not None:
        pg.save(output_file)


def cqsim_execute(module_list, module_debug, job_cols=0, window_size=0,
                  is_training=False, weights_file=None, output_file=None):
    """
    Execute the CqSim Simulator using OpenAi based Gym Environment with Scheduling implemented using DeepRL Engine.

    :param module_list: CQSim Module :- List of attributes for loading CqSim Simulator
    :param module_debug: Debug Module :- Module to manage debugging CqSim run.
    :param job_cols: [int] :- No. of attributes to define a job.
    :param window_size: [int] :- Size of the input window for the DeepLearning (RL) Model.
    :param is_training: [boolean] :- If the weights trained need to be saved.
    :param weights_file: [str] :- Existing Weights file path.
    :param output_file: [str] :- File path if the where the new weights will be saved.
    :return: None
    """
    cqsim_gym = CqsimEnv(module_list, module_debug, job_cols, window_size)

    model_training(cqsim_gym, weights_file, is_training=is_training, output_file=output_file)
