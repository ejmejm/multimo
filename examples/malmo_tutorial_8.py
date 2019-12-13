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
        observation_space=0, action_type='continuous', action_space=0,
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

    for i in range(10):
        obs = mission.run()
        while mission.is_running():
            mission.step([])