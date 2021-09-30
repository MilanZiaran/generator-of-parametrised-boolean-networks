# Generator of Parametrised Boolean Networks

The Generator of parametrised boolean networks provides generation of fully randomised parametrised boolean networks, as well as generation of parametrised boolean networks based on models, such as the Barabási-Albert model or the Watts-Strogatz model, using functions of the [networkx module](https://networkx.org/documentation/stable/index.html) in Python. Format of the network is the [SBML qual](http://www.colomoto.org/formats/sbml-qual.html). Furthermore, generator is able to parametrise non-parametrised boloean network passed as argument. Generator requires the non-parametrised network to be in the SBML qual format.

## Requirements
Python 3.7+\
Modules: 
- networkx 2.5

Note: You might need to install tkinter package on some distributions of linux as follows:
```shell
$ sudo apt-get install python3.7-tk
```
Source: (https://stackoverflow.com/a/25905642)

## Usage
There are three possible ways of using the application:

### 1. Via shell (deprecated)
With the commands below, the user can generate a parametrised boolean network based on the arguments.
#### Network based on Barabási-Albert model:
Command below generates a parametrised boolean network based on the [Barabási-Albert model](https://en.wikipedia.org/wiki/Barab%C3%A1si%E2%80%93Albert_model).
```shell
$ python3 parametrised_bn_gen/generator_of_parametrised_bn.py ba n m (seed?)
```
_n_     - Number of nodes in the network.\
_m_     - Number of existing nodes connected to the newly added node. (Note that this only applies to the initially generated network built on the Barabási-Albert model. Transformation of the network to parametrised boolean network converts each edge to directed edge in a random direction; therefore, this doesn't apply to the resulting network.)\
_seed_  - <Optional> Setting a seed value ensures that the generator generates the same  network for the same seed. If left unfilled, the generator uses the current time.
#### Network based on Watts-Strogatz model:
Command below generates a parametrised boolean network based on the [Watts-Strogatz model](https://en.wikipedia.org/wiki/Watts%E2%80%93Strogatz_model).
```shell
$ python3 parametrised_bn_gen/generator_of_parametrised_bn.py ws n k p (seed?)
```
_n_     - Number of nodes in the network.\
_k_     - Number of neighbours connected to each node. (Same change as with Barabási-Albert model, each edge is converted to directed edge in a random direction.)\
_p_     - Probablity of rewiring each edge.\
_seed_  - ...
#### Random network
```shell
$ python3 parametrised_bn_gen/generator_of_parametrised_bn.py rand n p (seed?)
```
_n_     - Number of nodes in the network.\
_p_     - Probability of the existence of an outgoing edge from one vertex to another.\
_seed_  - ...
#### Parametrising a non-parametrised boolean network
Use this command to parametrise non-parametrised boolean network.
```shell
$ python3 parametrised_bn_gen/generator_of_parametrised_bn.py your_network.sbml
```

User can then find the generated network in the same directory as the script, named generated_bn.sbml.

### 2. Passing a json configuration as argument (available from GUI)
Another way to generate a network is to create a json with the desired configuration. To do this, use:
```shell
$ python3 parametrised_bn_gen/generator_of_parametrised_bn.py your_conf.json
```
Example how the json should look like can be found within this repository in args.json. Please, use exactly this format and just change the values. Generating via json configuration is also viable using the GUI. GUI also supports exporting the entered configuration to json.

### 3. Using the GUI (most preferred)
Upon realising the complexity of the documentation grows directly proportional to the number of arguments and consequently it becomes easier for the user to get lost, I have created a straightforward GUI for the application. GUI was developed using the [tkinter module](https://docs.python.org/3/library/tkinter.html) in Python.

#### Installation
To run the GUI, install the parametrised_bn_gen module using:
Via ssh
```shell
$ pip3 install git+ssh://git@gitlab.fi.muni.cz/xziaran/generator-of-parametrised-boolean-networks.git
```
Via https
```shell
$ pip3 install git+https://gitlab.fi.muni.cz/xziaran/generator-of-parametrised-boolean-networks.git
```
Subsequently, clone the repository: \
Via ssh
```shell
$ git clone git@gitlab.fi.muni.cz:xziaran/generator-of-parametrised-boolean-networks.git
```
Via https
```shell
$ git clone https://gitlab.fi.muni.cz/xziaran/generator-of-parametrised-boolean-networks.git
```

#### Usage
Navigate to the cloned repository and run:
```shell
$ python3 user_interface.py
```
or use the provided binary for your system.

Fill the corresponding windows and start generating.
