import MalmoPython
import numpy as np
import json
import sys
import time
from enum import Enum

from mission_specs import compile_mission_spec, WorldSpec, AgentSpec, Mission
from server import create_hosts, run_mission
from preprocessing import preprocess_state

if __name__ == '__main__':
    world_spec = WorldSpec(time_limit=10000, world_type='flat')
    agent_spec = AgentSpec(name='TestAgent', mode='cReAtive', spawn_point=(180, 10, 0),
        start_yaw=0, start_pitch=90,
        inventory='<InventoryItem slot="0" type="diamond_pickaxe"/>',
        observation_space=0, action_type='continuous',
        enable_chat=True)

    ports = [10000, 10001]

    mission = Mission(world_spec, [agent_spec, AgentSpec('Agent2')], ports)

    agents = mission.run()
    while mission.is_running():
        for agent in agents:
            agent.sendCommand('move 1')
        time.sleep(1)