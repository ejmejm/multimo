import MalmoPython
import os
import sys
import time

from mission_specs import compile_mission_spec
from client import start_client
from server import create_host, run_mission

# Create default Malmo objects:

agent_host = create_host()
my_mission, my_mission_record = compile_mission_spec()
run_mission(agent_host, my_mission, my_mission_record)