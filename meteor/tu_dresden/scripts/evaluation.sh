for i in $(seq 1 1 10)
do
  fact_nr=$((i * 10000))
  python3 ../pipeline.py --facts $fact_nr --glassbox 0
done

for i in 1
do
  for j in $(seq 1 1 10)
  do
    fact_nr=$((j * 10000))
    in_data_dir="json_$i/$fact_nr.json"
    out_graph_dir="output/$i/graph_$fact_nr.svg"
    out_proof_dir="output/$i/proof_$fact_nr.svg"
    java -jar ../proof_extractor.jar $in_data_dir $out_graph_dir $out_proof_dir
  done
done
