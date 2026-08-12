# AI evaluation

Golden datasets define expected citations and reference answers. `evaluate_prompt_release.py`
requires an answer for every case and calculates aggregate groundedness and citation accuracy.
Prompt releases declare their dataset and minimum groundedness/citation-accuracy gates in
`prompts/releases.json`; both gates must pass before a candidate is eligible. The travel-policy
dataset includes a negative insufficient-evidence case. Each future deployed evaluated run is
stored in `evaluation_history`; this source-controlled benchmark does not yet persist runs.

The reviewed v2 baseline currently passes two cases with aggregate groundedness `0.9167` and
citation accuracy `1.0`; this is deterministic regression evidence, not a claim of live-model
quality.
