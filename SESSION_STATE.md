# Session state

**Last updated:** 2026-08-07

## Completed

Milestone 0 initialized the production-oriented monorepo scaffold. Milestone 1 added
reusable Terraform modules for the AWS platform boundaries, documentation, examples,
and development environment network composition. No application code was added.

IMP-001 repaired the Alembic revision chain by adding `0002_knowledge_chunks`; `0003`
evaluation history now has a resolvable predecessor. Lineage and revision-contract tests
were added.

IMP-002 made the travel-request repository lifecycle transaction-safe: request sessions
commit on success, roll back on failure, and close deterministically.

IMP-003 is deployed to the approved `eu-west-2` development account. It adds the
`TravelRequestCreated` EventBridge integration, a Standard Step Functions callback
approval workflow, SQS dead-letter queue, approval-task persistence migration `0004`,
and API approval endpoint. The deployed OpenAPI endpoint returned HTTP 200.
The callback state now stores its result under `$.approval`, preserving the original
EventBridge detail for the completion task.

IMP-012 now bounds outbox publication attempts. After three failures, the event is marked
`FAILED` and a minimal recovery message is written to the encrypted SQS DLQ. Concurrent
dispatchers skip locked events. The retry and DLQ Terraform contracts, unit tests, and deployed
AWS recovery exercise pass: a failed event was requeued, republished, and started its
idempotent Step Functions execution.

The API Lambda receives `JWT_SECRET` from a sensitive development Terraform variable. This
enables authenticated API calls; migrate it to Secrets Manager before production use.

## Current milestone

IMP-012 is complete. IMP-003's deployed recovery path was exercised through an authorized
approval: the API returned HTTP 202, CockroachDB recorded `APPROVED` and `COMPLETED`, and the
idempotent Step Functions execution succeeded. A scripted authenticated request-submission
test and demo evidence remain open.

## Next authorized work

Add the scripted authenticated request-submission test and demo evidence for IMP-003 before
starting the next implementation milestone.
