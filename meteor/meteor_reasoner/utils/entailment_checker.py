from meteor_reasoner.canonical.utils import find_periods
from meteor_reasoner.canonical.canonical_representation import CanonicalRepresentation
from meteor_reasoner.utils.loader import load_dataset, load_program
from meteor_reasoner.utils.parser import parse_str_fact
from meteor_reasoner.classes.atom import Atom
from meteor_reasoner.canonical.utils import fact_entailment
from meteor_reasoner.utils.operate_dataset import print_dataset

def entailment_check_without_load(dataset, program, fact, glassbox=False):
    CR = CanonicalRepresentation(dataset, program, glassbox=glassbox)
    CR.initilization()
    D1, common, varrho_left, left_period, left_len, varrho_right, right_period, right_len = find_periods(CR)
    entailment = fact_entailment(D1, fact, common, left_period, left_len, right_period, right_len, graph=CR.G)
    if glassbox and entailment:
        return CR.G

    return entailment

def entailment_check(data, program, fact, glassbox=False):
    D = load_dataset(data)
    Program = load_program(program)

    CR = CanonicalRepresentation(D, Program, glassbox=glassbox)
    CR.initilization()

    D1, common, varrho_left, left_period, left_len, varrho_right, right_period, right_len = find_periods(CR)
    try:
        predicate, entity, interval = parse_str_fact(fact)
        FAKT = Atom(predicate, entity, interval)
    except:
        raise ("The format you input is not correct")

    entailment = fact_entailment(D1, FAKT, common, left_period, left_len, right_period, right_len, graph=CR.G)

    # if varrho_left is None and varrho_right is None:
    #     print("This program is finitely materialisable for this dataset.")
    # else:
    #     if varrho_left is not None:
    #         print("left period:", str(varrho_left))
    #         for key, values in left_period.items():
    #             print(str(key), [str(val) for val in values])
    #     else:
    #         print("left period:", "[" + str(CR.base_interval.left_value - CR.w) + "," + str(CR.base_interval.left_value), ")")
    #
    #     if varrho_right is not None:
    #         print("right period:", str(varrho_right))
    #         for key, values in right_period.items():
    #             print(str(key), [str(val) for val in values])
    #     else:
    #         print("right period:", "(" + str(CR.base_interval.right_value), "," +  str(CR.base_interval.right_value + CR.w) + "]")

    # print("Entailment:", entailment)

    if glassbox and entailment:
        # for el in CR.G:
        #     print(el["succ"], ":", el["rule"], ":", el["pred"])
        #     print("====================================")
        return CR.G

    return entailment



