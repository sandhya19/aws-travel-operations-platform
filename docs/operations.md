# Operational evidence and service objectives

## Development SLOs

The development environment is intentionally small and has no production traffic commitment. Its
synthetic operating targets are: no visible workflow-DLQ messages, no failed Step Functions
executions, zero Lambda errors during a benchmark, API p99 latency below 3 seconds, RPO of 60
minutes, and RTO of 120 minutes. These targets are acceptance gates for the hackathon evidence,
not a claim of a production availability SLA.

## CloudWatch operations view

Terraform creates the `${project}-${environment}-operations` dashboard and an encrypted SNS topic.
It alarms on Lambda and Step Functions failures, DLQ depth, API 4XX client/authentication signals,
API p99 latency, and KMS key errors. An optional `operations_alert_email` Terraform variable adds
an email subscription; AWS requires the recipient to confirm it before notifications are delivered.

On an alarm, preserve the alarm timestamp and correlation ID, inspect CloudWatch and X-Ray, then
use the relevant recovery procedure in [the runbooks](runbooks/README.md). A 4XX alarm is a
screening signal rather than proof of an attack: separate expected validation errors from rejected
authentication/authorization requests in the API access logs.

## Load, fault, and recovery evidence

`scripts/benchmark_workflow.py` runs the existing authenticated create/approve/complete journey
with a deliberately bounded number of dev samples. Begin with five sequential requests and only
increase to five concurrent requests after the dashboard remains healthy. It prints no tokens or
request payloads; store the JSON results in an evidence location outside the repository.

The existing callback-failure drill is the approved fault injection. It proves the approval is
durable before the callback failure and that the checkpoint-gated replay completes the same
request. The drill must be switched off immediately after recovery. See
[Dev recovery drill](runbooks/README.md#dev-recovery-drill).

## KPI comparison and cost evidence

Run the same bounded workload twice: label the current human-governed workflow `baseline`; label
the approved AgentCore-assisted policy-tool workflow `assisted` only when both runs exercise a
comparable completed business journey. Compare the two JSON results with
`scripts/compare_kpi_benchmarks.py`. The comparison reports success, p95 latency, and throughput
deltas without treating degraded latency as a benefit.

Record the CloudWatch window, request count, benchmark JSON, and an AWS Cost Explorer export for
the same period. Attribute AI cost only to actual Bedrock/AgentCore usage; do not infer model cost
from a mocked or non-model workflow. This keeps the hackathon KPI claim evidence-based.
