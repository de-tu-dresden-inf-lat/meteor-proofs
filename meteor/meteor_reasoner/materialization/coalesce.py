from meteor_reasoner.classes.interval import *
from meteor_reasoner.classes.atom import *
import copy

def coalescing(old_intervals, atom=None, graph=None):
    if len(old_intervals) == 0:
        return old_intervals
    new_intervals = []
    old_intervals = sorted(old_intervals, key=lambda t: (t.left_value, t.left_open))
    mover = old_intervals[0]
    if graph is not None:
        merged_intervals = {old_intervals[0]}
    for i in range(1, len(old_intervals)):
        tmp_interval = Interval.union(mover, old_intervals[i])
        if tmp_interval is None:
            # no intersection
            if graph is not None:
                if len(merged_intervals) > 1:
                    # If resulting atom is from multiple intervals, then extend the graph
                    graph.extend((atom, mover), "coalescing", *[(atom, x) for x in merged_intervals])
                merged_intervals.clear()

            new_intervals.append(mover)
            mover = old_intervals[i]
        else:
            mover = tmp_interval

        if graph is not None:
            merged_intervals.add(old_intervals[i])
    new_intervals.append(mover)

    # Edge case where last interval merges
    if graph is not None and len(merged_intervals) > 1:
        graph.extend((atom, mover), "coalescing", *[(atom, x) for x in merged_intervals])

    return new_intervals


def coalescing_d(D, graph=None):
    """
    Merge two overlapped intervals into one interval.
    Args:
        D (a dictionary object): store facts.
    Returns:
    """
    for predicate in D:
        for entity, old_intervals in D[predicate].items():
            old_intervals = D[predicate][entity]
            if len(old_intervals) == 0:
                continue
            if graph is not None:
                new_intervals = coalescing(old_intervals, atom=Atom(predicate, entity), graph=graph)
            else:
                new_intervals = coalescing(old_intervals)
            D[predicate][entity] = new_intervals
