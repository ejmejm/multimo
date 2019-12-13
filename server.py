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

def create_hosts(n=1):
    hosts = []
    for _ in range(n):
        hosts.append(create_host())
    return hosts

def run_mission(agent_hosts, mission_spec, mission_record, client_ports):
    # Attempt to start a mission:
    if not isinstance(agent_hosts, list):
        agent_hosts = [agent_hosts]

    client_pool = MalmoPython.ClientPool()
    for port in client_ports:
        client_pool.add(MalmoPython.ClientInfo('127.0.0.1', port))

    for agent_idx in range(len(agent_hosts)):
        used_attempts = 0
        max_attempts = 5
        for _ in range(max_attempts):
            try:
                agent_hosts[agent_idx].startMission(mission_spec, client_pool, mission_record, agent_idx, '')
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

    print('Starting safe wait')
    safeWaitForStart(agent_hosts)
    
    # print('Waiting for the mission to start ', end=' ')
    # for agent_idx in range(len(agent_hosts)): 
    #     # Loop until mission starts:
    #     world_state = agent_hosts[agent_idx].getWorldState()
    #     while not world_state.has_mission_begun:
    #         print('.', end='')
    #         time.sleep(0.1)
    #         world_state = agent_hosts[agent_idx].getWorldState()
    #         for error in world_state.errors:
    #             print('Error:', error.text)

    # print()
    # print('Mission running ', end=' ')

def safeWaitForStart(agent_hosts):
    print("Waiting for the mission to start", end=' ')
    start_flags = [False for a in agent_hosts]
    start_time = time.time()
    time_out = 120  # Allow two minutes for mission to start.
    while not all(start_flags) and time.time() - start_time < time_out:
        states = [a.peekWorldState() for a in agent_hosts]
        start_flags = [w.has_mission_begun for w in states]
        errors = [e for w in states for e in w.errors]
        if len(errors) > 0:
            print("Errors waiting for mission start:")
            for e in errors:
                print(e.text)
            print("Bailing now.")
            exit(1)
        time.sleep(0.1)
        print(".", end=' ')
    print()
    if time.time() - start_time >= time_out:
        print("Timed out waiting for mission to begin. Bailing.")
        exit(1)
    print("Mission has started.")

    # # Loop until mission ends:
    # while world_state.is_mission_running:
    #     print('.', end='')
    #     time.sleep(0.1)
    #     world_state = agent_host.getWorldState()
    #     for error in world_state.errors:
    #         print('Error:', error.text)

    # print()
    # print('Mission ended')