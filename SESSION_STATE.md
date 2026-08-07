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
`FAILED` and a minimal recovery message is written to the encrypted SQS DLQ. The retry and
DLQ Terraform contracts and unit tests pass; the deployed AWS recovery exercise remains open.

The API Lambda receives `JWT_SECRET` from a sensitive development Terraform variable. This
enables authenticated API calls; migrate it to Secrets Manager before production use.

## Current milestone

IMP-012 is in progress. Repository-side bounded retry/DLQ support is complete; AWS delivery
and recovery evidence remains required before it can be marked complete.

## Next authorized work

Refresh the AWS SSO session, apply the changed development Terraform, and exercise failed
publication through DLQ recovery. Then complete IMP-003's authenticated cloud E2E/demo
evidence before starting the next implementation milestone.
