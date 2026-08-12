# Implementation Report — Milestone 4 Operational Evidence

## Objective

Implement the remaining Milestone 4 source changes: bounded load/fault/recovery evidence
(IMP-020), operational alarms/dashboard (IMP-021), CockroachDB DR proof procedure (IMP-022), and
cost/latency KPI measurement tooling (IMP-023). Public API and workflow interfaces remain unchanged.

The hackathon interaction increment adds a backwards-compatible `POST /itineraries` API that turns
one authenticated customer requirement into a centralized, durable, non-booking itinerary draft.

## Design decisions

- Reuse the existing authenticated request/approval/completion runner so benchmark and E2E behavior
  cannot drift.
- Keep benchmark concurrency deliberately bounded and exclude tokens, payloads, and error details
  from output.
- Keep restore execution outside Terraform and the request path: CockroachDB backup/PITR is
  operator- and cluster-tier-controlled. Source control contains a non-sensitive template and
  validator, not credentials or restore evidence.
- Add only CloudWatch, SNS, and existing resource metrics; no new runtime framework, datastore, or
  public endpoint is introduced.

## Files modified

- `terraform/environments/dev/operations.tf`, `variables.tf`, and `outputs.tf`
- `scripts/benchmark_workflow.py`, `compare_kpi_benchmarks.py`, `validate_dr_evidence.py`, and
  `scripts/README.md`
- `src/travel_operations/services/itineraries.py`, `src/travel_operations/api/main.py`,
  `src/travel_operations/agent_tools.py`, and `agent_runtime/agent.py`
- `tests/unit/test_operations_evidence.py` and `tests/unit/test_vertical_slice_contract.py`
- `docs/operations.md`, `docs/runbooks/README.md`, `docs/runbooks/disaster-recovery.md`,
  `docs/evidence/dr-drill.template.json`, architecture/security docs, deployment guide, README,
  and ADR 0005
- `IMPLEMENTATION_PLAN.md`, `SESSION_STATE.md`, and `CHANGELOG.md`

## Database migrations

None. The restore drill verifies existing durable tables: `travel_requests`, `agent_sessions`,
`agent_memory_events`, and `tool_executions`.

## Terraform changes

- Encrypted SNS operations-alert topic with an optional confirmed email subscription.
- CloudWatch alarms for Lambda errors, Step Functions failures, DLQ depth, API 4XX client/auth
  signals, API p99 latency, and KMS key errors.
- CloudWatch operations dashboard and outputs for its name and alert-topic ARN.

## New AWS resources

- One SNS topic; zero or one email subscription depending on `operations_alert_email`.
- Nine CloudWatch metric alarms (four Lambda error alarms plus workflow, DLQ, API 4XX, API p99,
  and KMS alarms).
- One CloudWatch dashboard.

## New CockroachDB tables/indexes

None.

## Tests added

- Benchmark success, latency, throughput, and sanitized-failure behavior.
- Interactive itinerary orchestration: six specialist delegations, durable provenance, and an
  explicit non-booking/human-approval result.
- KPI comparison deltas.
- DR evidence success and row-count-mismatch rejection.
- Terraform contract coverage for all required alarm categories and the operations dashboard.

## Test coverage and results

- `py -3.12 -m pytest tests/unit/test_operations_evidence.py tests/unit/test_vertical_slice_contract.py`:
  **12 passed** (one non-fatal existing `.pytest_cache` Windows access warning).
- `py -3.12 -m pytest tests/unit`: **76 passed** (the same non-fatal cache warning).
- Focused itinerary/coordinator/API contracts: **15 passed** (the same non-fatal cache warning).
- `py -3.12 -m pytest tests/integration`: **9 passed, 4 skipped**; skipped tests are the explicit
  database/cloud opt-in suites and require the configured external environments.
- Ruff for the new/changed scripts and tests: **passed**.
- MyPy for the prior operations scripts/tests: **passed**. Full application MyPy remains blocked by
  missing local `boto3`/`mangum` typing packages and pre-existing strict return annotations; it is
  not claimed as a full-project pass.
- `terraform fmt -check -recursive terraform`: **passed**.
- `terraform init -backend=false`: **completed** and initialized the new local SNS module.
- `terraform validate`: source configuration was reported valid during initialization; the separate
  validation then could not refresh the configured AWS SSO credentials because the session proxy
  points at refused `127.0.0.1:9`. This is an environment credential/proxy issue, not a validation
  error in the configuration.
- Black did not complete in this Windows environment (the known local process hang), so full-format
  success is not claimed.
- Live benchmark, alarm delivery, callback-fault replay, and CockroachDB restore have not been run
  from this workspace and are not claimed as passed.

## Performance impact

No request-path latency change. Benchmark work is explicit and bounded; dashboard/alarm metric
collection is asynchronous AWS control-plane monitoring.

## Security impact

Alarm notifications use an existing KMS key and optional explicit SNS confirmation. Benchmarks do
not log bearer tokens, request payloads, or exception content. The DR evidence template excludes
credentials and PII. The API 4XX alarm is documented as a triage signal, not definitive intrusion
detection.

## Cost impact

Adds low-volume CloudWatch dashboard/alarm/SNS costs and small dev workflow invocations only when
an operator runs a benchmark. Actual Bedrock/AgentCore cost remains measured from Cost Explorer;
the implementation does not fabricate a model-cost estimate.

## Documentation updated

Deployment, operations/SLOs, recovery, disaster recovery, architecture, security, ADR, scripts,
README, plan, session state, and changelog have been updated.

## Known limitations

- CockroachDB backup/PITR availability and restore mechanics depend on the deployed CockroachDB
  Cloud tier and must be executed by an authorized operator.
- Central CloudTrail-based IAM/Secrets Manager denial alarms are deliberately out of scope; current
  KMS and API signals are covered by CloudWatch metrics and access-log triage.
- This development benchmark is not a production load certification.

## Remaining work

1. Apply Terraform with valid AWS SSO credentials and confirm the SNS email subscription.
2. Run the bounded baseline/assisted benchmarks and capture CloudWatch/Cost Explorer evidence.
3. Run the existing callback-failure/replay drill and record results.
4. Run the isolated CockroachDB restore drill and validate its evidence JSON.
5. Rebuild and apply the AgentCore Runtime package before demonstrating the itinerary coordinator.
6. Rebuild and apply the Lambda package before demonstrating `POST /itineraries`.
7. If local staged dependency files are unreadable, recreate `dist/lambda-package` from Linux
   wheels before building; the packager now preserves the existing archive until a full new ZIP is
   successfully written.

## Status

The source implementation and local automated contracts are complete. Milestone 4 acceptance is
pending the four external dev exercises above; success is intentionally not claimed until they pass.
