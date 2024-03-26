for i in $(seq 1 1 10)
do
  fact_nr=$((i * 10000))
  python3 generate_facts.py --facts $fact_nr --iteration 6
done
