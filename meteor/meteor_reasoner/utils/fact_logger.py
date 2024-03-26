import os

project_path = os.path.dirname(os.path.abspath(__file__))
derived_facts_path = os.path.join(project_path, "../../derived_facts")

fact = {
        "name": "A(a)@1",
        "from": { "rule": "A(X):-B(X)", "facts": ["B(a)@1"]}
}

def write_derived_fact_to_file(derived_fact=fact, file_name="facts.txt"):
    if not os.path.exists(derived_facts_path):
        os.makedirs(derived_facts_path)
    with open(os.path.join(derived_facts_path, file_name), "a") as f:
        f.write(str(derived_fact) + "\n")
        f.close()

if __name__ == "__main__":
    write_derived_fact_to_file()
