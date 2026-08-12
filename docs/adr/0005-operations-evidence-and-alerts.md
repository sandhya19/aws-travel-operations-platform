# ADR 0005: Keep operational evidence outside the request path

## Status

Accepted — 2026-08-12

## Decision

The dev environment provisions CloudWatch alarms and an encrypted SNS topic for failure, DLQ,
API client/authentication, latency, and KMS signals. A bounded synthetic benchmark, checkpoint
failure/replay drill, and CockroachDB isolated-restore runbook collect operational evidence without
adding work to the request API or workflow state machine.

## Consequences

- Existing public APIs and human-approval behavior remain unchanged.
- Alarm email delivery is opt-in and requires AWS SNS confirmation.
- Restore proof remains an operator-controlled CockroachDB Cloud procedure; source control stores
  only a non-sensitive template and validation logic, never backup credentials or evidence PII.
- The development SLOs are evidence targets, not a production availability commitment.
