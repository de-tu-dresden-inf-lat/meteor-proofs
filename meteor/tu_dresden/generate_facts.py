from meteor_reasoner.materialization.index_build import *
from meteor_reasoner.materialization.coalesce import *
from meteor_reasoner.utils.loader import load_dataset, load_program
from meteor_reasoner.utils.parser import parse_str_fact
from meteor_reasoner.classes import *
from meteor_reasoner.utils.entail_check import entail
from meteor_reasoner.materialization.materialize import materialize
from collections import defaultdict
import random
import time
import argparse
import json
import os

parser = argparse.ArgumentParser()
parser.add_argument("--facts", default="10000", type=str, help="Input the dataset path")
parser.add_argument("--rulepath", default="programs/p.txt", type=str, help="Input the program path")

parser.add_argument("--iteration", default=5, type=int, help="Input the iteration times")

args = parser.parse_args()

nr_facts = args.facts
iter = args.iteration

data_path_relative = f"output/{nr_facts}.txt"
current_path = os.path.dirname(os.path.realpath(__file__))
data_path = os.path.join(current_path, data_path_relative)
D = load_dataset(data_path)

coalescing_d(D)
D_index = build_index(D)

with open(args.rulepath) as file:
    rules = file.readlines()
    program = load_program(rules)

keys_from_previous_iterations = defaultdict(list)

predicate = "Scientist"
# predicate = "FullProfessor"
selected_facts = []
seen = set()
limit = 10

round = 0
while round < iter:
    materialize(D, rules=program, mode="naive", K=1)
    # If not last iteration, add the keys to the list
    keys = list(D[predicate].keys())
    keys_from_previous_iterations[round].extend(keys)
    for key in keys:
        intervals = D[predicate][key]
        for interval in intervals:
            fact = Atom(predicate, entity=key, interval=interval)
            if round != iter - 1:
                seen.add(fact.__str__())
            else:
                if len(selected_facts) < limit and fact.__str__() not in seen:
                    selected_facts.append(fact.__str__())
                    seen.add(fact.__str__())
                else:
                    break

    round += 1

# Write the selected facts to file in format { round }, { fact } on each line
# with open(f"data/T4_{nr_facts}.txt", "w") as file:
#     for round, fact in selected_facts.items():
#         file.write(f"{round}, {fact}\n")

# all_facts = defaultdict(list)
# for iteration, keys in keys_from_previous_iterations.items():
#     print(f"Keys from iteration {intital_iter - iteration}: {len(keys)}")
#     for key in keys:
#         intervals = D[predicate][key]
#         for interval in intervals:
#             fact = Atom(predicate, entity=key, interval=interval.__str__())
#             all_facts[iteration].append(fact.__str__())

# keys_from_last_round = [key for key in keys if key not in keys_from_previous_iterations]
#
# if len(keys_from_last_round) == 0:
#     print("No new keys found")
#     exit(1)
#
# sampled_keys = random.sample(keys_from_last_round, 1)
#
# for key in sampled_keys:
#     intervals = D[predicate][key]
#     interval = random.choice(intervals)
#     fact = Atom(predicate, entity=key, interval=interval)
#     selected_facts.append(fact.__str__())

with open(f"data/T4_{nr_facts}.txt", "w") as file:
    file.write("\n".join(selected_facts))
