import numpy as np
import sys
import time

sys.path.insert(0, '../')

from mission_specs import WorldSpec, AgentSpec, Mission
from server import create_hosts, run_mission
import MalmoPython

import tensorflow as tf
from tensorflow.keras.layers import Input, Dense, Conv2D, MaxPool2D, Flatten

def gaussian_likelihood(x, mu, std):
    pre_sum = -(0.5*tf.log(2.*np.pi)) - (0.5*tf.log(std)) - (tf.square(x - mu))/(2.*std+1e-8)
    return tf.reduce_sum(pre_sum, axis=1)

def discount_rewards(rewards, gamma=0.99):
    new_rewards = [float(rewards[-1])]
    for i in reversed(range(len(rewards)-1)):
        new_rewards.append(float(rewards[i]) + gamma * new_rewards[-1])
    return new_rewards[::-1]

if __name__ == '__main__':
    ### Neural Network Stuff ###
    sess = tf.Session()

    in_shape = [480, 270, 3] # Size of reshaped observations

    # Creating a conv net for the policy and value estimator
    obs_op = Input(shape=in_shape)
    conv1 = Conv2D(16, 8, (4, 4), activation='relu')(obs_op)
    max_pool1 = MaxPool2D(2, 2)(conv1)
    conv2 = Conv2D(32, 4, (2, 2), activation='relu')(max_pool1)
    max_pool2 = MaxPool2D(2, 2)(conv2)
    conv2 = Conv2D(32, 4, (2, 2), activation='relu')(max_pool1)
    max_pool2 = MaxPool2D(2, 2)(conv2)
    conv2 = Conv2D(64, 4, (2, 2), activation='relu')(max_pool1)
    max_pool2 = MaxPool2D(2, 2)(conv2)
    dense1 = Dense(256, activation='relu')(max_pool2)
    flattened = Flatten()(dense1)

    out_op = Dense(8, activation='tanh')(flattened)
    value_op = Dense(1)(flattened)

    act_holders = tf.placeholder(tf.float32, shape=[None, out_op.shape[1].value])
    reward_holders = tf.placeholder(tf.float32, shape=[None])
    
    std = tf.Variable(0.5 * np.ones(shape=out_op.shape[1].value), dtype=tf.float32)
    out_act = out_op + tf.random_normal(tf.shape(out_op), dtype=tf.float32) * std
    
    log_probs = gaussian_likelihood(act_holders, out_op, std)
    loss = -tf.reduce_mean(log_probs * reward_holders)
    optimizer = tf.train.AdamOptimizer()
    update = optimizer.minimize(loss)
    
    train_model = lambda train_data: sess.run(update, 
        feed_dict={obs_op: np.stack(np.array(train_data)[:, 0]),
            act_holders: np.stack(np.array(train_data)[:, 1]),
            reward_holders: np.array(train_data)[:, 2]})
    
    sess.run(tf.global_variables_initializer())

    def get_raw_act(obs):
        return sess.run(out_act, feed_dict={obs_op: [obs]})[0]

    def format_act(act):
        act[:4] = np.clip(act[:4], -1, 1)
        act[4:] = [0 if a < 0 else 1 for a in act[4:]]
        return act

    ### Multimo Stuff ###

    world_spec = WorldSpec(time_limit=30000, world_type='flat', start_time=14000,
        extra_server_handlers="""
            <ClassroomDecorator>
                <complexity>
                <building>0.5</building>
                <path>0.5</path>
                <division>1</division>
                <obstacle>1</obstacle>
                <hint>0</hint>
                </complexity>
            </ClassroomDecorator>""")
    agent_spec = AgentSpec(name='TestAgent', mode='survival', spawn_point=(-203.5, 81, 217.5),
        observation_space=0, action_type='continuous', action_space=0,
        observation_dim=tuple(in_shape[:2]),
        extra_handlers="""<RewardForMissionEnd rewardForDeath="-10000">
        <Reward description="found_goal" reward="1000" />
        <Reward description="out_of_time" reward="-1000" />
        </RewardForMissionEnd>
        <RewardForTouchingBlockType>
        <Block type="gold_ore diamond_ore redstone_ore" reward="20" />
        </RewardForTouchingBlockType>
        <AgentQuitFromTouchingBlockType>
        <Block type="gold_block diamond_block redstone_block" description="found_goal" />
        </AgentQuitFromTouchingBlockType>""")

    ports = [10000]
    mission = Mission(world_spec, [agent_spec], ports)

    full_data = []
    all_rewards = []
    for i in range(1000):
        train_data = []
        ep_reward = 0
        obs = mission.run()[0]['pixels']
        while mission.is_running():
            if obs is None:
                time.sleep(0.1)
                continue
            
            raw_act = get_raw_act(obs)
            act = format_act(raw_act)

            obs, reward, _, _ = mission.step([[act]], wait_time=0.5)[0]
            obs = obs['pixels']

            train_data.append([obs, raw_act, reward])
            ep_reward += reward

        print(f'Episode Reward: {ep_reward}')
        train_data = np.array(train_data)
        train_data[:, 2] = discount_rewards(train_data[:, 2])
        full_data.extend(train_data)
        all_rewards.append(ep_reward)

        # Train every 5 episodes
        if (i+1) % 5 == 0:
            print('Training model...')
            train_model(full_data)
            full_data = []

    sess.close()