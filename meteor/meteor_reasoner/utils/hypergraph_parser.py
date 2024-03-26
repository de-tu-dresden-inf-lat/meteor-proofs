from collections import defaultdict
import json

class HyperGraphParser:
    def __init__(self, conns):
        self.conns = conns
        self.edges = []
        self.conclusion = None

    def initialization(self):
        # dnh 12/07: BOTTLENECK
        for conn in self.conns:
            rule = conn['rule']
            if rule == "Asserted":
                v = conn['succ']
                self.edges.append((conn["pred"], rule, v))
                # Assuming that dataset does not contain duplicate facts
            else:
                child = vertices_from_entity(conn['succ'])
                parents = vertices_from_entity(conn['pred'])
                if self.conclusion is None and rule == "inclusion":
                    self.conclusion = child[0]
                self.edges.append((parents, rule, child[0]))
                # local_edge = (parents, rule, child[0])
                # if local_edge not in self.edges:
                #     self.edges.append((parents, rule, child[0]))

    # Turn all edges in to string, print out all that contains "Scientist"
    def print_edges(self):
        for edge in self.edges:
            str_edges = str(edge)
            if "doctoralDegreeFrom(ID7087,ID4314)" in str_edges:
                print(str_edges)


    def write_to_file_as_json(self, file_path):
        with open(file_path, 'w') as f:
            json.dump({
                'edges': self.edges,
                'conclusion': self.conclusion
            }, f)


    def write_to_bash(self):
        print(json.dumps({
            'edges': self.edges,
            'conclusion': self.conclusion
        }))


    def read_from_file_as_json(self, file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
            self.edges = data['edges']


def vertices_from_entity(entity):
    vs = []
    if isinstance(entity, dict):
        keys = entity.keys()
        if 'alpha_1' in keys and 'alpha_2' in keys:
            # Entity from binary rule
            for i in range(2):
                alpha = entity[f'alpha_{i+1}']
                interval = entity[f'roh_{i+1}']
                vs.append(generate_string_entity(alpha=alpha, interval=interval))
        elif 'interval' in keys:
            # Entity from literal with interval
            alpha = entity['alpha']
            interval = entity['interval']
            vs.append(generate_string_entity(alpha=alpha, interval=interval))
        else:
            # Entity from unary rule
            alpha = entity['alpha']
            interval = entity['roh_1']
            vs.append(generate_string_entity(alpha=alpha, interval=interval))
    elif isinstance(entity, str):
        # Entity from simple atom
        vs.append(generate_string_entity(entity_string=entity))
    elif isinstance(entity, list):
        # Entity is list of entities
        for e in entity:
            vs += vertices_from_entity(e)
    else:
        raise Exception(f"Unknown entity type: {type(entity)}")

    return vs


def generate_string_entity(alpha=None, interval=None, entity_string=None):
    if entity_string is not None:
        alpha, interval = entity_string.split('@')
        if interval[0] != '[' and interval[0] != '(':
            interval = f"[{interval},{interval}]"

    return f"{alpha}@{interval}"
