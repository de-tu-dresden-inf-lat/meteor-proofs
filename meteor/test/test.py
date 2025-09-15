import sys
sys.path.append('./')

from meteor_reasoner.utils.hypergraph import HyperGraph
from meteor_reasoner.materialization.index_build import *
from meteor_reasoner.materialization.coalesce import *
from meteor_reasoner.utils.loader import load_dataset, load_program
from meteor_reasoner.utils.parser import parse_str_fact
from meteor_reasoner.classes import *
from meteor_reasoner.utils.operate_dataset import print_dataset
from meteor_reasoner.materialization.materialize import materialize
import os

current_path = os.path.dirname(os.path.realpath(__file__))
do_profile = False

rulepath = os.path.join(current_path, f"test.mtl")
data_path = os.path.join(current_path, f"test.dat")

with open(rulepath) as file:
    rules = file.readlines()
    program = load_program(rules)
    for rule in program:
        print(rule)

graph = HyperGraph()
D = load_dataset(data_path, graph=graph)
F = Atom(*parse_str_fact("E(a)@[37,37]"))
i = -1
print(F)

while True:
    i = i + 1
    print("#####")
    print(i)
    print_dataset(D)
    if materialize(D, rules=program, mode="seminaive", graph=graph, fact=F):
        break

file_name = os.path.join(current_path, f"test.json")
graph.write_to_file_as_json(file_name)

# TODO: final conclusion
