from meteor_reasoner.classes.interval import *
from meteor_reasoner.classes.atom import *

def entail(fact, D, graph=None):
    if fact.predicate not in D:
        return False
    else:
        if not fact.entity in D[fact.predicate]:
            return False
        else:
            intervals = D[fact.predicate][fact.entity]
            for interval in intervals:
                if Interval.inclusion(fact.interval, interval):
                    if graph is not None:
                        atom = Atom(fact.predicate, fact.entity)
                        graph.extend((atom, fact.interval), "inclusion", (atom, interval))
                        graph.set_conclusion = (atom, fact.interval)
                    return True
            else:
                return False
