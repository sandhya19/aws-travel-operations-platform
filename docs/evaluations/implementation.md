# AI evaluation

Golden datasets define expected citations and reference answers. Regression tests score
groundedness, faithfulness, latency, and citation accuracy. Prompt versions are compared
by groundedness plus citation accuracy; each run is stored in `evaluation_history`.
