for name in {"test/0","test/1","test/2","test/3"} #$all
do
    printf "\n TEST $name \n"
    python3 pipeline.py --drone $name
#done
#for name in "easy/4/c" #$all
##do
#    in_data_dir="drones/ds/$name.json"
#    out_graph_dir="drones/NLGexamples/$name/graph.svg"
#    out_proof_dir="drones/NLGexamples/$name/proof.svg"
#    out_json_dir="drones/NLGexamples/$name/proof.json"
#    java -jar proof_extractor.jar $in_data_dir $out_graph_dir $out_proof_dir > $out_json_dir
done
