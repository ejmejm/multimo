# Most of the base server and mission creation code
# comes directly from the Microsoft Malmo tutorials.
# https://github.com/microsoft/malmo/tree/master/Malmo/samples/Python_examples

import sys
import time

from malmo import MalmoPython

def create_server():
    agent_host = MalmoPython.AgentHost()
    try:
        agent_host.parse(sys.argv)
    except RuntimeError as e:
        print('ERROR:', e)
        print(agent_host.getUsage())
        exit(1)
    if agent_host.receivedArgument('help'):
        print(agent_host.getUsage())
        exit(0)

    return agent_host

def generate_mission(mission_xml=None, flat_word=False, seed=None,
    start_time=None, start_loc=None, creative=False, get_video=True,
    vid_width=320, vid_height=240, time_limit=None):
    """
    Creates and returns a mission spec and a mission record.
    The values of the parameters include some of the more important
    options for the mission spec XML. Other options can be set
    manually, or a manual XML can be passed in.
    """
    if mission_xml is not None:
        mission_spec = MalmoPython.MissionSpec(mission_xml, True)
    else:
        mission_spec = MalmoPython.MissionSpec()
        if not flat_word:
            mission_spec.createDefaultTerrain()
        if seed:
            mission_spec.setWorldSeed(seed)
        if start_time:
            mission_spec.setTimeOfDay(start_time)
        if start_loc:
            mission_spec.startAt(*start_loc)
        if creative:
            mission_spec.setModeToCreative()
        if get_video:
            mission_spec.requestVideo(vid_width, vid_height)
        if time_limit:
            mission_spec.timeLimitInSeconds(time_limit)

    mission_record = MalmoPython.MissionRecordSpec()
    return mission_spec, mission_record

def run_mission(agent_host, mission_spec, mission_record):
    # Attempt to start a mission:
    max_retries = 3
    for retry in range(max_retries):
        try:
            agent_host.startMission(mission_spec, mission_record)
            break
        except RuntimeError as e:
            if retry == max_retries - 1:
                print('Error starting mission:', e)
                exit(1)
            else:
                time.sleep(2)

    # Loop until mission starts:
    print('Waiting for the mission to start ', end=' ')
    world_state = agent_host.getWorldState()
    while not world_state.has_mission_begun:
        print('.', end='')
        time.sleep(0.1)
        world_state = agent_host.getWorldState()
        for error in world_state.errors:
            print('Error:', error.text)

    print()
    print('Mission running ', end=' ')

    # Loop until mission ends:
    while world_state.is_mission_running:
        print('.', end='')
        time.sleep(0.1)
        world_state = agent_host.getWorldState()
        for error in world_state.errors:
            print('Error:', error.text)

    print()
    print('Mission ended')