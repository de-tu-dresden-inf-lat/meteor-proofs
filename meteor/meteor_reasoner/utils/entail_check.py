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
                        atom = Atom(fact.predicate, entity=fact.entity, interval=interval)
                        el = {
                            "succ": fact.__str__(),
                            "rule": "inclusion",
                            "pred": atom.__str__(),
                        }
                        graph.append(el)
                    return True
            else:
                return False
