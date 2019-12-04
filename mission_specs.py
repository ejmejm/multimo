from enum import Enum

import MalmoPython

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
        start_yaw=None, start_pitch=None, inventory=None, action_space='discrete',
        observation_space='default', reward_type=None, quit_condition=None):
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
            action_space (str): Type of action_space for the agent.
                Choose from {'dicrete', 'continuous'}.
            observation_space (str): Type of observation_space for the agent.
                Choose from {'dicrete', 'continuous'}.
            reward_type (str): String denoting the reward function for the agent.
                Should follow the XML formatting inside the <AgentHandlers> tag.
            quit_condition (str): String denoting the quit condition(s) for the agent.
                Should follow the XML formatting inside the <AgentHandlers> tag.
        """

        self.name = name
        self.mode = mode
        self.spawn_point = spawn_point
        self.start_yaw = start_yaw
        self.start_pitch = start_pitch
        self.inventory = inventory
        self.action_space = action_space
        self.observation_space = observation_space
        self.reward_type = reward_type
        self.quit_condition = quit_condition
    
    def get_xml(self):
        # xml = ''

        # if self.mode.lower() == 'survival':
        #     xml += '<AgentSection mode="Survival">\n'
        # elif self.mode.lower() == 'creative':
        #     xml += '<AgentSection mode="Creative">\n'
        # else:
        #     raise ValueError('`mode` must be one of the following values:' + \
        #         '\{"survival", "creative"\}')

        # xml += '<Name>{}</Name>\n'.format(self.name)

        # xml += '<AgentStart>\n'
        # xml += '<Placement>'
        # if self.spawn_point or self.start_pitch or self:
        # xml += '</Placement>'
        # xml += '</AgentStart>'

        
        # xml += '</AgentSection>'

        return '''<AgentSection mode="Survival">
                <Name>MalmoTutorialBot</Name>
                <AgentStart>
                    <Placement>
                    </Placement>
                </AgentStart>
                <AgentHandlers>
                  <ObservationFromFullStats/>
                  <ContinuousMovementCommands turnSpeedDegs="180"/>
                </AgentHandlers>
              </AgentSection>
              '''
        
class TaskSpec():
    def __init__(self):
        pass

    def get_xml(self):
        return ''

def compile_mission_spec(world_spec=None, agent_specs=None, 
        task_spec=None, summary='', xml=None, print_xml=False):
    if xml:
        return MalmoPython.MissionSpec(xml, True), MalmoPython.MissionRecordSpec()

    if world_spec is None and agent_specs is None and task_spec is None:
        return MalmoPython.MissionSpec(), MalmoPython.MissionRecordSpec()

    if world_spec is None:
        world_spec = WorldSpec()
    if agent_specs is None:
        agent_specs = [AgentSpec()]
    if task_spec is None:
        task_spec = TaskSpec()

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
    xml += task_spec.get_xml()

    xml += '</Mission>'

    if print_xml:
        print(xml)

    mission_spec = MalmoPython.MissionSpec(xml, True)
    mission_record = MalmoPython.MissionRecordSpec()
    
    return mission_spec, mission_record