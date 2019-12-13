# Multimo

### By Edan Meyer

## Setup
1. Perform a git clone to download multimo.
2. Download the [latest Malmo release](https://github.com/microsoft/malmo/releases), and add the folder to the multimo root directory.
3. Install Malmo dependencies as listed on the [Malmo GitHub page]([https://github.com/microsoft/malmo](https://github.com/microsoft/malmo)).
4. Add the ".../MalmoPlatform/PythonExamples/MalmoPython.so" library to your path (the easiest way to do this is by putting it in your working directory). Optionally, you could also build the library yourself.

## Usage
1. Launch a client to port 10000 with the command, "python client.py -p 10000"
2. Try out an example with the command, "python examples/malmo_tutorial_8.py"
