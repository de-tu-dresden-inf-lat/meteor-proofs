from meteor_reasoner.classes.interval import *
from meteor_reasoner.classes.atom import *
import copy

def coalescing(old_intervals, predicate=None, entity=None, graph=None):
    if len(old_intervals) == 0:
        return old_intervals
    new_intervals = []
    old_intervals = sorted(old_intervals, key=lambda t: (t.left_value, t.left_open))
    i = 1
    mover = old_intervals[0]
    if graph is not None:
        merged_intervals = []
        is_merged = False
    while i <= len(old_intervals)-1:
        tmp_interval = Interval.union(mover, old_intervals[i])
        if tmp_interval is None:
            # no intersection
            if graph is not None:
                # If resulting atom are from multiple intervals, then write
                if len(merged_intervals) > 1:
                    atom = Atom(predicate, entity=entity, interval=mover)
                    interval_strs = map(lambda x: Atom(predicate, entity=entity, interval=x).__str__(), merged_intervals)
                    el = {
                        "succ": atom.__str__(),
                        "rule" : "coalescing",
                        "pred": [*interval_strs]
                    }
                    # Next iteration starts with interval i
                    merged_intervals = [old_intervals[i]]
                    graph.append(el)
                    is_merged = True
                # Else reset the merged intervals
                else:
                    merged_intervals = []

            new_intervals.append(mover)
            mover = old_intervals[i]
        else:
            if graph is not None and old_intervals[i] not in merged_intervals:
                merged_intervals.append(old_intervals[i])
                # Edge case where first interval can be merged to the second interval, else only merge the i-interval
                if mover == old_intervals[0] and mover not in merged_intervals:
                    merged_intervals.append(mover)
                is_merged = False

            mover = tmp_interval
        i += 1
    new_intervals.append(mover)

    # Edge case where last interval merges
    if graph is not None:
        if not is_merged and len(merged_intervals) > 1:
            atom = Atom(predicate, entity=entity, interval=mover)
            interval_strs = map(lambda x: Atom(predicate, entity=entity, interval=x).__str__(), merged_intervals)
            el = {
                "succ": atom.__str__(),
                "rule" : "coalescing",
                "pred": [*interval_strs]
            }
            merged_intervals = []
            graph.append(el)

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
                new_intervals = coalescing(old_intervals, predicate=predicate, entity=entity, graph=graph)
            else:
                new_intervals = coalescing(old_intervals)
            D[predicate][entity] = new_intervals
