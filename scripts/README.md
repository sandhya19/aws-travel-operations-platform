# Scripts

Reserved for reviewed developer and operational automation. Scripts must be
idempotent, documented, and safe to run.

`replay_approved_callback.py <request-id>` resumes a Step Functions approval callback only from
the matching durable approved checkpoint. See `docs/runbooks/README.md` before using it.

`evaluate_prompt_release.py --prompt-id <id> --answers-file <file>` evaluates a candidate answer
set against the active prompt release's linked golden dataset and exits non-zero when either release
gate fails.

`benchmark_workflow.py` runs a bounded, authenticated deployed workflow benchmark and emits
sanitized latency/throughput JSON. `compare_kpi_benchmarks.py` compares two successful benchmark
JSON files. `validate_dr_evidence.py` validates non-sensitive CockroachDB restore-drill evidence;
it does not perform a backup or restore.

`build_lambda_package.py` creates the deployable API archive from the prepared Linux dependency
directory and the current `src/travel_operations` source tree. Rebuild it whenever API or service
code changes, including the interactive itinerary API; do not manually copy source into `dist`.
