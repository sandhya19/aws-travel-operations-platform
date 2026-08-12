# Evaluation framework

Evaluation assets live under `evaluations/`, with approved regression examples in
`evaluations/golden_datasets/` and reviewed baseline candidate answers in `evaluations/baselines/`.
Each suite defines data provenance, expected output, metrics, acceptance threshold, and version.

IMP-018 evaluates every case linked by an active prompt release. A release passes only when its
average groundedness and citation accuracy meet both registry gates and its answers exactly cover
the dataset. Run the current baseline:

```bash
poetry run python scripts/evaluate_prompt_release.py \
  --prompt-id rag_grounded_answer \
  --answers-file evaluations/baselines/rag_grounded_answer.v2.json
```

Groundedness, faithfulness, latency, hallucination rate, answer relevance, and citation accuracy
remain the long-term metric set. This deterministic benchmark currently gates groundedness and
citation accuracy; model latency and qualitative metrics need a deployed generation path.
