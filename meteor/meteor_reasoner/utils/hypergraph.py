from collections import defaultdict
import json

class HyperGraph:
    def __init__(self):
        self.edges = []
        self.conclusion = None

    def extend(self, conclusion, rule_name, *premises):
        self.edges.append(([lit_intv(*premise) for premise in premises], rule_name, lit_intv(*conclusion)))

    def set_conclusion(self, literal, interval):
        self.conclusion = lit_intv(literal, interval)

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

def lit_intv(literal, interval):
    return f"{literal}@{interval}"
