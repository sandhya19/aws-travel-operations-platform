# Session state

**Last updated:** 2026-08-12

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

IMP-005 moves the API JWT signing secret to a dedicated KMS-encrypted Secrets Manager entry.
The Lambda receives only its ARN and resolves the value at runtime; local development retains
the ignored `JWT_SECRET` environment variable.

IMP-006 has started. Revision `0007` adds tenant-scoped `agent_sessions` plus append-only
`agent_memory_events`, correlated to each travel request. The active workflow now records
request submission, approval requested, approval decision, and completion in that durable
history. An authenticated requester can retrieve the ordered history at
`GET /travel-request/{request_id}/memory`. This is the memory foundation only; agent tools,
plans, checkpoints/replay, lifecycle, and cross-session retrieval are not yet implemented.

IMP-007 has started. Revision `0008` adds immutable `agent_plans` and `tool_executions`.
Submitting a request records the deterministic validation/approval/completion plan. The Lambda
action-group handler records a completed tool invocation only when Bedrock supplies a valid
travel-request session attribute; duplicate invocation IDs are idempotent. No live Bedrock agent
or LLM reasoning trace exists yet.

IMP-008 has started. Revision `0009` adds idempotent durable checkpoints after validation,
approval wait, approval decision, and completion. Operator replay automation and a cloud
failure/resume exercise remain outstanding.

IMP-010 has started. Revision `0010` gives each travel-case session a retention expiry. A daily
dev lifecycle Lambda marks only terminal sessions expired and records immutable expiry evidence;
it does not physically delete data.

IMP-011 is complete. Revision `0011` adds a non-null `tenant_id` to travel requests, backfills
existing rows to the backwards-compatible `default` tenant, and indexes tenant/requester/status.
Authenticated request, memory, approval, and approval-history operations use that tenant filter;
the action-group handler requires tenant and user session attributes before it records provenance.

IMP-013 is complete. Revision `0012` adds immutable tenant-owned knowledge-document versions and
tenant/page metadata for chunks. A private, KMS-encrypted S3 bucket invokes a scoped Lambda that
accepts only tenant-prefixed PDFs after metadata, size, signature, encryption, prompt-injection,
and Titan embedding-dimension checks; the ingestion is idempotent by tenant, source key, and hash.

IMP-014 is complete. Revision `0013` adds document-role ACL metadata. Retrieval filters vectors by
tenant and role before similarity ranking, then the grounded-answer service accepts only citations
for the retrieved document/chunk/version. Prompt and deterministic citation regression tests cover
the versioned citation contract.

IMP-015 is complete. Because this account cannot create new Bedrock Agents during the AWS service
maintenance mode, the development Terraform composition uses an AgentCore Runtime direct-code
coordinator and a typed `lookup_policy` Lambda tool instead. Invocation records remain scoped to
the tenant/user travel-case session and are persisted as durable tool provenance.

IMP-016 is complete. The grounded-answer service now returns `INSUFFICIENT_EVIDENCE` below a
minimum authorized retrieval score of `0.75`, and `SAFE_FALLBACK` for generation or citation
validation failures. Terraform includes a baseline Bedrock Guardrail with non-sensitive blocked
input/output messages and a required input-only `PROMPT_ATTACK` policy. The Guardrail has been
applied in development; no current service invokes a generation model, so runtime Guardrail
enforcement awaits a model-backed answer endpoint.

IMP-017 is complete. `prompts/releases.json` governs the active `rag_grounded_answer` `v2`
template, owner, model assumption, linked golden dataset, groundedness/citation release gates, and
reviewed `v1` rollback. The registry rejects missing templates/datasets, invalid gates, and invalid
release status.

IMP-018 is complete. `scripts/evaluate_prompt_release.py` evaluates a candidate answer map against
the active release's registered golden dataset, rejects missing/extra cases, and exits non-zero when
aggregate groundedness or citation accuracy misses either configured release gate. The checked-in
v2 baseline passes the deterministic benchmark.

IMP-019 is complete. The reusable dev workflow runner now returns completion evidence for both the
demo and an opt-in `RUN_CLOUD_E2E=1` pytest test against `DEV_API_URL`. Database persistence tests
remain opt-in behind `RUN_DATABASE_INTEGRATION=1`; default CI now triggers on push and pull request
and keeps external integration/cloud tests safely skipped without their explicit environments.

Milestone 4 operational implementation is ready for dev execution. IMP-020 adds a bounded
concurrent workflow benchmark and documents the existing checkpoint replay as the approved fault
drill. IMP-021 adds Terraform-managed CloudWatch alarms/dashboard and an encrypted SNS topic.
IMP-022 adds an isolated CockroachDB restore runbook and evidence validator with 60-minute RPO and
120-minute RTO targets. IMP-023 adds a baseline-versus-assisted latency/throughput comparison.
No live load, alarm, restore, or KPI evidence is recorded in this repository; those exercises need
the dev AWS/CockroachDB operator and must not be represented as passed before execution. The
callback-failure recovery drill has been exercised and the development SNS subscription has been
confirmed; retain redacted evidence outside the repository unless it is safe and reproducible to
commit.

The AgentCore Runtime now acts as a centralized itinerary coordinator. For a saved tenant-scoped
travel request it delegates fixed profile, policy/compliance, risk, inventory research, itinerary,
and financial-triage specialist calls. Each delegation is persisted as CockroachDB tool provenance
and memory history. The present specialists are intentionally non-autonomous: policy/risk require
human review and the itinerary is a non-booking draft.

The public dev API now exposes `POST /itineraries` for the hackathon demonstration. A customer
submits destination, dates, purpose, travelers, budget, currency, and interests once. The
coordinator persists profile, policy/compliance, risk, inventory research, itinerary, and financial
triage outputs to the travel-case memory/tool provenance, returns a non-booking draft, then routes
the travel case through the existing human approval workflow.

The dev Terraform state was migrated from local files to the versioned, private, SSE-KMS S3
backend with DynamoDB locking. The backend uses the dedicated
`alias/travel-operations-terraform-state` KMS key.

## Current milestone

The hackathon interaction increment is deployed in development. `POST /itineraries` has been
exercised successfully with a tenant-scoped draft, specialist delegation results, and human approval
requirements. Milestone 4 source implementation is complete; the callback recovery drill and SNS
subscription are complete, while load, alarm, isolated restore, and KPI evidence remain optional
dev operational exercises.
The development AgentCore Runtime was applied and invoked with a valid
tenant/user/travel-request context. Its `lookup_policy` tool created a `COMPLETED` durable
`tool_executions` record and a `tool_execution_completed` CockroachDB memory event. The database
integration suite also passed. The deployed dev demonstration runner creates an authenticated request,
waits for approval, submits an authorized approval, and verifies `COMPLETED`; it was successfully
exercised against the deployed API.

## Current review state

The scripted authenticated dev workflow demonstration has been added and exercised. The current
work is a production-readiness review of the implemented slice; it does not expand the planned
AI or platform scope.

## Pause hand-off

The repository is being prepared for a focused hackathon push. On return, follow the post-pause
finish plan in `IMPLEMENTATION_PLAN.md`: build a simple reviewer UI, record the two-minute
evidence-led demo, then rehearse the documented validation and deployment path. Do not represent
unrecorded DR, load, alarm, or KPI exercises as complete.
