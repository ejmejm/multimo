import time

from preprocessing import preprocess_state
from server import create_hosts, run_mission

import MalmoPython

class Mission():
    def __init__(self, world_spec, agent_specs, client_ports):
        self.world_spec = world_spec
        self.agent_specs = agent_specs
        self.client_ports = client_ports
        self.agent_hosts = create_hosts(n=len(agent_specs))
        
        # self.act_types = []
        # for spec in agent_specs:
        #     self.act_types.append(spec.action_type.lower())
        
        # self.act_types = []
        # for spec in agent_specs:
        #     self.act_types.append(spec.action_type.lower())

    def run(self, print_xml=False):
        mission, mission_record = compile_mission_spec(
            world_spec=self.world_spec, 
            agent_specs=self.agent_specs,
            print_xml=print_xml)

        run_mission(self.agent_hosts, mission, mission_record, self.client_ports)

        return self.agent_hosts

    def get_compiled_mission(self):
        return compile_mission_spec(
                world_spec=self.world_spec, 
                agent_specs=self.agent_specs,
                print_xml=False)[0]

    def is_running(self):
        for agent_host in self.agent_hosts:
            if agent_host.peekWorldState().is_mission_running:
                return True

        return False

    def step(self, actions, wait_time=1):
        for agent_host, act, agent_spec in zip(self.agent_hosts, actions, self.agent_specs):
            if agent_spec.action_type == 'continuous':
                self.continuous_step(agent_host, act)
            elif agent_spec.action_type == 'discrete':
                self.discrete_step(agent_host, act)

        if wait_time > 0:
            time.sleep(wait_time)

        results = []
        for agent_host, agent_spec in zip(self.agent_hosts, self.agent_specs):
            state = agent_host.getWorldState()
            proc_state = preprocess_state(state, agent_spec, flat=False)
            results.append(proc_state)

        return results

    def continuous_step(self, agent_host, action):
        """Takes a set of actions in the environment based on `action`.

        Args:
            agent_host: Agent host to send the commands to.
            action (:obj:`list` of :obj:`float`): The first dimension of the
                list should be equal to the agent host's action space plus two
                (i.e. action space of 2 would mean list of length 3).
                The first dimensions of the list correspond to the following
                types of actions: [movement, chat, inventory, crafting].
                
                movement: List with shape of [8], corresponding to the following
                    actions: [move, strafe, turn, pitch, use, attack, crouch, jump].
                    The first four values should be [-1, 1], and the latter four
                    values should be {0, 1}.
                chat: String to be outputed to chat. An empty string will result in no
                    chat action being performed.
        """
        if not isinstance(action, list):
            raise ValueError('Actions must contain a list with an entry for each separate action space!')
        
        if len(action) == 0:
            return None
        if len(action) >= 1:
            move_acts = action[0]
            agent_host.sendCommand(f'move {move_acts[0]}')
            agent_host.sendCommand(f'pitch {move_acts[1]}')
            agent_host.sendCommand(f'turn {move_acts[2]}')
            agent_host.sendCommand(f'strafe {move_acts[3]}')
            agent_host.sendCommand(f'use {move_acts[4]}')
            agent_host.sendCommand(f'attack {move_acts[5]}')
            agent_host.sendCommand(f'crouch {move_acts[6]}')
            agent_host.sendCommand(f'jump {move_acts[7]}')

        return 0

    def discrete_step(self, agent_host, action):
        return 0

class WorldSpec():
    def __init__(self, world_type='default', seed=None, start_time=None,
                 freeze_time=None, time_limit=None, ms_per_tick=None):
        self.world_type = world_type
        self.seed = seed
        self.start_time = start_time
        self.freeze_time = freeze_time
        self.time_limit = time_limit
        self.ms_per_tick = ms_per_tick
    
    def get_xml(self):
        xml = ''

        # Mod settings
        if self.ms_per_tick:
            xml += f'''<ModSettings>
            <MsPerTick>{self.ms_per_tick}</MsPerTick>
            </ModSettings>
            '''

        # Start server section
        xml += '<ServerSection>\n'

        # Start time
        xml += '''<ServerInitialConditions>
        <Time>
        '''

        if self.start_time:
            xml += f'<StartTime>{self.start_time}</StartTime>\n'
        if self.freeze_time is not None:
            xml += f'<AllowPassageOfTime>{str(self.freeze_time).lower()}</AllowPassageOfTime>\n'
        
        # End time
        xml += '''</Time>
        </ServerInitialCondition>
        '''

        # Server handlers
        xml += '<ServerHandlers>\n'

        # Defining world types and seeds
        if self.seed and self.world_type == 'default':
            xml += f'''<DefaultWorldGenerator
            seed="{self.seed}"/>
            '''
        elif self.world_type == 'default':
            xml += '<DefaultWorldGenerator/>\n'
        elif self.seed and self.world_type == 'flat':
            xml += f'''<FlatWorldGenerator
            seed="{self.seed}"/>
            '''
        elif self.world_type == 'flat':
            xml += '<FlatWorldGenerator/>\n'

        # Times
        if self.time_limit:
            xml += f'<ServerQuitFromTimeUp description="" timeLimitMs="{self.time_limit}"/>\n'

        # End server handlers
        xml += '</ServerHandlers>\n'

        # End server section
        xml += '</ServerSection>\n'

        return xml

class AgentSpec():
    def __init__(self, name='default_agent', mode='survival', spawn_point=None,
        start_yaw=None, start_pitch=None, inventory=None, action_space=0,
        action_type='continuous', observation_space=0, observation_dim=(640, 360),
        enable_chat=True, reward_type=None, quit_condition=None, extra_handlers=None):
        """Creates a specification for a single Minecraft agent.

        Args:
            name (str): Name of the agent.
            mode (str): Type of gamemode, choose from {'survival', 'creative'}.
            spawn_point (:obj:`tuple` of :obj:`str`): Tuple of length 3,
                corresponding to the starting x, y, and z values of the agent.
            start_yaw (int): Starting yaw of the agent.
            start_pitch (int): Starting pitch of the agent.
            inventory (str): String denoting the starting inventory of the agent.
                Should follow the XML formatting inside the <Inventory> tag.
            action_space (int): Type of action_space for the agent.
                Choose from {0, 1}. Higher number modes contain more abstractions.
            action_type (string): Type of actions avaliable to the agent.
                Choose from {'discrete', 'continuous'}.
            observation_space (int): Type of observation_space for the agent.
                Choose from {0, 1}. Higher number modes contain more data.
            observation_dim (:obj:`tuple` of :obj:`int`): Two elements stating
                the width and height of the observation space.
            enable_chat (bool): Whether or not to allow the agent to see and
                use the chat.
            reward_type (str): String denoting the reward function for the agent.
                Should follow the XML formatting inside the <AgentHandlers> tag.
            quit_condition (str): String denoting the quit condition(s) for the agent.
                Should follow the XML formatting inside the <AgentHandlers> tag.
            extra_handlers (str): String denoting any extra handlers for the agent.
                Should follow the XML formatting inside the <AgentHandlers> tag.
        """

        self.name = name
        self.mode = mode
        self.spawn_point = spawn_point
        self.start_yaw = start_yaw
        self.start_pitch = start_pitch
        self.inventory = inventory
        self.action_space = action_space
        self.action_type = action_type
        self.observation_space = observation_space
        self.observation_dim = observation_dim
        self.enable_chat = enable_chat
        self.reward_type = reward_type
        self.quit_condition = quit_condition
        self.extra_handlers = extra_handlers
    
    def get_xml(self):
        xml = ''

        # Gamemode type
        if self.mode.lower() == 'survival':
            xml += '<AgentSection mode="Survival">\n'
        elif self.mode.lower() == 'creative':
            xml += '<AgentSection mode="Creative">\n'
        else:
            raise ValueError('`mode` must be one of the following values:' + \
                '\{"survival", "creative"\}')

        # Agent name
        xml += '<Name>{}</Name>\n'.format(self.name)

        xml += '<AgentStart>\n'

        # Initial spawn details
        if self.spawn_point or self.start_pitch or self.start_yaw:
            xml += '<Placement\n'

            if self.spawn_point:
                xml += 'x="' + str(self.spawn_point[0]) + '"\n'
                xml += 'y="' + str(self.spawn_point[1]) + '"\n'
                xml += 'z="' + str(self.spawn_point[2]) + '"\n'
            if self.start_pitch is not None:
                    xml += 'pitch="' + str(self.start_pitch) + '"\n'
            if self.start_yaw is not None:
                    xml += 'yaw="' + str(self.start_yaw) + '"\n'

            xml += '/>\n'

            if self.inventory is not None:
                xml += '<Inventory>\n'
                xml += self.inventory + '\n'
                xml += '</Inventory>\n'
                
        xml += '</AgentStart>\n'

        xml += '<AgentHandlers>\n'

        # Chat ability
        if self.enable_chat:
            xml += '<ObservationFromChat/>\n'
            xml += '<ChatCommands/>\n'

        # Observation space level of detail
        if self.observation_space >= 0:
            xml += '<VideoProducer\n'
            if self.observation_space == 0:
                xml += f'want_depth="{0}"\n'
            else:
                xml += f'want_depth="{1}"\n'
            xml += 'viewpoint="0"\n'
            xml += '>\n'
            xml += f'<Width>{self.observation_dim[0]}</Width>\n'
            xml += f'<Height>{self.observation_dim[1]}</Height>\n'
            xml += '<DepthScaling autoscale="1"/>\n'
            xml += '</VideoProducer>\n'

        if self.observation_space >= 1:
            xml += '<ObservationFromFullInventory/>\n'
            xml += '<ObservationFromFullStats/>\n'

        # Action type
        if self.action_type.lower() == 'discrete':
            xml += '<DiscreteMovementCommands autoFall="1"/>\n'
        elif self.action_type.lower() == 'continuous':
            xml += '<ContinuousMovementCommands/>\n'
        else:
            raise ValueError('`action_type` must be one of the following values:' + \
                '\{"discrete", "continuous"\}')

        # Action space level of detail
        if self.action_space >= 1:
            xml += '<InventoryCommands/>\n'
        if self.action_space >= 2:
            xml += '<SimpleCraftCommands/>\n'

        # Various handlers
        if self.reward_type:
            xml += self.reward_type + '\n'
        if self.quit_condition:
            xml += self.quit_condition + '\n'
        if self.extra_handlers:
            xml += self.extra_handlers + '\n'

        xml += '</AgentHandlers>\n'
        
        xml += '</AgentSection>\n'

        return xml

def compile_mission_spec(world_spec=None, agent_specs=None,
        summary='', xml=None, print_xml=False):
    if xml:
        return MalmoPython.MissionSpec(xml, True), MalmoPython.MissionRecordSpec()

    if world_spec is None and agent_specs is None:
        return MalmoPython.MissionSpec(), MalmoPython.MissionRecordSpec()

    if world_spec is None:
        world_spec = WorldSpec()
    if agent_specs is None:
        agent_specs = [AgentSpec()]

    # AgentSpecs should be a list
    if isinstance(agent_specs, AgentSpec):
        agent_specs = [agent_specs]

    xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
    <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <About>
            <Summary> {summary} </Summary>
        </About>
    '''

    xml += world_spec.get_xml()
    xml += '\n'
    for agent_spec in agent_specs:
        xml += agent_spec.get_xml()
        xml += '\n'

    xml += '</Mission>'

    if print_xml:
        print(xml)

    mission_spec = MalmoPython.MissionSpec(xml, True)
    mission_record = MalmoPython.MissionRecordSpec()
    
    return mission_spec, mission_record