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


def model_training(env, weights_file_name=None, is_training=False, output_file_name=None,
                   window_size=50, learning_rate=0.1, gamma=0.99, batch_size=10):

    sess = tf.Session()
    tf.keras.backend.set_session(sess)
    pg = PG(env, sess, window_size, learning_rate, gamma, batch_size)

    if weights_file_name:
        pg.load_using_model_name(weights_file_name)

    obs = env.get_state()
    done = False

    while not done:

        # env.render()
        output_vector = pg.act(obs.feature_vector)

        action = get_action_from_output_vector(output_vector, obs.wait_que_size, is_training)
        new_obs, done, reward = env.step(action)
        pg.remember(obs.feature_vector, output_vector, reward, new_obs.feature_vector)
        if is_training:
            pg.train()
        obs = new_obs

    if is_training and output_file_name:
        pg.save_using_model_name(output_file_name)


def model_engine(module_list, module_debug, job_cols=0, window_size=0,
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
    cqsim_gym = CqsimEnv(module_list, module_debug,
                         job_cols, window_size)
    model_training(cqsim_gym, window_size=window_size, is_training=is_training,
                   weights_file_name=weights_file, output_file_name=output_file)
