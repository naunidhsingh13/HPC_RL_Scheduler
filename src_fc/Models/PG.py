import numpy as np
import random
from collections import deque
import tensorflow.compat.v1 as tf
import keras.backend as K
tf.disable_v2_behavior()


class PG:
    def __init__(self, env, sess, learning_rate=1e-1, gamma=0.99, batch_size=10):
        self.env = env
        self.sess = sess

        self.batch_size = batch_size
        self.lr = learning_rate
        self.gamma = gamma
        self.memory = deque(maxlen=20)

        self.policy, self.predict = self.build_policy()

    def build_policy(self):
        obs_shape = self.env.observation_space.shape
        input = tf.keras.layers.Input(shape=(obs_shape[1], obs_shape[2]))
        advantages = tf.keras.layers.Input(shape=[1])
        input_reshape = tf.reshape(input, [-1, obs_shape[2], 1])
        conv1d = tf.keras.layers.Conv1D(1, obs_shape[2], input_shape=(obs_shape[2], 1))(input_reshape)
        conv1d_reshape = tf.reshape(conv1d, [-1, obs_shape[1]])
        hidden_layer1 = tf.keras.layers.Dense(4000, 'relu', input_shape=(obs_shape[1],), use_bias=False)(conv1d_reshape)
        hidden_layer2 = tf.keras.layers.Dense(1000, 'relu', input_shape=(2000,), use_bias=False)(hidden_layer1)
        output = tf.keras.layers.Dense(50, activation='sigmoid')(hidden_layer2)

        def custom_loss(y_true, y_pred):
            out = K.clip(y_pred, 1e-8, 1-1e-8)
            log_like = y_true*K.log(out)

            return K.sum(-log_like*advantages)

        policy = tf.keras.Model(inputs=[input, advantages], outputs=output)
        adam = tf.keras.optimizers.Adam(lr=self.lr)
        policy.compile(loss=custom_loss, optimizer=adam)
        predict = tf.keras.Model(inputs=[input], outputs=[output])
        return policy, predict

    def act(self, obs):
        return self.predict.predict(obs)

    def train(self):
        if len(self.memory) < self.batch_size:
            return

        states = np.zeros((self.batch_size, *self.env.observation_space.shape))
        actions = np.zeros([self.batch_size, 50])
        G = np.zeros(self.batch_size)

        for i in range(self.batch_size):
            reward_sum = 0
            discount = 1
            for j in range(i, self.batch_size):
                _, _, reward, _ = self.memory[j]
                reward_sum += reward * discount
                discount *= self.gamma
            G[i] = reward_sum

            states[i, :], actions[i, :], _, _ = self.memory[i]

        mean = np.mean(G)
        std = np.std(G) if np.std(G) > 0 else 1
        G = (G - mean) / std

        self.policy.train_on_batch([states, G], actions)
        self.memory = deque(maxlen=20)

    def remember(self, obs, action, reward, new_obs):
        self.memory.append([obs, action, reward, new_obs])

    def save(self, fp):
        self.predict.save(fp+'.h5')

    def load(self, fp):
        self.predict.load_weights(fp)
