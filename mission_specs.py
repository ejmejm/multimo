from enum import Enum

import MalmoPython

class WorldType(Enum):
    DEFAULT = 'default'
    FLAT = 'flat'

class WorldSpec():
    def __init__(self, world_type=WorldType.DEFAULT, seed=None, start_time=None,
                 freeze_time=False, time_limit=None, ms_per_tick=None):
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

        # '<AllowPassageOfTime>false</AllowPassageOfTime>'

        # Start time
        xml += '''<ServerInitialConditions>
        <Time>
        '''

        if self.start_time:
            xml += f'<StartTime>{self.start_time}</StartTime>\n'
        if self.freeze_time is not None:
            xml += f'<AllowPassageOfTime>{str(self.start_time).lower()}</AllowPassageOfTime>\n'
        
        # End time
        xml += '''</Time>
        </ServerInitialCondition>
        '''

        # Server handlers
        xml += '<ServerHandlers>\n'

        # Defining world types and seeds
        if self.seed and self.world_type==WorldType.DEFAULT:
            xml += f'''<DefaultWorldGenerator
            seed="{self.seed}"/>
            '''
        elif self.world_type == WorldType.DEFAULT:
            xml += '<DefaultWorldGenerator/>\n'
        elif self.seed and self.world_type==WorldType.FLAT:
            xml += f'''<FlatWorldGenerator
            seed="{self.seed}"/>
            '''
        elif self.world_type == WorldType.FLAT:
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
    def __init__(self):
        pass
    
    def get_xml(self):
        return ''
        
class TaskSpec():
    def __init__(self):
        pass

    def get_xml(self):
        return ''

def compile_mission_spec(world_spec=None, agent_spec=None, task_spec=None, summary=''):
    if world_spec is None and agent_spec is None and task_spec is None:
        return MalmoPython.MissionSpec(), MalmoPython.MissionRecordSpec()

    if world_spec is None:
        world_spec = WorldSpec()
    if agent_spec is None:
        agent_spec = AgentSpec()
    if task_spec is None:
        task_spec = TaskSpec()

    xml = f'''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
    <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
        <About>
            <Summary> {summary} </Summary>
        </About>
    '''

    xml += world_spec.get_xml()
    xml += agent_spec.get_xml()
    xml += task_spec.get_xml()

    xml += '</Mission>'

    mission_spec = MalmoPython.MissionSpec(xml, True)
    mission_record = MalmoPython.MissionRecordSpec()

    return mission_spec, mission_record