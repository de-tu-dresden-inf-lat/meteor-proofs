## Finding Proofs for Critical Situations Over Sensor Data Streams(Code)


### 1. Introduction:
This repo contains the Java and Python code used for evaluation in "Finding Proofs for Critical Situations Over Sensor Data Streams"

#### Project structure:
``` bash
.
├── LICENSE
├── evee
│   ├── pom.xml
│   ├── proof_output
│   └── src
│       ├── main
│       └── test
└── meteor
    ├── meteor_reasoner
    │   ├── __init__.py
    │   ├── __pycache__
    │   ├── canonical
    │   ├── classes
    │   ├── datagenerator
    │   ├── entailment
    │   ├── graphutil
    │   ├── materialization
    │   ├── stream
    │   ├── utils
    │   └── version.py
    └── tu_dresden
        ├── data
        ├── generate_facts.py
        ├── generate_owl.py
        ├── json_1
        ├── output
        ├── pipeline.py
        ├── programs
        ├── proof_extractor.jar
        ├── results
        └── scripts
```

#### Outlines:
* The **evee** folder contains build information and the Java code for constructing proofs
* **meteor/** contains MeTeoR reasoner's modules:
  * **meteor/meteor_reasoner**: modified code of the original reasoner to enable tracing
  * **meteor/tu_dresden**: Code used in the experiments of the paper

### 2. Experiments:

We follow similar steps for generating temporal data as proposed in the original project of MeTeoR:

1. Download the data generator (UBA) from **SWAT Projects - Lehigh University Benchmark (LUBM)** [website](http://swat.cse.lehigh.edu/projects/lubm/). In particular,
we used [UBA1.7](http://swat.cse.lehigh.edu/projects/lubm/uba1.7.zip).

###### Add package's path to CLASSPATH
```shell
export CLASSPATH="$CLASSPATH:your package path"
```

<span id="datalog"/>

###### Generate owl files
```
==================
USAGES
==================

command:
   edu.lehigh.swat.bench.uba.Generator
      	[-univ <univ_num>]
	[-index <starting_index>]
	[-seed <seed>]
	[-daml]
	-onto <ontology_url>

options:
   -univ number of universities to generate; 1 by default
   -index starting index of the universities; 0 by default
   -seed seed used for random data generation; 0 by default
   -daml generate DAML+OIL data; OWL data by default
   -onto url of the univ-bench ontology
```

We found some naming and storage issues when using the above command provided 
by the official documentation. To provide a more user-friendly way, we 
wrote a script which can be directly used to generate required owl files
by passing some simple arguments. An example is shown as follows,

```python
from meteor_reasoner.datagenerator import generate_owl

univ_nume = 1 # input the number of universities you want to generate
dir_name = "./data" # input the directory path used for the generated owl files.

generate_owl.generate(univ_nume, dir_name)

```
In  **./data**, you should obtain a serial of owl files like below,
```
University0_0.owl 
University0_12.owl  
University0_1.owl
University0_4.owl
.....
```

Then, we need to convert the owl files to datalog-like facts. We also prepare
a script that can be directly used to do the conversion. 
```python
from meteor_reasoner.datagenerator import generate_datalog

owl_path = "data" # input the dir_path where owl files locate
out_dir = "./output" # input the path for the converted datalog triplets

generate_datalog.extract_triplet(owl_path, out_dir)
```
In **./output**, you should see a **./output/data**  containing data
in the form of
```
UndergraduateStudent(ID0)
undergraduateDegreeFrom(ID1,ID2)
takesCourse(ID3,ID4)
undergraduateDegreeFrom(ID5,ID6)
UndergraduateStudent(ID7)
name(ID8,ID9)
......
```

###### Add intervals to datalog data
File path: **meteor/meteor_reasoner/datagenerator/add_intervals.py** 

```
  --datalog_file_path DATALOG_FILE_PATH
  --factnum FACTNUM
  --intervalnum INTERVALNUM
  --unit UNIT
  --punctual            specify whether we only add punctual intervals
  --openbracket         specify whether we need to add open brackets
  --min_val MIN_VAL
  --max_val MAX_VAL
```

For example, to create a dataset containing 10000 facts and each facts has at most 2 intervals, run the following command
```shell

python add_intervals.py --datalog_file_path your_folder/your_datalog_data.txt --factnum 10000 --intervalnum 2

```

In the **datalog/10000.txt**, there should be 10000 facts, each of which is in the form P(a,b)@\varrho, and 
a sample of facts are shown as follows,
```
UndergraduateStudent(ID0)@[1,18]
undergraduateDegreeFrom(ID1,ID2)@[7,18]
takesCourse(ID3,ID4)@[12,46]
undergraduateDegreeFrom(ID5,ID6)@[21,24]
UndergraduateStudent(ID7)@[3,10]
name(ID8,ID9)@[5,22]
```

###### Generate facts for fact entailment
Note: The script *only* generates new facts of the last materialisation round.
Assuming you have a data file containing 10000 facts under **output/10000.txt", to generate facts that are only seen in the 6th round, use:

```shell
python generate_facts.py --facts 10000 --iteration 6

```
The script will write in **data/10000.txt** the facts entailed from the last materialisation round

#### Run the experiment
For simplicity, the script uses the first fact in the **generated.txt** for evaluation
Assuming your data file is under **output/" and the facts for entailment checking in **data/**, to run experiment with tracing enabled, use:

```shell
python pipeline.py --facts 10000 --glassbox 1

```

If tracing is enabled/disabled, the script will write into **trace_time.txt**/**time.txt** a new line of the following format(in second):

``` 
nr of facts | load time | reasoning time | parse time | total time | Size of D after entailment checking | Size of the Parser 
```
