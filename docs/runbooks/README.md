# Runbooks

Runbooks provide safe, repeatable operational procedures. Do not include credentials or
sensitive values.

## Dev travel workflow recovery

**Trigger:** a travel request remains pending after EventBridge publication, or an outbox event
reaches `FAILED` after its bounded retries.

**Prerequisites:** AWS SSO credentials for the dev account, the dev Terraform outputs, and a
database connection that resolves through the configured Secrets Manager entries.

1. Identify the request and outbox event IDs from the API audit logs or CockroachDB.
2. Inspect the `travel-operations-dev-travel-events` SQS DLQ for the matching, sanitized
   recovery message.
3. Correct the external delivery cause before retrying. Do not replay an event whose request is
   already completed.
4. Run `python scripts/requeue_outbox_event.py --event-id <event-id>` with the normal dev
   database environment. This resets only the failed event to its safe pending state.
5. Verify the EventBridge dispatcher publishes the event and that the deterministic Step
   Functions execution starts. Approve it only through the authenticated API endpoint.

**Verification:** the outbox event is `PUBLISHED`, the request reaches `COMPLETED`, and the
corresponding Step Functions execution succeeds.

**Escalation:** if the event fails again, leave it in the DLQ, preserve the sanitized failure
context, and investigate Lambda, EventBridge, and Secrets Manager logs. The product owner owns
approval of any manual database repair.

## Approved callback replay

**Trigger:** an approver decision is durable, but `SendTaskSuccess` failed before Step Functions
could resume the waiting execution.

1. Verify that the travel request is not `COMPLETED` and that the failure was limited to the
   callback delivery.
2. Run `python scripts/replay_approved_callback.py <request-id>` with normal AWS and database
   credentials.
3. Verify that the Step Functions execution resumes and the request reaches `COMPLETED`.

The command refuses to run unless the latest durable checkpoint is `APPROVAL_APPROVED` and the
approval task remains approved. Do not use it for rejected, pending, or completed requests.

## Dev recovery drill

Enable the failure injection only in the dev Terraform environment:

```bash
terraform -chdir=terraform/environments/dev apply \
  -var='simulate_approval_callback_failure=true'
```

Create and approve a fresh test request. The approval endpoint returns HTTP 503 only after the
approval decision and checkpoint commit. Verify it remains incomplete, then run
`python scripts/replay_approved_callback.py <request-id>` and verify completion. Disable the
switch immediately after the exercise:

```bash
terraform -chdir=terraform/environments/dev apply \
  -var='simulate_approval_callback_failure=false'
```

## Operations alarms and bounded load test

The dev Terraform stack creates a CloudWatch operations dashboard and alarms for Lambda and Step
Functions failures, DLQ depth, API authentication/client-error signals, API p99 latency, and KMS
key errors. Confirm the optional SNS email subscription before relying on notifications.

For a controlled load exercise, use `scripts/benchmark_workflow.py` first with five requests and
one worker. Do not increase concurrency while any error, DLQ, latency, or KMS alarm is active.
Preserve only the sanitized benchmark JSON and CloudWatch window; it contains no bearer tokens.

When an alarm fires, record the timestamp/correlation ID, inspect CloudWatch and X-Ray, and use
the narrowest recovery action: investigate and replay an approved callback, or requeue a reviewed
failed outbox event. Never manually mutate completed requests.

## Disaster recovery

Use the dedicated [CockroachDB disaster-recovery drill](disaster-recovery.md) to prove an isolated
restore. It defines the 60-minute RPO and 120-minute RTO, required durable-table count checks, and
evidence validation. A backup configuration alone is not restore proof.
