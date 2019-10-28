
# Multimo

### By Edan Meyer

## Goals

#### Client Goals
- Allow easy creation of any number of clients with a single function
- Allow for parallel and sped up building of different clients (primarily with different ports)
- Ability to run headless
- Create a framework that allows 3 possibilities for agent controllers
	1. Designate one function that controls them all
	2. Designate a separate function for each agent
	3. Same function but different parameters (i.e. same I/O but different models)
- Provide 3 observation formats
	1. Raw/unstructured, raw pixel data
	2. Structured, human readable (i.e. pixels with chat log and specific items in inv.)
	3. Structured, NN compatible, such that data can be fed straight into most types of NNs, mostly numerical data
	4. Same as part 2 & 3 but with chat enabled
- Provide 2 action formats
    1. Raw, just mouse and keyboard manipulation
    2. Simplified, actions for things like picking up an item in a specific inv. Slot
    3. Same as 1 & 2 but with chat enabled

#### Server/World Goals
- Allow easy creation of a server with a single function
- Ability to host on public IP, allowing any normal player to join
- Provide a default XML mission template
- Allow certain, most important mission variable to be programatically edited
- World bounds
- Agent spawning bounds
- Simulation speed

#### Miscellaneous Goals
- Logging that makes it easy to see what is going on for an entire environment and a log that is easy to browse for individual agents
- Formal documentation
- Final Paper