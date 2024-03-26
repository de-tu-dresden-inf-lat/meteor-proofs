# from meteor_reasoner.datagenerator import generate_owl
#
# univ_nume = 1 # input the number of universities you want to generate
# dir_name = "./data" # input the directory path used for the generated owl files.
#
# generate_owl.generate(univ_nume, dir_name)

from meteor_reasoner.datagenerator import generate_datalog

owl_path = "data" # input the dir_path where owl files locate
out_dir = "./output" # input the path for the converted datalog triplets

generate_datalog.extract_triplets(owl_path, out_dir)
