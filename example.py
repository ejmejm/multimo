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
    world_spec = WorldSpec(time_limit=10000, world_type='flat', start_time=6000)
    agent_spec = AgentSpec(name='TestAgent', mode='survival', spawn_point=(180.5, 5, 0.5),
        start_yaw=0, start_pitch=20,
        inventory='<InventoryItem slot="0" type="diamond_pickaxe"/>',
        observation_space=0, action_type='continuous',
        action_space=2,
        enable_chat=True)

    ports = [10000, 10001]

    mission = Mission(world_spec, [agent_spec], ports)
    print(dir(mission.get_compiled_mission()))
    # print(mission.get_compiled_mission().getAllowedCommands())
    print(list(mission.get_compiled_mission().getListOfCommandHandlers(0)))

    agents = mission.run()
    while mission.is_running():
        mission.step([[[1, 0, 0.1, 0, 0, 1, 0, 1], '']])

    # i  = 0
    # agents = mission.run()
    # while mission.is_running():
    #     for agent in agents:
    #         if i < 5:
    #             agent.sendCommand('hotbar.5 0')
    #         # agent.sendCommand('jump 1')
    #         # agent.sendCommand('jumpmove 1')
    #         # agent.sendCommand('jump 1')
    #     i += 1
    #     time.sleep(1)