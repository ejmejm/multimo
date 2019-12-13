import copy

from mission_specs import WorldSpec, AgentSpec, Mission
from server import create_hosts, run_mission
import MalmoPython

if __name__ == '__main__':
    world_spec = WorldSpec(time_limit=30000, world_type='flat', start_time=6000)

    agent_args = {'mode': 'survival', 'spawn_point': (-203.5, 5, 217.5),
        'observation_space': 0, 'action_type': 'continuous', 'action_space': 0}

    agent_args['name'] = 'Agent1'
    agent_spec_1 = AgentSpec(**agent_args)

    agent_args['name'] = 'NotAgent1'
    agent_args['spawn_point'] = (-204.5, 5, 217.5)
    agent_spec_2 = AgentSpec(**agent_args)

    ports = [10000, 10001]
    mission = Mission(world_spec, [agent_spec_1, agent_spec_2], ports)

    for i in range(10):
        obs = mission.run()
        while mission.is_running():
            act_1 = [[1, 0, 0.2, 0, 0, 0, 0, 1], 'I am agent 1!']
            act_2 = [[-0.5, 0, 0, 0, 0, 0, 0, 0], 'I am not agent 1 :(']
            mission.step([act_1, act_2])