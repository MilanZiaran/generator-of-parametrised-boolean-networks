#!/usr/bin/env

import json
import networkx as nx
import numpy
from math import cos, sin
from os import path
import re
import time
import xml.etree.ElementTree as ET

# constants
MAXSIZE = 2**31-1  # (replaces maxint due to consistency among devices)


def write_vertices_to_sbml(sbml_f, num_of_vertices: int) -> None:
    """Writes vertices to the sbml file in sbml qual format

    Parameters
    ----------
    sbml_f
        sbml file
    num_of_vertices : int
        Number of vertices

    Returns
    -------
    None
    """
    sbml_f.write('<qual:listOfQualitativeSpecies xmlns:qual="http://www.sbml.org/sbml/level3/version1/qual/version1">')
    for vertex in range(num_of_vertices):
        sbml_f.write(f'<qual:qualitativeSpecies qual:constant="false" '
                     f'qual:id="X{vertex}" qual:maxLevel="1" qual:name="X{vertex}"/>')
    sbml_f.write('</qual:listOfQualitativeSpecies>')


def generate_layout(sbml_f, num_of_vertices: int) -> None:
    """Generates layout for the network (with AEON having auto-layout option, this is unnecessary)

    Generates circle layout for the network so all the vertices are not at the same coordinates.

    Parameters
    ----------
    sbml_f
        sbml file
    num_of_vertices : int
        Number of vertices

    Returns
    -------
    None
    """
    sbml_f.write('<layout:listOfLayouts xmlns:layout="http://www.sbml.org/sbml/level3/version1/layout/version1" '
                 'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">')
    sbml_f.write('<layout:layout layout:id="__layout__">')
    sbml_f.write('<layout:listOfAdditionalGraphicalObjects>')
    # following circle algorithm from https://www.mathopenref.com/coordcirclealgorithm.html
    angle = 0
    step = 360 / num_of_vertices
    radius = 200
    for vertex in range(num_of_vertices):
        sbml_f.write(f'<layout:generalGlyph layout:id="_ly_X{vertex}" layout:reference="X{vertex}">')
        sbml_f.write('<layout:boundingBox>')
        sbml_f.write(f'<layout:position layout:x="{radius * round(cos(angle), 2)}" '
                     f'layout:y="{radius * round(sin(angle), 2)}"/>')
        sbml_f.write('<layout:dimensions layout:height="25" layout:width="45"/>')
        sbml_f.write('</layout:boundingBox>')
        sbml_f.write('</layout:generalGlyph>')
        angle += step
    sbml_f.write('</layout:listOfAdditionalGraphicalObjects>')
    sbml_f.write('</layout:layout>')
    sbml_f.write('</layout:listOfLayouts>')


def generate_and_write_function(sbml_f, vertex: int, vertices: list, idx: int,
                                arity: int, seed: int) -> None:
    """Generates uninterpreted function in update function for given vertex

    Function checks lower and upper bound of the arity of the uninterpreted function. If it's not possible to satisfy
    these constraints, uninterpreted function won't be generated. Although this might appear counterintuitive, user
    is able to specify arity of the uninterpreted function.

    Parameters
    ----------
    sbml_f
        sbml file
    vertex : int
        Vertex
    vertices : list
        List of tuples (node, type_of_regulation), i.e. regulators of give vertex
    idx : int
        Number of vertices for update function - 1 in this recursion call (see 'generate_update_function' function)
    arity : int
        Randomly generated arity of an uninterpreted function
    seed : int
        Seed value

    Returns
    -------
    None
    """
    if arity > 0 and (len(vertices) >= arity):
        numpy.random.seed(seed)
        rand_values = numpy.random.choice([0, 1], size=len(vertices))
        if sum(rand_values) >= arity:
            sbml_f.write('<apply>')
            sbml_f.write(
                f'<csymbol>F{str(vertex) + "_" + str(idx)}</csymbol>')  # str(vertex) + "_" + str(idx) is unique id here
            sbml_f.write(f'<ci>X{vertices[idx][0]}</ci>')
            total = 1
            i = 0
            for vrtx in vertices:
                if rand_values[i] and total < arity:
                    if vertices[idx][0] != vrtx[0]:
                        sbml_f.write(f'<ci>X{vrtx[0]}</ci>')
                        total += 1
                i += 1
            sbml_f.write('</apply>')
        else:
            write_var_to_sbml(sbml_f, vertices, idx)
    else:
        write_var_to_sbml(sbml_f, vertices, idx)


def write_var_to_sbml(sbml_f, vertices: list, idx: int):
    """Writes variable of the update function to sbml file

    Parameters
    ----------
    sbml_f
        sbml file
    vertices : list
        List of tuples (node, regulation_type). Denotes regulators of given 'vertex'
    idx : int
        Number of vertices for update function - 1 in this recursion call (see 'generate_update_function' function)

    Returns
    -------
    None
    """
    is_not = False
    if not vertices[idx][1]:  # if the regulation leading to vertex vertices[idx] is inhibiting
        is_not = True
        sbml_f.write('<apply>')
        sbml_f.write('<not/>')
    sbml_f.write('<apply>')
    sbml_f.write('<eq/>')
    sbml_f.write(f'<ci>X{vertices[idx][0]}</ci>')
    sbml_f.write('<cn type="integer">1</cn>')
    sbml_f.write('</apply>')
    if is_not:
        sbml_f.write('</apply>')


def generate_update_function(sbml_f, vertex: int, vertices: list, num_of_upd_ver: int,
                             rand_which: list, rand_arr: list, i: int, j: int, seed_vals: list,
                             l_bound: int, u_bound: int) -> None:
    """Recursive function that generates update function for given vertex

    Parameters
    ----------
    sbml_f
        sbml file
    vertex : int
        Vertex
    vertices : list
        List of tuples (node, regulation_type). Denotes regulators of given 'vertex'
    num_of_upd_ver : int
        Number of regulations for given vertex
    rand_which : list
        Pre-generated list of booleans used in generation of the update function
    rand_arr
        Pre-generated list of booleans used in generation of the update function
    i : int
        Iterative variable
    j : int
        Iterative variable
    seed_vals : list
        Pre-generated seed values for generation of seeds for the generation of uninterpreted function
    l_bound : int
        Lower bound of the arity of the uninterpreted functions
    u_bound : int
        Upper bound of the arity of the uninterpreted functions

    Returns
    -------
    None
    """
    idx = num_of_upd_ver - 1
    which = rand_which[i]
    if which and num_of_upd_ver >= 2:
        sbml_f.write('<apply>')
        sbml_f.write('<or/>')
    elif not which and num_of_upd_ver >= 2:
        sbml_f.write('<apply>')
        sbml_f.write('<and/>')
    if num_of_upd_ver > 1:
        generate_update_function(sbml_f, vertex, vertices, num_of_upd_ver - 1,
                                 rand_which, rand_arr, i + 1, j + 1, seed_vals, l_bound, u_bound)
    if rand_arr[j] or len(vertices) < l_bound:
        write_var_to_sbml(sbml_f, vertices, idx)
    else:
        seed = seed_vals[idx]
        numpy.random.seed(seed)
        arity = numpy.random.randint(low=l_bound, high=u_bound + 1)
        generate_and_write_function(sbml_f, vertex, vertices, idx, arity, seed)
    if idx >= 1:  # <apply> tag can't be closed between the first two vertices
        sbml_f.write('</apply>')


def write_update_function(sbml_f, vertex: int, vertices_for_update_f: list,
                          seed: int, seed_which: int, seed_arr: int, rand_ch: int,
                          l_bound: int, u_bound: int) -> None:
    """Writes update function to sbml using 'generate_update_function' function

    If the number of regulations is greater than 4, for AEON to be able to process the model,
    update function has to be generated.

    Parameters
    ----------
    sbml_f
        sbml file
    vertex : int
        Vertex
    vertices_for_update_f : list
        List of tuples (node, regulation_type). Denotes regulators of given 'vertex'
    seed : int
        Seed value
    seed_which : int
        Seed used for generation of the 'rand_which' list, used in 'generate_update_function'
    seed_arr : int
        Seed used for generation of the 'rand_arr' list, used in 'generate_update_function'
    rand_ch : int
        Bool value to determine if the vertex will have an update function
    l_bound : int
        Lower bound of the arity of the uninterpreted functions
    u_bound : int
        Upper bound of the arity of the uninterpreted functions

    Returns
    -------
    None
    """
    if len(vertices_for_update_f) > 4 or (rand_ch and len(vertices_for_update_f) > 0):
        # Is the given vertex going to have an update function?
        # If there are more than 4 incoming regulations to the vertex, update function has to be generated,
        # otherwise AEON would yield an error 'Error: Function too large for on-the-fly analysis.'
        sbml_f.write('<qual:listOfFunctionTerms>')
        sbml_f.write('<qual:defaultTerm qual:resultLevel="0"/>')
        sbml_f.write('<qual:functionTerm qual:resultLevel="1">')
        sbml_f.write('<math xmlns="http://www.w3.org/1998/Math/MathML">')
        numpy.random.seed(seed)
        seed_vals = numpy.random.randint(MAXSIZE, size=len(vertices_for_update_f))
        numpy.random.seed(seed_which)
        rand_which = numpy.random.choice([0, 1], size=len(vertices_for_update_f))
        numpy.random.seed(seed_arr)
        rand_arr = numpy.random.choice([0, 1], size=len(vertices_for_update_f))
        generate_update_function(sbml_f, vertex, vertices_for_update_f, len(vertices_for_update_f),
                                 list(rand_which), list(rand_arr), 0, 0, list(seed_vals), l_bound, u_bound)
        sbml_f.write('</math>')
        sbml_f.write('</qual:functionTerm>')
        sbml_f.write('</qual:listOfFunctionTerms>')


def generate_transitions(num_of_vertices: int, probability_of_edge: float, seed: int, frac_reg: float) -> dict:
    """Generates transitions for the network when generating fully randomised network

    Parameters
    ----------
    num_of_vertices : int

    probability_of_edge : float
        Probability of an existence of an edge leading from one vertex to another
    seed : int
        Seed value

    Returns
    -------
    dict
        Dictionary where vertex is a key and its value is a list of regulations
    """
    inc_transitions = {k: [] for k in range(num_of_vertices)}
    numpy.random.seed(seed)
    rand_prob_vals = numpy.random.randint(low=1, high=101, size=(num_of_vertices, num_of_vertices))  # 101 off by one
    numpy.random.seed(seed)
    rand_reg_types = numpy.random.choice([True, False], p=[frac_reg, 1 - frac_reg],
                                         size=(num_of_vertices, num_of_vertices))
    i = 0
    for vertex in range(num_of_vertices):
        j = 0
        for other_vertex in range(num_of_vertices):
            if rand_prob_vals[i][j] <= probability_of_edge * 100:
                inc_transitions[other_vertex].append((vertex, rand_reg_types[i][j]))
            j += 1
        i += 1
    return inc_transitions


def write_transitions(sbml_f, inc_transitions: dict, seed_: int, l_bound: int, u_bound: int) -> None:
    """Writes transitions to sbml file

    Parameters
    ----------
    sbml_f
        sbml file
    inc_transitions : dict
        Dictionary where vertex is a key and its value is a list of regulations
    seed_ : int
        Seed for generating seeds needed in 'write_update_function' function
    l_bound : int
        Lower bound of the arity of the uninterpreted functions
    u_bound : int
        Upper bound of the arity of the uninterpreted functions

    Returns
    -------
    None
    """
    sbml_f.write('<qual:listOfTransitions xmlns:qual="http://www.sbml.org/sbml/level3/version1/qual/version1">')
    numpy.random.seed(seed_)
    seeds = list(numpy.random.randint(MAXSIZE, size=3))
    numpy.random.seed(seeds[0])
    rand_ch = numpy.random.choice([0, 1], size=len(inc_transitions))
    i = 0
    for vertex in inc_transitions:
        sbml_f.write(f'<qual:transition qual:id="tr_X{vertex}">')
        sbml_f.write('<qual:listOfInputs>')
        for other_vertex in inc_transitions[vertex]:
            if other_vertex[1]:
                sign = 'positive'
            else:
                sign = 'negative'
            sbml_f.write(f'<qual:input qual:id="tr_X{other_vertex[0]}_in_X{vertex}" '
                         f'qual:qualitativeSpecies="X{other_vertex[0]}" '
                         f'qual:sign="{sign}" qual:transitionEffect="none"/>')
        sbml_f.write('</qual:listOfInputs>')
        sbml_f.write('<qual:listOfOutputs>')
        sbml_f.write(f'<qual:output qual:id="tr_X{vertex}_out" qual:qualitativeSpecies="X{vertex}" '
                     f'qual:transitionEffect="assignmentLevel"/>')
        sbml_f.write('</qual:listOfOutputs>')
        write_update_function(sbml_f, vertex, inc_transitions[vertex], seed_, seeds[1], seeds[2], list(rand_ch)[i],
                              l_bound, u_bound)
        sbml_f.write('</qual:transition>')
        i += 1
    sbml_f.write('</qual:listOfTransitions>')


def write_transitions_to_dict(graph, num_of_vertices: int, seed: int, bool_seed_trans: int, frac_reg: float) -> dict:
    """Writes transitions to dictionary for easier usage

    Parameters
    ----------
    graph
        Generated graph
    num_of_vertices : int
        Number of vertices
    seed : int
        Seed value
    bool_seed_trans : int
        Seed value used to generate list of booleans for regulation types
    frac_reg : float
        Probability that a regulation is activating

    Returns
    -------
    dict
        Dictionary where vertex is a key and its value is a list of its regulators
    """
    # external graph generator from networkx library generates graph with undirected edges
    # thus we have to transform the edges
    # line below taken from https://stackoverflow.com/a/11509759 and it assigns empty list to each vertex
    transitions = {k: [] for k in range(num_of_vertices)}
    num_of_edges = len(graph.edges)
    numpy.random.seed(seed)
    rand_reg_types = numpy.random.choice([True, False], p=[frac_reg, 1 - frac_reg], size=num_of_edges)
    # following lines inspired by https://stackoverflow.com/a/19597672
    # this ensures desired number of activating regulations within the generated network
    rand_choice = numpy.random.choice([True, False], size=num_of_edges)  # create an array full of zeros
    i = 0
    for edge in graph.edges:
        reg_type = rand_reg_types[i]
        if rand_choice[i]:
            transitions[edge[0]].append((edge[1], reg_type))
        else:
            transitions[edge[1]].append((edge[0], reg_type))
        i += 1
    return transitions


def generate_watts_strogatz_graph(sbml_f, num_of_vertices: int, num_of_connections: int, probability: float,
                                  seed: int, seeds: list, l_bound: int, u_bound: int, frac_reg: float):
    """Generates a Watts-Strogatz small-world graph, then transforms it to SBML-qual format
    (Docs taken from the watts_strogatz_graph function in networkx module)
    
    Parameters
    ----------
    sbml_f
        sbml file
    num_of_vertices
        Number of vertices within the network
    num_of_connections
        Each node is joined with its `num_of_connections` nearest neighbors in a ring topology
    probability
        The probability of rewiring each edge
    seed
        Seed value
    seeds : list
        List of seeds
    l_bound : int
        Lower bound of the arity of the uninterpreted functions
    u_bound : int
        Upper bound of the arity of the uninterpreted functions
    frac_reg : float, optional
        Fraction of activating regulations within the network

    Returns
    -------
    None
    """
    g = nx.watts_strogatz_graph(num_of_vertices, num_of_connections, probability, seed=seed)
    generate_layout(sbml_f, num_of_vertices)
    write_vertices_to_sbml(sbml_f, num_of_vertices)
    inc_transitions = write_transitions_to_dict(g, num_of_vertices, seed, seeds[0], frac_reg)
    write_transitions(sbml_f, inc_transitions, seeds[1], l_bound, u_bound)


def generate_barabasi_albert_graph(sbml_f, num_of_vertices: int, connections: int,
                                   seed: int, seeds: list, l_bound: int, u_bound: int, frac_reg: float):
    """Generates a Barabasi-Albert graph, then transoforms it to SBML-qual format
    (Docs taken from the barabasi_albert_graph function in networkx module)

    Parameters
    ----------
    sbml_f
        sbml file
    num_of_vertices
        Number of vertices within the network
    connections
        Number of edges to attach from a new node to existing nodes
    seed : int
        Seed value
    seeds : list
        List of seeds
    l_bound : int
        Lower bound of the arity of the uninterpreted functions
    u_bound : int
        Upper bound of the arity of the uninterpreted functions
    frac_reg : float, optional
        Fraction of activating regulations within the network

    Returns
    -------
    None
    """
    g = nx.barabasi_albert_graph(num_of_vertices, connections, seed=seed)
    generate_layout(sbml_f, num_of_vertices)
    write_vertices_to_sbml(sbml_f, num_of_vertices)
    inc_transitions = write_transitions_to_dict(g, num_of_vertices, seed, seeds[0], frac_reg)
    write_transitions(sbml_f, inc_transitions, seeds[1], l_bound, u_bound)


def generate_random_graph(sbml_f, num_of_vertices: int, probability_of_edge: float, seed: int,
                          seed_trans: int, l_bound: int, u_bound: int, frac_reg: float):
    """Generates fully randomised network

    Parameters
    ----------
    sbml_f
        sbml file
    num_of_vertices
        Number of vertices within the network
    probability_of_edge
        Probability of an existence of an edge leading from one vertex to another
    seed : int
        Seed value
    seed_trans : int
        Seed used in generation of transitions
    l_bound : int
        Lower bound of the arity of the uninterpreted functions
    u_bound : int
        Upper bound of the arity of the uninterpreted functions
    frac_reg : float, optional
        Fraction of activating regulations within the network

    Returns
    -------
    None
    """
    generate_layout(sbml_f, num_of_vertices)
    write_vertices_to_sbml(sbml_f, num_of_vertices)
    inc_transitions = generate_transitions(num_of_vertices, probability_of_edge, seed, frac_reg)
    write_transitions(sbml_f, inc_transitions, seed_trans, l_bound, u_bound)


def generate_bn(num_of_vertices: int, seed=int(time.time()), probability=0, num_of_connections=0,
                l_bound=2, u_bound=4, frac_reg=0.8, ba=False, ws=False, random=False, loc="", n=1):
    # make it possible to generate arbitrary amount of vertices?
    """Generates random parametrised boolean network in SBML qual format.
    - http://www.colomoto.org/formats/sbml-qual.html

    Parameters
    ----------
    num_of_vertices : int
        User-defined size of the boolean network
    seed : int, optional
        Seed value for the option to regenerate the same network. Default seed is time.time()
    probability : float, optional
        For 'random' network, user-defined probability of an outgoing edge from one vertex to another
        For the Watts-Strogatz, it is the probability of rewiring each edge
        Not used in the Barabási-Albert model
    num_of_connections : int, optional
        For Barabási-Albert model, it is number of edges to attach from a new node to existing nodes
        For Watts-Strogatz, each node is joined with its `num_of_connections` nearest neighbors in a ring topology
        Not used in 'random' network
    l_bound : int, optional
        Lower bound of the arity of the uninterpreted functions. Default value is 2
    u_bound : int, optional
        Upper bound of the arity of the uninterpreted functions
        Default value is 4, so AEON doesn't face the state-space explosion
    frac_reg : float, optional
        Fraction of activating regulations within the network
    ba : bool, optional
        Barabási-Albert model
    ws : bool, optional
        Watts-Strogatz model
    random : bool, optional
        Fully randomised network
    loc : str
        Directory to store the networks in
    n : int
        Number of networks to generate. Keep in mind that if 'n' > 1 and 'seed' is not set to default, you will get 'n'
        same networks

    Returns
    -------
    None
    """
    numpy.random.seed(seed)
    network_seeds = list(numpy.random.randint(MAXSIZE, size=n))
    for i in range(n):
        curr_seed = int(network_seeds[i])
        if ba or ws:
            gen = f'ba_{num_of_connections}' if ba else f'ws_{num_of_connections}_{probability}'
        else:
            gen = f'rand_{probability}'
        with open(f'{loc}bn_{gen}_s{seed}_l{l_bound}_u{u_bound}_'
                  f'f{frac_reg}_n{num_of_vertices}_{i}.sbml', 'w+') as sbml_f:
            sbml_f.write('<?xml version=\'1.0\' encoding=\'UTF-8\' standalone=\'no\'?>')
            sbml_f.write('<sbml xmlns="http://www.sbml.org/sbml/level3/version1/core" '
                         'layout:required="false" level="3" qual:required="true" '
                         'xmlns:layout="http://www.sbml.org/sbml/level3/version1/layout/version1" version="1" '
                         'xmlns:qual="http://www.sbml.org/sbml/level3/version1/qual/version1">')
            sbml_f.write('<model>')
            numpy.random.seed(curr_seed)
            seeds = list(numpy.random.randint(MAXSIZE, size=2))
            if random:
                generate_random_graph(sbml_f, num_of_vertices, probability,
                                      curr_seed, seeds[0], l_bound, u_bound, frac_reg)
            elif ba:
                generate_barabasi_albert_graph(sbml_f, num_of_vertices, num_of_connections, curr_seed, seeds, l_bound,
                                               u_bound, frac_reg)
            elif ws:
                generate_watts_strogatz_graph(sbml_f, num_of_vertices, num_of_connections,
                                              probability, curr_seed, seeds, l_bound, u_bound, frac_reg)
            sbml_f.write('</model>')
            sbml_f.write('</sbml>')


"""----------------------------------------------FUNCTIONS FOR INPUT CHECK-------------------------------------------"""


def check_number_of_vertices(arg):
    # https://stackoverflow.com/a/56089296 I have read this discussion to help me decide how to deal with incorrect
    # arguments.
    # 'print' in combination with 'exit' statement makes the error message more readable for the user; however,
    # raising exception has value for the programmer. Not sure which one to keep, print&exit seems more elegant.
    try:
        int(arg)
    except ValueError:
        # raise ValueError(f"Number of vertices is not in correct format, expected int, got {type(arg)}")
        print(f"Number of vertices is not in correct format, expected int, got {type(arg)}")
        exit(1)
    if int(arg) < 2:  # or > n, after I find the threshold
        # raise ValueError(f"Number of vertices must be in range [2, n), got {arg}")
        print(f"Number of vertices must be in range [2, n), got {arg}", file=stderr)
        exit(1)


def check_probability_argument(arg):
    try:
        float(arg)
    except ValueError:
        # raise ValueError(f"Probability is not in a correct format, expected float, got {type(arg)}")
        print(f"Probability is not in a correct format, expected float, got {type(arg)}")
        exit(1)
    if round(float(arg), 2) <= 0 or round(float(arg), 2) > 1:
        # raise ValueError(f"Probability must be in range (0, 1> rounded to two decimal places, got {arg}")
        print(f"Probability rounded to two decimal places must be within (0, 1] range, got {arg}", file=stderr)
        exit(1)


def check_probability_argument_for_ws(arg):
    try:
        float(arg)
    except ValueError:
        # raise ValueError(f"Probability is not in a correct format, expected float, got {type(arg)}")
        print(f"Probability is not in a correct format, expected float, got {type(arg)}")
        exit(1)
    if round(float(arg), 2) < 0 or round(float(arg), 2) > 1:
        # raise ValueError(f"Probability must be in range [0, 1> rounded to two decimal places, got {arg}")
        print(f"Probability rounded to two decimal places must be within [0, 1] range, got {arg}", file=stderr)
        exit(1)


def check_num_of_connections(arg, threshold):
    # threshold makes the function reusable for different models
    try:
        int(arg)
    except ValueError:
        # raise ValueError(f"Number of vertices is not in correct format, expected int, got {type(arg)}")
        print(f"Number of vertices is not in correct format, expected int, got {type(arg)}")
        exit(1)
    if int(arg) < threshold:  # or > n, after I find the threshold
        # raise ValueError(f"Number of vertices must be in range [{threshold}, n), got {arg}")
        print(f"Number of connections must be within [{threshold}, n) range, got {arg}", file=stderr)
        exit(1)


"""------------------------------------------------------------------------------------------------------------------"""


def remove_whitespaces(network):
    # https://stackoverflow.com/a/43447546
    try:
        with open(network, 'r') as n:
            lines = n.readlines()
        lines = [line.strip() for line in lines]
        return ''.join(lines)
    except FileNotFoundError:
        print(f"File \'{network}\' not found.", file=stderr)
        exit(1)


def modify_network(network, parametrisation_frac: float, seed: int, loc=""):
    """Parametrises give network

    Parameters
    ----------
    network
        Network to be parametrised
    parametrisation_frac : float
        Denotes the fraction of all most-nested binary boolean functions to be replaced for parameters
    seed : int
        Seed value ensures the same result for the same seed
    loc : str
        Directory to store the networks in

    Returns
    -------
    None
    """
    # change all conjunctions to uninterpreted fncs, or disjunctions
    line = remove_whitespaces(network)
    i = 0

    and_matches = re.findall(r"(<and/><apply><eq/><ci>(\s*\w+\s*)</ci><cn type=\"integer\">\s*1\s*</cn></apply><apply><eq/>"
                         r"<ci>(\s*\w+\s*)</ci><cn type=\"integer\">\s*1\s*</cn></apply>)|"
                         r"(<and/><apply><not/><apply><eq/><ci>(\s*\w+\s*)</ci><cn type=\"integer\">\s*1\s*</cn></apply>"
                         r"</apply><apply><eq/><ci>(\s*\w+\s*)</ci><cn type=\"integer\">\s*1\s*</cn></apply>)|"
                         r"(<and/><apply><eq/><ci>(\s*\w+\s*)</ci><cn type=\"integer\">\s*1\s*</cn></apply><apply><not/>"
                         r"<apply><eq/><ci>(\s*\w+\s*)</ci><cn type=\"integer\">\s*1\s*</cn></apply></apply>)|"
                         r"(<and/><apply><not/><apply><eq/><ci>(\s*\w+\s*)</ci><cn type=\"integer\">\s*1\s*</cn></apply>"
                         r"</apply><apply><not/><apply><eq/><ci>(\s*\w+\s*)</ci><cn type=\"integer\">\s*1\s*</cn>"
                         r"</apply></apply>)", line)
    or_matches = re.findall(r"(<or/><apply><eq/><ci>(\s*\w+\s*)</ci><cn type=\"integer\">\s*1\s*</cn></apply><apply><eq/>"
                         r"<ci>(\s*\w+\s*)</ci><cn type=\"integer\">\s*1\s*</cn></apply>)|"
                         r"(<or/><apply><not/><apply><eq/><ci>(\s*\w+\s*)</ci><cn type=\"integer\">\s*1\s*</cn></apply>"
                         r"</apply><apply><eq/><ci>(\s*\w+\s*)</ci><cn type=\"integer\">\s*1\s*</cn></apply>)|"
                         r"(<or/><apply><eq/><ci>(\s*\w+\s*)</ci><cn type=\"integer\">\s*1\s*</cn></apply><apply><not/>"
                         r"<apply><eq/><ci>(\s*\w+\s*)</ci><cn type=\"integer\">\s*1\s*</cn></apply></apply>)|"
                         r"(<or/><apply><not/><apply><eq/><ci>(\s*\w+\s*)</ci><cn type=\"integer\">\s*1\s*</cn></apply>"
                         r"</apply><apply><not/><apply><eq/><ci>(\s*\w+\s*)</ci><cn type=\"integer\">\s*1\s*</cn>"
                         r"</apply></apply>)", line)
    res = []
    new_content = line
    all_possibilities = 0
    and_or_matches = and_matches + or_matches
    for match in and_or_matches:
        for k in match:
            if len(k) > 0 and k[0] == '<':
                all_possibilities += 1
    # following lines inspired by https://stackoverflow.com/a/19597672
    # this ensures desired number of parameters
    parametrise_arr = numpy.zeros(all_possibilities)
    parametrise = round(float(parametrisation_frac) * all_possibilities)
    parametrise_arr[:parametrise] = 1
    numpy.random.seed(seed)
    numpy.random.shuffle(parametrise_arr)
    for match in and_or_matches:
        for k in match:
            if len(k) > 0 and k[0] == '<':  # filter the false matches
                if parametrise_arr[i]:
                    k = '<root>' + k + '</root>'  # little trick to help the library to work correctly
                    response = ET.fromstring(str(k))
                    for child in response:  # searching for children
                        for other in child:
                            if other.tag == 'ci':
                                res.append(other.text)
                            for foo in other:
                                if foo.tag == 'ci':
                                    res.append(foo.text)
                    new_content = new_content.replace(str(k[6:-7]),
                                                      f"<csymbol>F{i}</csymbol><ci>{res[0]}</ci><ci>{res[1]}</ci>")
                    res = []
        i += 1
    # below is an initial implementation, which is found illegal by windows (meaning windows detects a virus),
    # thus a rewrite was necessary
    # with open(f'{loc}parametrised_{path.basename(network)}', 'w') as net:
    # same problem with vvv
    # with open(f'{loc}parametrised_{Path(network).stem}.sbml', 'w') as net:
    # nothing works, windows just detects viruses and I don't understand
    # with open(f'{loc}parametrised_model_{datetime.now().strftime("%m%d%y%H%M%S")}.sbml', 'w') as net:
    base = path.basename(network)
    f_name = path.splitext(base)[0]
    with open(f'{loc}parametrised_{f_name}_f{parametrisation_frac}_s{seed}.sbml', 'w') as net:
        net.write(new_content)


def parse_json(json_file, loc=""):
    """Parses the json containing the configuration for the network generation

    Parameters
    ----------
    json_file
        Configuration file
    loc : str
        Directory to save the network

    Returns
    -------
    1 if the file isn't in valid JSON format, otherwise None
    """
    try:
        with open(json_file, 'r') as js:
            try:
                args = json.load(js)
                seed = args['seed']
                if seed == 'rand':
                    seed = numpy.random.seed(int(time.time()))

                number_of_vertices = args['vertices']
                if number_of_vertices == 'rand':
                    numpy.random.seed(seed)
                    number_of_vertices = numpy.random.randint(low=2, high=1001)  # 1001 off by one

                num_of_networks = args['number of networks']
                if num_of_networks == 'rand':
                    numpy.random.seed(seed)
                    num_of_networks = numpy.random.randint(low=1, high=5)

                frac_of_act_regs = args['fraction of act regs']
                if frac_of_act_regs == 'rand':
                    numpy.random.seed(seed)
                    frac_of_act_regs = round(numpy.random.random(), 1)

                l_arity = args['uninterpreted function arity']['lower bound']
                if l_arity == 'rand':
                    numpy.random.seed(seed)
                    l_arity = numpy.random.randint(low=1, high=5)

                u_arity = args['uninterpreted function arity']['upper bound']
                if u_arity == 'rand':
                    numpy.random.seed(seed)
                    u_arity = numpy.random.randint(low=4, high=9)

                if args['generator']['Barabasi-Albert']['use']:
                    conn = args['generator']['Barabasi-Albert']['connections']
                    if conn == 'rand':
                        numpy.random.seed(seed)
                        conn = numpy.random.randint(2, number_of_vertices - 1)
                    generate_bn(number_of_vertices, seed, num_of_connections=conn, l_bound=l_arity, u_bound=u_arity,
                                frac_reg=frac_of_act_regs, ba=True, loc=loc, n=num_of_networks)

                elif args['generator']['Watts-Strogatz']['use']:
                    conn = args['generator']['Watts-Strogatz']['connections']
                    if conn == 'rand':
                        numpy.random.seed(seed)
                        conn = numpy.random.randint(2, number_of_vertices)
                    probability = args['generator']['Watts-Strogatz']['rewire probability']
                    if probability == 'rand':
                        numpy.random.seed(seed)
                        probability = round(numpy.random.random(), 2)
                    generate_bn(number_of_vertices, seed, num_of_connections=conn,
                                probability=probability, l_bound=l_arity, u_bound=u_arity,
                                frac_reg=frac_of_act_regs, ws=True, loc=loc, n=num_of_networks)

                elif args['generator']['Random Network']['use']:
                    probability = args['generator']['Random Network']['connection probability']
                    if probability == 'rand':
                        numpy.random.seed(seed)
                        probability = round(numpy.random.random(), 2)
                    generate_bn(number_of_vertices, seed, probability=probability,
                                l_bound=l_arity, u_bound=u_arity, frac_reg=frac_of_act_regs,
                                random=True, loc=loc, n=num_of_networks)
            except json.JSONDecodeError:
                print(f"Invalid json file {json_file}")
                exit(1)
    except FileNotFoundError:
        print(f"File \'{json_file}\' not found.", file=stderr)
        exit(1)


# deprecated, still usable tho
if __name__ == "__main__":
    from sys import argv, stderr

    if len(argv) == 2:
        if argv[1].endswith('.json'):
            parse_json(argv[1])
        elif argv[1].endswith('.sbml'):
            modify_network(argv[1], parametrisation_frac=0.5, seed=int(time.time()))
        else:
            print(f"{argv[1]} is neither a json nor an smbl file.")
            exit(1)
        print("Network generated successfully!")
        exit(0)
    elif argv[1] not in ['ba', 'ws', 'rand']:
        raise ValueError(f"{argv[1]} isn't a supported model of a network")
    check_number_of_vertices(argv[2])
    if argv[1] == 'ba':
        check_num_of_connections(argv[3], 1)  # check if number of edges per vertex is reasonable
        generate_bn(int(argv[2]), seed=int(argv[4]), num_of_connections=int(argv[3]), ba=True)
    elif argv[1] == 'ws':
        check_num_of_connections(argv[3], 2)
        check_probability_argument_for_ws(argv[4])
        generate_bn(int(argv[2]), seed=int(argv[5]), num_of_connections=int(argv[3]),
                    probability=round(float(argv[4]), 2), ws=True)
    elif argv[1] == 'rand':
        check_probability_argument(argv[3])
        generate_bn(int(argv[2]), seed=int(argv[4]), probability=round(float(argv[3]), 2), random=True)
    print("Network generated successfully!")
