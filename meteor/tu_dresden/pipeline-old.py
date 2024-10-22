import sys
sys.path.append('../')

from meteor_reasoner.utils.hypergraph_parser import HyperGraphParser
from meteor_reasoner.materialization.index_build import *
from meteor_reasoner.materialization.coalesce import *
from meteor_reasoner.utils.loader import load_dataset, load_program
from meteor_reasoner.utils.parser import parse_str_fact
from meteor_reasoner.classes import *
from meteor_reasoner.utils.entail_check import entail
from meteor_reasoner.utils.operate_dataset import yield_dataset
from meteor_reasoner.materialization.materialize import materialize
import cProfile
import time
import argparse
import json
import os
import io
import pstats

parser = argparse.ArgumentParser()
parser.add_argument("--facts", default="10000", type=str, help="Input the dataset path")
parser.add_argument("--rulepath", default="programs/p.txt", type=str, help="Input the program path")
parser.add_argument("--glassbox", default="1", type=str, help="Do Glassbox tracing")
parser.add_argument("--profile", default="0", type=str, help="Do profiling")

args = parser.parse_args()

nr_facts = args.facts
do_profile = args.profile

data_path_relative = f"output/{nr_facts}.txt"
current_path = os.path.dirname(os.path.realpath(__file__))
data_path = os.path.join(current_path, data_path_relative)

with open(args.rulepath) as file:
    rules = file.readlines()
    program = load_program(rules)

try:
    fact_path = f"data/T4_{nr_facts}.txt"
    with open(fact_path, "r") as file:
        fact = file.readlines()[0].strip()

    predicate, entity, interval = parse_str_fact(fact)
    F = Atom(predicate, entity, interval)
except:
    raise Exception("The format you input is incorrect")

glassbox = args.glassbox


"""
    LOADING
"""
LOADING_START = time.perf_counter()
if glassbox == "1":
    graph = []
    D = load_dataset(data_path, graph=graph)
else:
    D = load_dataset(data_path)
    graph = None
    print("The graph is None")
entail(F, D, graph=graph)
coalescing_d(D, graph=graph)
D_index = build_index(D)
LOADING_END = time.perf_counter()
LOADING_TIME = LOADING_END - LOADING_START


def run():
    if entail(F, D, graph=graph):
        return True
    else:
        while True:
            flag = materialize(D, rules=program, mode="naive", K=1, graph=graph, fakt=F)
            if entail(F, D, graph=graph):
                return True
            else:
                if flag:
                    return False


"""
    REASONING
"""
REASONING_START = time.perf_counter()
if do_profile == "1":
    pr = cProfile.Profile()
    pr.enable()
    entailment = run()
    if glassbox == "1" and entailment:
        parser = HyperGraphParser(graph)
        parser.initialization()
        file_name = data_path_relative.split(".")[0]
        parser.write_to_file_as_json("{}.json".format(file_name))
    pr.disable()
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('tottime')
    ps.print_stats()
    with open("profile.txt", "a") as f:
        f.write(f"========= {nr_facts} =========\n {s.getvalue()}")
else:
    entailment = run()
REASONING_END = time.perf_counter()
REASONING_TIME = REASONING_END - REASONING_START

"""
    PARSING
"""
PARSING_START = time.perf_counter()
if glassbox == "1" and entailment and do_profile == "0":
    parser = HyperGraphParser(graph)
    parser.initialization()
    file_path = f"json_1/{nr_facts}.json"
    parser.write_to_file_as_json(file_path)
PARSING_END = time.perf_counter()
PARSING_TIME = PARSING_END - PARSING_START

TOTAL_TIME = PARSING_TIME + REASONING_TIME + LOADING_TIME
print("========= RESULT =========")
print("Total time: ", TOTAL_TIME)

if glassbox == "1":
    with open("trace_time.txt", "a") as f:
        f.write(f"{nr_facts} : {LOADING_TIME} : {REASONING_TIME} : {PARSING_TIME} : {TOTAL_TIME} : {len(graph)} : {len([*yield_dataset(D)])} : {len(parser.edges)}\n")
else:
    with open("time.txt", "a") as f:
        f.write(f"{nr_facts} : {LOADING_TIME} : {REASONING_TIME} : {PARSING_TIME} : {TOTAL_TIME}\n")
