# Most of the base server and mission creation code
# comes directly from the Microsoft Malmo tutorials.
# https://github.com/microsoft/malmo/tree/master/Malmo/samples/Python_examples

import sys
import time

import MalmoPython

def create_host():
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
    print('Sucessfully created agent host!')

    return agent_host

# def generate_mission(mission_xml=None, flat_word=False, seed=None,
#     start_time=None, start_loc=None, creative=False, get_video=True,
#     vid_width=320, vid_height=240, time_limit=None):
#     """
#     Creates and returns a mission spec and a mission record.
#     The values of the parameters include some of the more important
#     options for the mission spec XML. Other options can be set
#     manually, or a manual XML can be passed in.
#     """
#     if mission_xml is not None:
#         mission_spec = MalmoPython.MissionSpec(mission_xml, True)
#     else:
#         mission_spec = MalmoPython.MissionSpec()
#         if not flat_word:
#             mission_spec.createDefaultTerrain()
#         if seed:
#             mission_spec.setWorldSeed(seed)
#         if start_time:
#             mission_spec.setTimeOfDay(start_time)
#         if start_loc:
#             mission_spec.startAt(*start_loc)
#         if creative:
#             mission_spec.setModeToCreative()
#         if get_video:
#             mission_spec.requestVideo(vid_width, vid_height)
#         if time_limit:
#             mission_spec.timeLimitInSeconds(time_limit)
#         mission_spec.

#     mission_record = MalmoPython.MissionRecordSpec()
#     return mission_spec, mission_record

def run_mission(agent_host, mission_spec, mission_record, client_ports=None):
    # Attempt to start a mission:
    used_attempts = 0
    max_attempts = 5
    for _ in range(max_attempts):
        try:
            print('trying to start')
            if client_ports is None:
                agent_host.startMission(mission_spec, mission_record)
            else:
                client_pool = MalmoPython.ClientPool()
                for port in client_ports:
                    client_pool.add(MalmoPython.ClientInfo('127.0.0.1',port))
                agent_host.startMission(mission_spec, client_pool, mission_record, 0, '')
            break
        except MalmoPython.MissionException as e:
            errorCode = e.details.errorCode
            if errorCode == MalmoPython.MissionErrorCode.MISSION_SERVER_WARMING_UP:
                print("Server not quite ready yet - waiting...")
                time.sleep(2)
            elif errorCode == MalmoPython.MissionErrorCode.MISSION_INSUFFICIENT_CLIENTS_AVAILABLE:
                print("Not enough available Minecraft instances running.")
                used_attempts += 1
                if used_attempts < max_attempts:
                    print("Will wait in case they are starting up.", max_attempts - used_attempts, "attempts left.")
                    time.sleep(2)
            elif errorCode == MalmoPython.MissionErrorCode.MISSION_SERVER_NOT_FOUND:
                print("Server not found - has the mission with role 0 been started yet?")
                used_attempts += 1
                if used_attempts < max_attempts:
                    print("Will wait and retry.", max_attempts - used_attempts, "attempts left.")
                    time.sleep(2)
            else:
                print("Other error:", e.message)
                print("Waiting will not help here - bailing immediately.")
                exit(1)
        if used_attempts == max_attempts:
            print("All chances used up - bailing now.")
            exit(1)

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