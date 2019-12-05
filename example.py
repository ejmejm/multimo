import MalmoPython
import numpy as np
import json
import sys
import time

from mission_specs import compile_mission_spec, WorldSpec, AgentSpec, TaskSpec
from client import start_client
from server import create_host, run_mission
from preprocessing import preprocess_state

if __name__ == '__main__':
    agent = create_host()

    # world_spec = WorldSpec(world_type='flat')
    world_spec = WorldSpec(time_limit=10000, world_type='flat')
    agent_spec = AgentSpec(name='TestAgent', mode='cReAtive', spawn_point=(180, 10, 0),
        start_yaw=0, start_pitch=90,
        inventory='<InventoryItem slot="0" type="diamond_pickaxe"/>',
        observation_space=1, action_type='continuous')
    task_spec = TaskSpec()

    my_mission, my_mission_record = compile_mission_spec(
        world_spec=world_spec, 
        agent_specs=agent_spec,
        task_spec=task_spec,
        print_xml=True)

    # two_digger.py as example for multiagent clientpool passed into startMission
    run_mission(agent, my_mission, my_mission_record, role=0, client_ports=[10000, 10001])
    # print('a')
    peek = agent.peekWorldState()
    print(agent.peekWorldState())
    print(dir(agent.peekWorldState()))
    print(peek.observations)
    print(peek.video_frames)
    while agent.peekWorldState().is_mission_running:
        state = agent.getWorldState()
        print(state)
        proc_state = preprocess_state(state, agent_spec, flat=False)
        print(proc_state)
        # agent.sendCommand('move 1')
        time.sleep(1)