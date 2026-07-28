# Evaluation framework

Evaluation assets will live under `evaluations/`, with approved regression examples in
`evaluations/golden_datasets/`. Each suite must define data provenance, expected output,
metrics, acceptance threshold, and version.

Required metrics will include groundedness, faithfulness, latency, hallucination rate,
answer relevance, and citation accuracy. Framework implementation is deferred to
Milestone 9.
