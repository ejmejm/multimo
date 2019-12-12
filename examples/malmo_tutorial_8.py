import sys

sys.path.insert(0, '../')

from mission_specs import WorldSpec, AgentSpec, Mission
from server import create_hosts, run_mission
import MalmoPython

if __name__ == '__main__':
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
        observation_space=1, action_type='continuous', action_space=0,
        extra_handlers="""<AgentQuitFromTouchingBlockType>
        <Block type="gold_block diamond_block redstone_block" description="found_goal" />
      </AgentQuitFromTouchingBlockType>""")

    ports = [10000, 10001]
    mission = Mission(world_spec, [agent_spec], ports)
    mission.print_mission_spec()

    for i in range(10):
        agents = mission.run()
        while mission.is_running():
            mission.step([])