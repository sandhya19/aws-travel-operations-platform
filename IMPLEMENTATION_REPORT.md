# Implementation Report — IMP-002, IMP-003, and IMP-012

## Objective

Deliver a development vertical slice for authenticated travel-request submission,
CockroachDB persistence, EventBridge delivery, Step Functions approval, and completion.
Also verify the API transaction lifecycle required by IMP-002 and the duplicate-safe
workflow-start behavior required by IMP-012.

## Design decisions

- Persist request state and a workflow outbox event before publishing to EventBridge.
- Resolve database credentials and the CockroachDB root certificate from AWS Secrets
  Manager at Lambda startup. The certificate is written only to `/tmp` for TLS use.
- Use a Standard Step Functions callback task for human approval.
- Start workflows through a Lambda adapter using the outbox event ID as the execution name.
- Treat an existing Standard Step Functions execution for the same outbox event as a
  successful duplicate delivery.
- Bound outbox publication to three attempts and route exhausted events to the encrypted
  SQS DLQ using only recovery identifiers and failure context.
- Lock selected outbox rows so concurrent dispatchers do not process an event simultaneously.
- Require the `travel:approve` role for approval requests.

## Files modified

- Application: `database.py`, API/auth/service/repository modules, event publication,
  outbox dispatcher, and workflow starter.
- Database: Alembic migrations through `0006`.
- Infrastructure: the dev vertical slice, EventBridge module, environment variables, and
  Secrets Manager wiring.
- Tests: transaction lifecycle, API contracts, auth, secret resolution, workflow, and
  migration-lineage tests.
- Documentation: `docs/architecture/api.md` and this report.

## Database migrations

- `0001`–`0004`: travel requests, knowledge/evaluation tables, and approval tasks.
- `0005_workflow_outbox_events`: durable workflow publication outbox.
- `0006_outbox_retries_and_approval_audit`: outbox retry metadata and immutable approval
  decisions.

## Terraform changes

- Added KMS-encrypted Secrets Manager storage for the CockroachDB root certificate.
- Added runtime secret ARNs and least-privilege `GetSecretValue`/`kms:Decrypt` permissions
  to the API, workflow, and outbox Lambdas.
- Added the outbox dispatcher and workflow starter Lambdas.
- Added the dispatcher DLQ URL and narrowly scoped `sqs:SendMessage` permission.
- Routed custom-bus travel events to the workflow starter and scheduled the dispatcher on
  the default EventBridge bus every minute.
- Added Lambda permissions for both EventBridge invocations and Step Functions failure
  transitions.

## New AWS resources

- `travel-operations-dev/cockroach-root-cert` Secrets Manager secret.
- Outbox-dispatcher and workflow-starter Lambda functions with execution roles.
- Default-bus EventBridge schedule and target for outbox dispatch.
- Lambda permissions for EventBridge invocation.
- IAM inline policies for KMS decrypt, Secrets Manager reads, EventBridge publication,
  and Step Functions execution.

## New CockroachDB tables/indexes

- `workflow_outbox_events`, indexed by `(status, created_at)`.
- `approval_decisions` for attributed approval history.
- Existing `approval_tasks` remains indexed by `(travel_request_id, status)`.

## Tests added

- Database URL/Secrets Manager resolution contract.
- Approver-role authorization.
- Session commit, rollback, and close lifecycle.
- Service commit delegation and API commit-before-publication contract.
- Workflow definition and KMS/Secrets Terraform contracts.
- Workflow-starter execution-name and duplicate-delivery contracts.
- Outbox-dispatcher success and retry contracts.
- Exhausted outbox-retry DLQ routing and Terraform/IAM environment contracts.
- Failed-event requeue command contracts.
- Migration lineage contracts for revisions through `0006`.

## Test coverage

- Targeted IMP-002 tests passed: 5 tests.
- Full Python execution passed: 31 tests.
- Terraform initialization, formatting checks for modified files, validation, planning, and
  multiple dev applies passed.
- The submit-to-approval path was manually completed in the deployed dev environment.
- A controlled AWS exercise verified a failed outbox event reached `FAILED` after three attempts,
  emitted one sanitized SQS DLQ message, was requeued with `scripts/requeue_outbox_event.py`,
  republished, and started its deterministic Step Functions execution.
- The recovered workflow was approved through the authenticated API (HTTP 202); CockroachDB
  recorded `APPROVED` and `COMPLETED`, and the matching Step Functions execution succeeded.

This report does **not** claim that all required quality or production tests passed.
The complete suite was not rerun after every final packaging/deployment change. Ruff,
Black, MyPy, load testing, fault injection, automated cloud E2E coverage, and a real
duplicate-delivery/DLQ recovery exercise remain incomplete.

## Performance impact

Human approval is asynchronous; request submission does not wait for an approver. The
outbox dispatcher runs once per minute for failed publications. No load, latency, or
cost benchmark has been performed.

## Security impact

- Database URL and CockroachDB root certificate are held in KMS-encrypted Secrets Manager
  secrets.
- Lambda retrieves the certificate through the AWS API and writes it only to `/tmp`.
- Approval now requires the `travel:approve` JWT role.
- The current JWT secret remains a Lambda environment variable; it has not yet been moved
  to runtime Secrets Manager retrieval.

## Cost impact

The dev stack now adds Secrets Manager storage and a one-minute EventBridge/Lambda
dispatcher invocation. No budget alarm or measured cost model exists.

## Documentation updated

- API transaction and outbox ordering in `docs/architecture/api.md`.
- This implementation report.

## Known limitations

- The outbox dispatcher uses bounded attempts but has no time-based backoff or alert threshold.
- Duplicate workflow starts are unit-tested. The exhausted retry/DLQ recovery path has been
  exercised in AWS, but automated cloud E2E coverage remains absent.
- Approval callback delivery is not a distributed transaction with Step Functions.
- The project has no automated, recorded cloud E2E test, DLQ exercise, or recovery drill.
- Terraform state is local; remote state and CI promotion controls are absent.
- The root certificate is supplied to Terraform from a local file during deployment.

## Remaining work

1. Add scripted or automated cloud E2E coverage for authenticated submission, approval, and
   completion.
2. Add CockroachDB migration and repository integration tests against an isolated database.
3. Make Ruff, Black, MyPy, security scanning, and coverage required CI gates.
4. Add operational alerts for outbox failures, DLQ growth, Lambda errors, and approval delay.
5. Move JWT secret retrieval to Secrets Manager and add rotation.
