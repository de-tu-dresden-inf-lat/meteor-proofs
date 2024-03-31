from meteor_reasoner.classes.rule import *
from meteor_reasoner.materialization.ground import *
from meteor_reasoner.classes.term import Term
from collections import defaultdict
from meteor_reasoner.materialization.index_build import build_index
from meteor_reasoner.utils.operate_dataset import print_dataset
from meteor_reasoner.materialization.coalesce import coalescing_d
from meteor_reasoner.materialization.ifCD import ifCD,isCD


def naive_join(rule, D, delta_new, D_index=None, must_literals=None, graph=None):
    """
    This function implement the join operator when variables exist in the body of the rule.
    Args:
        rule (a Rule instance):
        delta_new (a dictionary object): store new materialized results.
        D (a dictionary object): a global variable storing all facts.
        common_fragment: Canonical Representation related

    Returns:
        None
    """
    head_entity = rule.head.get_entity()
    head_predicate = rule.head.get_predicate()
    literals = rule.body + rule.negative_body


    def ground_body(global_literal_index, delta, context):
        if global_literal_index == len(literals):
            T = []
            # dnh: For atoms in body rule
            outermost_literals = defaultdict(list)
            # dnh: For atoms/literals in nested inside temporal operators with the first level of nesting is simply an atom
            nested_literals = defaultdict(list)
            '''
            dnh: Go through all the literals in the body of the rule and apply MTL ops to literals
            '''
            for i in range(len(rule.body)):
                # Exchange variable with constant
                grounded_literal = copy.deepcopy(literals[i])
                if isinstance(grounded_literal, BinaryLiteral):
                    grounded_literal.set_entity(delta[i])
                else:
                    if grounded_literal.get_predicate() not in ["Bottom", "Top"]:
                        grounded_literal.set_entity(delta[i][0])
                
                if not isCD(grounded_literal.get_predicate()):
                # Operators are popped here
                    if graph is not None:
                        t = apply(grounded_literal, D, outermost_literals=outermost_literals, nested_literals=nested_literals)
                    else:
                        t = apply(grounded_literal, D)
                # dnh: grounded literals satisfy the body of the rule at times t
                # i.e: head rule can be deduced at times t
                else:
                     if ifCD(grounded_literal.get_predicate(),delta[i][0]):
                         t = [Interval(float('-inf'), float('inf'), True, True)]
                     else:
                         t = []
                if len(t) == 0:
                    break
                else:
                    T.append(t)
                    if must_literals is not None:
                        must_literals[grounded_literal] += t
            n_T = []
            for i in range(len(rule.body), len(literals)):
                grounded_literal = copy.deepcopy(literals[i])
                if isinstance(grounded_literal, BinaryLiteral):
                    grounded_literal.set_entity(delta[i])
                else:
                    if grounded_literal.get_predicate() not in ["Bottom", "Top"]:
                        grounded_literal.set_entity(delta[i][0])

                t = apply(grounded_literal, D)
                if len(t) == 0:
                    break
                else:
                    n_T.append(t)
                    if must_literals is not None:
                        must_literals[grounded_literal] += t

            if len(n_T) > 0 and len(n_T) == len(rule.negative_body_atoms):
                n_T = interval_merge(T)
            else:
                n_T = []

            try:
                if len(head_entity) > 1 or head_entity[0].name != "nan":
                    replaced_head_entity = []
                    for term in head_entity:
                        if term.type == "constant":
                            replaced_head_entity.append(term)
                        else:
                            if term.name not in context:
                                raise ValueError("Head variables in Rule({}) do not appear in the body".format(str(rule)))
                            else:
                                new_term = Term.new_term(context[term.name])
                                replaced_head_entity.append(new_term)
                    replaced_head_entity = tuple(replaced_head_entity)
                else:
                    replaced_head_entity = head_entity
            except:
                 print("Head variables in Rule({}) do not appear in the body")
                 print(rule)

            # If all literals appear in some time interval (T)
            if len(T) == len(literals):
                # dnh: 26/05 new rule for interval merge intersection rule generalization
                # og_len = len(T)
                T = interval_merge(T)
                exclude_t = []
                if len(T) != 0 and len(n_T) != 0:
                    exclude_t = interval_merge([T, n_T])
                if len(exclude_t) != 0:
                    T = Interval.diff(T, exclude_t)
                # If all literals appear TOGETHER in some time interval (T)
                # after_merge_len = len(T)
                # if after_merge_len >  og_len:
                #     print("Og and after merge len: ", og_len, after_merge_len)
                if len(T) != 0:
                    if graph is not None:
                        # Add nested rules to graph
                        if len(nested_literals) != 0:
                            def do_profile_1():
                                for lit, rs in nested_literals.items():
                                    succ = lit.__str__()
                                    for r in rs:
                                        el = {}
                                        el["succ"] = {
                                            "alpha": succ,
                                            "interval": r["interval"].__str__()
                                        }
                                        el["rule"] = r["rule"]
                                        el["pred"] = { k: v.__str__() for k,v in r.items() if k not in ["interval", "rule"] }
                                        graph.append(el)
                            do_profile_1()
                        def do_profile_2():
                            for interval in T:
                                el = defaultdict(list)
                                # Succ
                                # if isinstance(rule.head, Atom):
                                if rule.head.get_op_name() is None:
                                    a_succ = Atom(head_predicate, entity=replaced_head_entity, interval=interval).__str__()
                                else:
                                    alpha = copy.deepcopy(rule.head)
                                    alpha.set_entity(replaced_head_entity)
                                    a_succ = { "alpha": alpha.__str__(), "interval": interval.__str__() }

                                el["succ"] = a_succ
                                el["rule"] = rule.__str__()
                                for lit, intvs in outermost_literals.items():
                                    # Pred
                                    for intv in intvs:
                                        # Intermediate step
                                        if isinstance(intv, dict):
                                            s_intv = Interval.inclusion(interval, intv['interval'])
                                            if s_intv:
                                                a_pred = lit.__str__()
                                                # if intv["rule"] in ["until", "since"]:
                                                #     r_str = {k: v.__str__() for k, v in intv.items()}
                                                #     el["pred"].append(r_str)
                                                # else:
                                                el["pred"].append({ "alpha": a_pred, "interval": intv["interval"].__str__() })
                                        else:
                                            s_intv = Interval.inclusion(interval, intv)
                                            if s_intv:
                                                a_pred = Atom(lit.get_predicate(), entity=lit.get_entity(), interval=intv).__str__()
                                                el["pred"].append(a_pred)
                                graph.append(el)
                        do_profile_2()

                    if not isinstance(rule.head, Atom):
                        # Remark: Was wrong, already rewrote this
                        tmp_head = copy.deepcopy(rule.head)
                        tmp_head.set_entity(replaced_head_entity)

                        if must_literals is not None:
                            must_literals[tmp_head] += T

                        nested_literals = defaultdict(list)
                        # T = reverse_apply(tmp_head, tmp_D, nested_literals=nested_literals)
                        tmp_T = copy.deepcopy(T)
                        T = reverse_apply(tmp_head, tmp_T, nested_literals=nested_literals)
                        if graph is not None:
                            def do_profile_3():
                                for lit, rs in nested_literals.items():
                                    for intv in rs:
                                        el = {}
                                        if intv['alpha'].get_op_name() is None:
                                            a_succ = Atom(intv['alpha'].get_predicate(), entity=intv['alpha'].get_entity(), interval=intv['interval']).__str__()
                                        else:
                                            a_succ = {
                                                    "alpha": intv['alpha'].__str__(),
                                                    "interval": intv['interval'].__str__()
                                            }
                                        el["succ"] = a_succ
                                        el["rule"] = intv['rule']
                                        el["pred"] = { "alpha": lit.__str__(), "interval": intv["roh_1"].__str__() }
                                        graph.append(el)
                            do_profile_3()

                    delta_new[head_predicate][replaced_head_entity] += T
                    # dnh: Used only in some experiments
                    if must_literals is not None:
                        must_literals[Atom(head_predicate, replaced_head_entity)] += T

        else:
            current_literal = copy.deepcopy(literals[global_literal_index])
            # If NOT until/since
            if not isinstance(current_literal, BinaryLiteral):
                # If bottom, top no context needed (exchanged var)
                if current_literal.get_predicate() in ["Bottom", "Top"]:
                    ground_body(global_literal_index+1, delta, context)
                # Else do go through each const to exchange with var
                else:
                    # Generate entity(const) and contexts(exchanged var) from the dataset
                    for tmp_entity, tmp_context in ground_generator(current_literal, context, D, D_index):
                        # Dict of exchanged var/const {literal_index: [consts]}
                        tmp_delata = {global_literal_index: [tmp_entity]}
                        ground_body(global_literal_index+1, {**delta, **tmp_delata}, {**context, **tmp_context})
            # If until/since
            else:
                left_predicate = current_literal.left_literal.get_predicate()
                right_predicate = current_literal.right_literal.get_predicate()

                if left_predicate in ["Bottom", "Top"]:
                    for tmp_entity, tmp_context in ground_generator(current_literal.right_literal, context,  D, D_index):
                        tmp_delta = {global_literal_index: [tmp_entity]}
                        ground_body(global_literal_index + 1, {**delta, **tmp_delta}, {**context, **tmp_context})

                elif right_predicate in ["Bottom", "Top"]:
                    for tmp_entity, tmp_context in ground_generator(current_literal.left_literal, context, D, D_index):
                        tmp_delta = {global_literal_index: [tmp_entity]}
                        ground_body(global_literal_index + 1, {**delta, **tmp_delta}, {**context, **tmp_context})

                else:
                    for left_entity, tmp_context1 in ground_generator(current_literal.left_literal, context, D):
                        for right_entity, tmp_context2 in ground_generator(current_literal.right_literal.atom,{**context, **tmp_context1}, D):
                            tmp_delta = {global_literal_index: [left_entity, right_entity]}
                            ground_body(global_literal_index + 1, {**delta, **tmp_delta}, {**context, **tmp_context1, **tmp_context2})

    ground_body(0, {}, dict())


if __name__ == "__main__":
    D = defaultdict(lambda: defaultdict(list))
    D["A"][tuple([Term("mike"), Term("nick")])] = [Interval(3, 4, False, False), Interval(6, 10, True, True)]
    D["B"][tuple([Term("nan")])] = [Interval(2, 8, False, False)]
    D["P"][tuple([Term("a")])] = [Interval(1, 1, False, False)]
    D_index = build_index(D)

    Delta = defaultdict(lambda: defaultdict(list))
    head = Atom("C", tuple([Term("nan")]))
    literal_a = Literal(Atom("A", tuple([Term("Y", "variable"), Term("X", "variable")])),
                        [Operator("Boxminus", Interval(1, 2, False, False))])
    literal_b = Literal(Atom("B", tuple([Term("nan")])), [Operator("Diamondminus", Interval(0, 1, False, False))])

    body = [literal_a, literal_b]

    new_literal = BinaryLiteral(Atom("A", tuple([Term("X", "variable"), Term("Y", "variable")])),
                                Atom("B", tuple([Term("nan")])), Operator("Since", Interval(1, 2, False, False)))
    body.append(new_literal)
    literal_p = Literal(Atom("P", tuple([Term("X", "variable")])),
                        [Operator("Diamondminus", Interval(1, 1, False, False))])
    head_p = Atom("P", tuple([Term("X", "variable")]))

    rule = Rule(head_p, [literal_p])
    i = 0
    delta_old = D
    while i < 5:
        i += 1
        delta_new = defaultdict(lambda: defaultdict(list))
        naive_join(rule, D=D, delta_new=delta_new, D_index=D_index)
        print("new:")
        print_dataset(delta_new)
        for predicate in delta_new:
            if predicate not in D:
                D[predicate] = delta_new[predicate]
            else:
                for entity in delta_new[predicate]:
                    D[predicate][entity] = D[predicate][entity] + delta_new[predicate][entity]
        coalescing_d(D)
        delta_old = delta_new











