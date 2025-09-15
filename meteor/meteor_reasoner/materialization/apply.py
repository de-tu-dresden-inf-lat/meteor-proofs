from meteor_reasoner.classes.literal import *
from meteor_reasoner.classes.interval import *
from meteor_reasoner.classes.atom import *
import copy


def since_deduce(literal, left_interval, right_interval):
    """
    Calculate the ``Since'' operator .
    Args:
        literal (a BinarayLiteral instance):
        left_interval (an Interval instance):
        right_interval (an Interval instance):
    Returns:
        a Interval instance or None
    """
    if not literal.operator.interval.left_open and literal.operator.interval.left_value == 0:
        return Interval.add(right_interval, literal.operator.interval)

    # calculate S
    closed_left_interval = copy.copy(left_interval)
    closed_left_interval.left_open = False
    closed_left_interval.right_open = False

    s_interval = Interval.intersection(closed_left_interval, right_interval)
    if s_interval is None:
        return None

    # calculate T satisfying the right literal
    t_interval = Interval.add(s_interval, literal.operator.interval)

    # calculate T satisfying the left literal
    interval = Interval.intersection(t_interval, closed_left_interval)
    if interval is None:
        return None
    else:
        return interval


def until_deduce(literal, left_interval, right_interval):
    """
    Calculate the ``Until'' operator .
    Args:
        literal (a BinarayLiteral instance):
        left_interval (an Interval instance):
        right_interval (an Interval instance):

    Returns:
        a Interval instance or None
    """
    if not literal.operator.interval.left_open and literal.operator.interval.left_value == 0:
        return Interval.sub(right_interval, literal.operator.interval)

    # calculate S
    closed_left_interval = copy.copy(left_interval)
    closed_left_interval.left_open = False
    closed_left_interval.right_open = False

    s_interval = Interval.intersection(closed_left_interval, right_interval)
    if s_interval is None:
        return None

    # calculate T satisfying the right literal
    t_interval = Interval.sub(s_interval, literal.operator.interval)

    # calculate T satisfying the left literal
    interval = Interval.intersection(t_interval,closed_left_interval)
    if interval is None:
        return None
    else:
        return interval

def apply(literal, D, delta_old=None, graph=None):
    """
    Apply MTL operator(s) to a literal.
    Args:
        literal (Literal BinaryLiteral Instance):
        D (defaultdict):

    Returns:
        A list of Interval instances.
    """

    if not isinstance(literal, BinaryLiteral) and (isinstance(literal, Atom) or
                                                   len(literal.operators) == 0):
        # If no temporal ops
        predicate = literal.get_predicate()
        entity = literal.get_entity()
        if entity:
            if predicate in D and entity in D[predicate]:
                if delta_old is not None and predicate in delta_old and entity in delta_old[predicate]:
                    full_intervals = copy.deepcopy(D[predicate][entity])
                    for remove_interval in delta_old[predicate][entity]:
                        full_intervals.remove(remove_interval)
                    return full_intervals
                # Always land here
                else:
                    T = D[predicate][entity]

                    return T
            else:
                return []

        else:
            if predicate in D:
                return D[predicate]
            else:
                return []
    else:
        op_name = literal.get_op_name()
        if op_name in ["Until", "Since"]:
            left_literal = literal.left_literal
            right_literal = literal.right_literal

            if left_literal.get_predicate() == "Bottom" or right_literal.get_predicate() == "Bottom":
                raise ValueError("It is not allowed to have the bottom predicate in the left side "
                                 "or the right side of a binary literal ")
            if left_literal.get_predicate() == "Top":
                T1 = [Interval(float('-inf'), float('inf'), True, True)]
            else:
                T1 = apply(left_literal, D, graph=graph)

            if right_literal.get_predicate() == "Top":
                T2 = [Interval(float('-inf'), float('inf'), True, True)]
            else:
                T2 = apply(right_literal, D, graph=graph)

            T = []
            if op_name == "Until":
                if T1 and T2:
                    for t1 in T1:
                        for t2 in T2:
                            t = until_deduce(literal, t1, t2)
                            if t:
                                T.append(t)
                                if graph is not None:
                                    graph.extend((literal, t), "until", (left_literal, t1), (right_literal, t2))
            else:
                if T1 and T2:
                    for t1 in T1:
                        for t2 in T2:
                            t = since_deduce(literal, t1, t2)
                            if t:
                                T.append(t)
                                if graph is not None:
                                    graph.extend((literal, t), "since", (left_literal, t1), (right_literal, t2))

            return T

        else:
            # Find out where the atom behind the operator occurs in D
            pop_operator = literal.operators.pop(0)
            # dnh 02/06 Nested temporal operators
            T0 = apply(literal, D, graph=graph)
            # assume that TO is sorted
            for i in range(1, len(T0)):
                assert T0[i-1].left_value < T0[i].left_value, f"Intervals {T0[i-1]} and {T0[i]} are not sorted"
            inner_literal = copy.deepcopy(literal)
            literal.operators.insert(0, pop_operator)
            # To support nested temporal operators, op are appended and name collapsed
            literal_copy = copy.deepcopy(literal)
            T = []
            if op_name == "Diamondminus":
                for t0 in T0:
                  interval = Interval.add(t0, literal.operators[0].interval)
                  if Interval.is_valid_interval(interval.left_value, interval.right_value,
                                                interval.left_open, interval.right_open):
                      T.append(interval)
                      if graph is not None:
                        graph.extend((literal_copy, interval), "diamondminus", (inner_literal, t0))
            elif op_name == "Boxminus":
                for t0 in T0:
                  interval = Interval.circle_add(t0, literal.operators[0].interval)
                  if Interval.is_valid_interval(interval.left_value, interval.right_value,
                                                interval.left_open, interval.right_open):
                      T.append(interval)
                      if graph is not None:
                        graph.extend((literal_copy, interval), "boxminus", (inner_literal, t0))

            elif op_name == "Diamondplus":
                for t0 in T0:
                  interval = Interval.sub(t0, literal.operators[0].interval)
                  if Interval.is_valid_interval(interval.left_value, interval.right_value,
                                                interval.left_open, interval.right_open):
                      T.append(interval)
                      if graph is not None:
                        graph.extend((literal_copy, interval), "diamondplus", (inner_literal, t0))

            elif op_name == "Boxplus":
                for t0 in T0:
                  interval = Interval.circle_sub(t0, literal.operators[0].interval)
                  if Interval.is_valid_interval(interval.left_value, interval.right_value,
                                                interval.left_open, interval.right_open):
                      T.append(interval)
                      if graph is not None:
                        graph.extend((literal_copy, interval), "boxplus", (inner_literal, t0))

            elif op_name == "Diamondc":
                if len(T0) > 0:
                    limit = literal.operators[0].interval
                    T = [T0[0]]
                    if graph is not None:
                        graph.extend((literal_copy, T0[0]), "diamondc", (inner_literal, T0[0]))
                    for i in range(1, len(T0)):
                        prev = T[-1]
                        curr = T0[i]
                        gap = curr.left_value - prev.right_value
                        if gap < limit or (not curr.left_open and not prev.right_open and gap == limit):
                            merged = Interval(prev.left_value, curr.right_value, prev.left_open, curr.right_open)
                            if graph is not None:
                                graph.extend((literal_copy, merged), "diamondc", (literal_copy, prev), (inner_literal, curr))
                            T[-1] = merged
                        else:
                            T.append(curr)
                            if graph is not None:
                                graph.extend((literal_copy, curr), "diamondc", (inner_literal, curr))

            elif op_name == "Boxc":
                for t0 in T0:
                    l = t0.right_value - t0.left_value
                    limit = literal.operators[0].interval
                    if l > limit or (not t0.left_open and not t0.right_open and l == limit):
                        T.append(t0)
                        if graph is not None:
                            graph.extend((literal_copy, t0), "boxc", (inner_literal, t0))

            else:
                raise ValueError("{} is an illegal MTL operator name!".format(op_name))

            return T


def reverse_apply(literal, outer_T, graph=None):
    """
    Apply MTL operator(s) to a literal.

    Args:
        literal (Literal BinaryLiteral Instance):
        D (defaultdict):

    Returns:
        A list of Interval instances.
    """
    if isinstance(literal, Atom) or len(literal.operators) == 0:
        return outer_T

    else:
        op_name = literal.get_op_name()
        pop_operator = literal.operators.pop(0)
        # inner atom IS HEAD
        alpha = copy.deepcopy(literal)
        # inner atom holds at some T0
        literal.operators.insert(0, pop_operator)
        # original
        literal_copy = copy.deepcopy(literal)
        T = []
        if op_name == "Boxplus":
            for t0 in outer_T:
              # dnh: Remark: Translate to since with A1 = T
              interval = Interval.add(t0, literal.operators[0].interval)
              if Interval.is_valid_interval(interval.left_value, interval.right_value,
                                            interval.left_open, interval.right_open):
                  T.append(interval)
                  if graph is not None:
                      graph.extend((alpha, interval), "reverse_boxplus", (literal_copy, t0))

        elif op_name == "Boxminus":
            for t0 in outer_T:
              interval = Interval.sub(t0, literal.operators[0].interval)
              if Interval.is_valid_interval(interval.left_value, interval.right_value,
                                            interval.left_open, interval.right_open):

                  T.append(interval)
                  if graph is not None:
                      graph.extend((alpha, interval), "reverse_boxminus", (literal_copy, t0))

        else:
            raise ValueError("{} is an illegal MTL operator name!".format(op_name))
        T0 = reverse_apply(alpha, T, graph=graph)

        return T0


if __name__ == "__main__":
    from collections import defaultdict
    from meteor_reasoner.classes import Term
    from meteor_reasoner.materialization.index_build import build_index

    D = defaultdict(lambda: defaultdict(list))
    D["A"][tuple([Term("mike"), Term("nick")])] = [Interval(3, 4, False, False), Interval(6, 10, True, True)]
    D["B"][tuple([Term("nan")])] = [Interval(2, 8, False, False)]
    D_index = build_index(D)
    literal_a = Literal(Atom("A", tuple([Term("mike"), Term("nick")])), [Operator("Boxminus", Interval(1, 2, False, False))])
    literal_b = Literal(Atom("A", tuple([Term("mike"), Term("nick")])), [Operator("Diamondminus", Interval(1, 2, False, False))])
    bi_literal_a = BinaryLiteral(Atom("A", tuple([Term("mike"), Term("nick")])),
                               Atom("B", tuple([Term("nan")])), Operator("Since", Interval(1, 2, False, False)))
    bi_literal_b = BinaryLiteral(literal_a, literal_b, Operator("Since", Interval(1, 2, False, False)))

    t1 = apply(literal_a, D)
    for t in t1:
        print(t)
    print("end")
    t2 = reverse_apply(literal_a, D)
    for t in t2:
        print(t)
    print("end")
    t3 = apply(bi_literal_a, D)
    for t in t3:
        print(t)
    print("end")
    t4 = apply(bi_literal_b, D)
    for t in t4:
        print(t)
    print("end")



