# CockroachDB × AWS Hackathon Review

## Executive Summary

> Historical baseline: this review predates the implemented IMP-001/002/003/004/012 vertical
> slice and the IMP-006/007 memory and provenance foundations. Its findings about broken migrations, uncomposed
> Terraform, unsafe request-session handling, absent approval history, and no deployable
> workflow are no longer current. Its findings about incomplete agent execution, memory
> provenance/replay, runtime RAG, CI gates, and operational evidence remain current.

**Historical score: 31/100.** This baseline predates the now-demonstrable request-to-approval
vertical slice. The current repository should be assessed against the remaining gaps: durable
memory is only a foundation, and agent execution, RAG, replay, CI gates, and operational proof
are still needed before it can contend for a final round.

## Detailed Rubric

| Category | Score /10 | Strict assessment |
| --- | ---: | --- |
| Agentic Memory Design | 1 | CockroachDB holds request metadata and proposed vectors, not durable agent memory. |
| Technical Implementation | 4 | FastAPI, SQLAlchemy, Terraform and RAG foundations exist; integration is incomplete/broken. |
| Real World Impact | 6 | Corporate travel operations is a real, expensive enterprise problem. |
| Product Readiness | 2 | No working vertical slice, deployment proof, demo, or operational evidence. |
| Creativity and Originality | 4 | Sensible established patterns; no demonstrated differentiator. |

## Agentic Memory Review

| Capability | Score /10 | Finding |
| --- | ---: | --- |
| Conversation, user, tool, planning, reasoning memory | 0 | No schemas, writes, or retrieval paths. |
| Task memory | 1 | Travel requests are metadata, not durable agent tasks. |
| Approval history | 0 | No approval table or immutable decision record. |
| Embeddings/context retrieval | 2 | Vector query exists, but table/migration path and integration are incomplete. |
| Consolidation, pruning, expiration | 0 | No lifecycle management. |
| Versioning | 1 | Ingestion attempts a content hash only. |
| Checkpointing, state recovery, replay | 0 | No persisted workflow/agent checkpoints. |
| Multi-session continuity/shared memory/learning | 0 | Absent. |
| Durability/indexing/search | 2 | CockroachDB could provide this, but memory model is absent. |

CockroachDB is **not acting as long-term agent memory**. The agent file contains static
specifications; the Lambda tool only returns a placeholder response. Build append-only
`agent_memory_events`, `agent_sessions`, `tool_executions`, `approval_decisions`, and
`workflow_checkpoints` tables, all keyed by tenant/user/correlation ID, with provenance,
retention, ACL filtering, replay, and vector/metadata search.

## Technical Review

### Strengths

- Human approval is explicitly a required business stage.
- CockroachDB, EventBridge, Step Functions, KMS/Secrets, RAG, and Terraform are sensible choices.
- Repository layout, ADRs, prompt paths, golden-dataset seed, and SQLAlchemy pooling show good intent.

### Weaknesses and Critical Issues

1. **Broken database migration lineage:** `0003_evaluation_history.py` depends on `0002`, which is absent. `alembic upgrade head` cannot succeed.
2. **No deployable composition:** dev Terraform creates networking only. API, Lambda, EventBridge, SQS, Step Functions, KMS/Secrets, and Bedrock modules are not wired together.
3. **Placeholder workflow:** ASL uses `${...LambdaArn}` tokens and has retry only on validation, no broad Catch strategy, no tested DLQ path, and no deployed state machine.
4. **IAM is not least privilege:** the IAM module creates only an assume-role policy; no required resource policies are attached.
5. **RAG/ingestion are not production-safe:** raw vector SQL assumes missing schema, no tenant/metadata filtering, no ACLs, no chunk provenance lifecycle, and no failure handling. The PDF ingestion service directly creates clients, repeats text extraction, lacks size/MIME/malware checks, and has no tests.
6. **Agent integration is absent:** no Bedrock Agent resources/action groups, typed tools, tool permissions, executions, or evaluations.
7. **API persistence is risky:** request dependency uses `next(session_scope())`, bypassing proper generator cleanup/transaction lifecycle.

## Production Review

| Area | Verdict |
| --- | --- |
| Single points of failure | No proven multi-region topology, HA policy, or workflow recovery. |
| Security | Helpers for masking/injection exist but are not integrated into API, RAG, or ingestion paths. |
| Audit/compliance | Audit is log-only; no durable immutable audit record, retention, consent, or tenant isolation. |
| Observability | Dashboard is minimal; no alarms, SLOs, traces, synthetic checks, or incident runbooks. |
| DR/backup | No Cockroach backup/restore strategy, RPO/RTO, restore drill, or document recovery plan. |
| Cost/scaling | No Bedrock quota/cost guardrails, concurrency limits, vector index plan, or load test. |
| Deployment | Terraform Apply uses `-auto-approve` without remote state, OIDC, policy gates, or promoted plan artifacts. |

For a Fortune 500 deployment, add least-privilege policies, OIDC, KMS key policies,
Secrets rotation, WAF/rate limits, tenant isolation, DLP, encryption evidence, backups,
regional DR, alarms for auth/KMS/secret/DLQ failures, and periodic access reviews.

## AI and Travel Industry Review

Prompt files are versioned by filename but lack ownership, model configuration, schemas,
release gates, rollback evidence, and evaluated versions. The single golden case is not a
benchmark. “Faithfulness” currently aliases token-overlap groundedness; citation parsing
is simplistic. There is no confidence score, fallback strategy, enforced Bedrock
Guardrail, or real tool orchestration.

Travel impact is plausible, but missing functions include HR/cost-center integration,
traveler profiles, policy rules by grade/country, GDS/airline/hotel booking, visa and
duty-of-care providers, expense/card integration, rebooking, delegated approval,
reporting, localization, accessibility, and policy/compliance administration.

## Test Review

Only basic unit tests exist for a placeholder tool, helper metrics, package import, and
security helpers. Missing: API/auth tests; Cockroach integration and migration tests;
transaction/retry tests; S3/PDF/Titan mocks; RAG precision/recall/citation tests; prompt
and agent regressions; EventBridge/Step Functions contracts; e2e flows; load/benchmark;
chaos; security/DLP; Terraform validate/plan/policy; Docker smoke; backup/restore tests.

Add Testcontainers CockroachDB migration tests, LocalStack/AWS sandbox contracts, pytest
API tests, fake Bedrock/S3 fixtures, ASL validation, k6 load tests, fault injection,
OWASP authorization tests, RAG benchmark datasets, and CI gates for `tflint`, `checkov`,
Terraform plans, coverage, and migration upgrades.

## Risk Register

| Risk | Severity | Required mitigation |
| --- | --- | --- |
| Missing Alembic revision | Critical | Repair history; test upgrade/downgrade in CI. |
| No end-to-end product | Critical | Deliver one API-to-approval vertical slice. |
| No agent memory | Critical | Implement replayable CockroachDB memory model. |
| PII in PDFs/embeddings | Critical | DLP, consent, ACLs, retention, encryption, deletion. |
| Placeholder IAM/workflow | High | Compose resource policies and deploy tested integrations. |
| No DR/alerts | High | Define RPO/RTO, restore drills, dashboards, alarms. |

## Prioritized Implementation Roadmap

1. **Days 1–2:** repair migrations; deploy request → CockroachDB → EventBridge → Step Functions → human approval → completion; provide a reproducible demo.
2. **Days 3–4:** make CockroachDB the differentiator with durable agent/session/tool/approval memory, checkpointing, replay, cross-session retrieval, provenance, pruning, and tenant ACLs.
3. **Days 5–6:** add real Bedrock action groups, citation RAG, policy/visa/risk adapters, quality evaluations, security controls, and failure/DLQ behavior.
4. **Day 7:** prove it with migration/e2e/load/security tests, backup restore, dashboard/alarms, live demo video, and quantified operator-time reduction.

## Hackathon Recommendation

**Final round:** unlikely. **Top 3:** no. **Winner:** no.

**Estimated winning probability: under 2%.** The concept can become competitive, but it
must demonstrate a working vertical slice and a distinctive CockroachDB-backed durable
agent-memory system. More scaffold files will not change the outcome; integration,
evidence, reliability, and a compelling live demo will.
