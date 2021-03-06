# import gym
#
# env = gym.make('CartPole-v0')
# for i_episode in range(20):
#     observation = env.reset()
#
#     for t in range(100):
#         env.render()
#         print(observation)
#         action = env.action_space.sample()
#         observation, reward, done, info = env.step(action)
#         if done:
#             print("Episode finished after {} timesteps".format(t + 1))
#             break

# import tensorflow as tf
# import numpy as np
# from collections import deque
# import random
# import gym
#
# EPISODE = 10000
#
#
# class DeepQNetwork:
#     learning_rate = 0.001
#     gamma = 0.9
#
#     action_list = None
#
#     # 执行步数
#     step_index = 0
#
#     # epsilon的范围
#     initial_epsilon = 0.5
#     final_epsilon = 0.01
#
#     explore = 10000
#
#     # 经验回放存储
#
#     memory_size = 10000
#     BATCH = 32
#
#     # 神经网络
#     state_input = None
#     Q_val = None
#     y_input = None
#     optimizer = None
#     cost = 0
#     session = tf.Session()
#     cost_history = []
#
#     def __init__(self, env):
#         self.replay_memory_store = deque()
#         self.state_dim = env.observation_space.shape[0]
#         self.action_dim = env.action_space.n
#         self.action_list = np.identity(self.action_dim)
#         self.epsilon = self.initial_epsilon  # epsilon_greedy-policy
#         self.create_network()
#         self.create_training_method()
#
#         self.session = tf.InteractiveSession()
#         self.session.run(tf.global_variables_initializer())
#
#     def print_loss(self):
#         import matplotlib.pyplot as plt
#         print(len(self.cost_history))
#         plt.plot(np.arange(len(self.cost_history)), self.cost_history)
#         plt.ylabel('Cost')
#         plt.xlabel('step')
#         plt.show()
#
#     def create_network(self):
#         self.state_input = tf.placeholder(shape=[None, self.state_dim], dtype=tf.float32)
#         #  第一层
#         neuro_layer_1 = 20
#         w1 = tf.Variable(tf.random_normal([self.state_dim, neuro_layer_1]))
#         b1 = tf.Variable(tf.zeros([neuro_layer_1]) + 0.1)
#         l1 = tf.nn.relu(tf.matmul(self.state_input, w1) + b1)
#         #  第二层
#         w2 = tf.Variable(tf.random_normal([neuro_layer_1, self.action_dim]))
#         b2 = tf.Variable(tf.zeros([self.action_dim]) + 0.1)
#         # 输出层
#         self.Q_val = tf.matmul(l1, w2) + b2
#
#     def egreedy_action(self, state):
#         self.epsilon -= (0.5 - 0.01) / 10000
#         Q_val_output = self.session.run(self.Q_val, feed_dict={self.state_input: [state]})[0]
#         if random.random() <= self.epsilon:
#             return random.randint(0, self.action_dim - 1)  # 左闭右闭区间，np.random.randint为左闭右开区间
#         else:
#             return np.argmax(Q_val_output)
#
#     def max_action(self, state):
#         Q_val_output = self.session.run(self.Q_val, feed_dict={self.state_input: [state]})[0]
#         action = np.argmax(Q_val_output)
#         return action
#
#     def create_training_method(self):
#         self.action_input = tf.placeholder(shape=[None, self.action_dim], dtype=tf.float32)
#         self.y_input = tf.placeholder(shape=[None], dtype=tf.float32)  # ???是[None]吗？
#         Q_action = tf.reduce_sum(tf.multiply(self.Q_val, self.action_input), reduction_indices=1)
#         self.loss = tf.reduce_mean(tf.square(self.y_input - Q_action))
#         self.optimizer = tf.train.AdamOptimizer(0.0005).minimize(self.loss)
#
#     def perceive(self, state, action, reward, next_state, done):
#         cur_action = self.action_list[action:action + 1]
#         self.replay_memory_store.append((state, cur_action[0], reward, next_state, done))
#         if len(self.replay_memory_store) > self.memory_size:
#             self.replay_memory_store.popleft()
#         if len(self.replay_memory_store) > self.BATCH:
#             self.train_Q_network()
#
#     def train_Q_network(self):
#         self.step_index += 1
#         # obtain random mini-batch from replay memory
#         mini_batch = random.sample(self.replay_memory_store, self.BATCH)
#         state_batch = [data[0] for data in mini_batch]
#         action_batch = [data[1] for data in mini_batch]
#         reward_batch = [data[2] for data in mini_batch]
#         next_state_batch = [data[3] for data in mini_batch]
#
#         # calculate y
#         y_batch = []
#         Q_val_batch = self.session.run(self.Q_val, feed_dict={self.state_input: next_state_batch})  # 预估下一个状态的Q值
#         for i in range(0, self.BATCH):
#             done = mini_batch[i][4]
#             if done:
#                 y_batch.append(reward_batch[i])
#             else:
#                 y_batch.append(reward_batch[i] + self.gamma * np.max(Q_val_batch[i]))  # 选择最优的Q函数进行更新
#
#         _, self.cost = self.session.run([self.optimizer, self.loss], feed_dict={
#             self.y_input: y_batch,
#             self.state_input: state_batch,
#             self.action_input: action_batch
#         })
#
#
# TEST = 10
# STEP = 300
#
#
# def main():
#     env = gym.make('CartPole-v0')
#     agent = DeepQNetwork(env)
#     for i in range(EPISODE):
#         # if i % 50 == 0:
#         #     env.render()
#         #     print(i)
#         state = env.reset()
#         for step in range(STEP):
#             # env.render()
#             action = agent.egreedy_action(state)
#             next_state, reward, done, _ = env.step(action)
#             agent.perceive(state, action, reward, next_state, done)
#             state = next_state
#
#             if done:
#                 break
#         if i % 100 == 0:
#             total_reward = 0
#             for _ in range(TEST):
#                 state = env.reset()
#                 for _ in range(STEP):
#                     env.render()
#                     action = agent.max_action(state)  # direct action for test
#                     state, reward, done, _ = env.step(action)
#                     total_reward += reward
#                     if done:
#                         break
#             ave_reward = total_reward / TEST
#             print('episode: ', i, 'Evaluation Average Reward:', ave_reward)
#             if ave_reward >= 200:
#                 break
#     # agent.print_loss()
#
#
# if __name__ == '__main__':
#     main()




# from mMaze import Maze
from DQN import DQN
import gym

if __name__ == "__main__":
    env = gym.make('CartPole-v0')# 建立环境
    env = env.unwrapped
# 以下可以显示这个环境的state 和 action
    print(env.action_space)
    print(env.observation_space.shape[0])
    print(env.observation_space.high)
    print(env.observation_space.low)

# 初始化DQN的模型
    RL = DQN(n_actions=env.action_space.n,
             n_features = env.observation_space.shape[0],
             learning_rate = 0.01,
             e_greedy = 0.9,
             replace_target_iter = 100,
             memory_size = 2000,
             e_greedy_increment = 0.001,
             use_e_greedy_increment = 1000)

    steps = 0
    for episode in range(300): # 训练300个回合，这里环境模型，结束回合的标志是 倾斜程度和 X 的移动限度，你可以很容易从训练效果中看出来，当然了，也可以去看gym的底层代码，还是比较清晰的。

        observation = env.reset()
        ep_r = 0

        while True: # 训练没有结束的时候循环
            env.render()# 刷新环境
            action = RL.choose_action(observation)# 根据状态选择行为
            observation_next, reward, done, info = env.step(action) # 环境模型 采用行为，获得下个状态，和潜在的奖励

            x, x_dot, theta, theat_dot = observation_next # 这里拆分了 状态值 ，里面有四个参数
# 这里用了，x 和theta的限度值 来判断奖励的幅度，当然也可以gym自带的 ，但是这个效率据说比较高
            reward1 = (env.x_threshold - abs(x)) / env.x_threshold - 0.8
            reward2 = (env.theta_threshold_radians - abs(theta)) / env.theta_threshold_radians - 0.5
            reward = reward1 + reward2 # 这里将奖励综合

            RL.store_transition(observation, action, reward, observation_next)# 先存储到记忆库
            ep_r += reward# 这里只是为了观察奖励值是否依据实际情况变化，来方便判断模型的正确性
            if steps > 1000: # 这里一开始先不学习，先积累奖励
                RL.learn()
            if done: # 这里判断的是回合结束，显示奖励积累值，你可以看到每回合奖励的变化，来判定这样一连串行为的结果好不好
                print('episode :', episode,
                      'ep_r:', round(ep_r, 2),
                      "RL's epsilon", round(RL.epsilon, 3))
                break

            observation = observation_next# 跟新状态
            steps +=1
    RL.plot_cost()  # 训练结束后来观察我们的cost
