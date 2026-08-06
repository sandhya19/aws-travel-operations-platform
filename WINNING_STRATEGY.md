# Winning Strategy: CockroachDB × AWS Hackathon

## Judge Reality

Judges will score proof, not architecture labels. Today they would see an ambitious
README, partial source files, disconnected Terraform, no verified demo, and no durable
agent-memory implementation. Winning requires one credible end-to-end story: **a travel
operator receives a cited recommendation whose state, tool history, approval decision,
and replayable memory are durably stored in CockroachDB and orchestrated on AWS.**

## Top 25 Improvements

Scores: impact, business value, novelty, CockroachDB, AWS, AI, and agent memory are 1–5;
effort is S/M/L.

| # | Improvement | Impact | Effort | Business | Novelty | CRDB | AWS | AI | Memory |
| ---: | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Deliver one live request-to-human-approval vertical slice | 5 | L | 5 | 3 | 4 | 5 | 4 | 4 |
| 2 | Build durable agent/session/tool/approval memory in CockroachDB | 5 | L | 5 | 5 | 5 | 3 | 4 | 5 |
| 3 | Repair migrations and prove upgrade/rollback in CI | 5 | S | 4 | 1 | 5 | 2 | 1 | 3 |
| 4 | Persist workflow checkpoints and implement replay after failure | 5 | L | 5 | 5 | 5 | 4 | 3 | 5 |
| 5 | Deploy actual Lambda/API/EventBridge/SFN/SQS composition | 5 | L | 4 | 2 | 3 | 5 | 2 | 2 |
| 6 | Implement cited policy RAG with tenant/metadata filtering | 5 | L | 5 | 4 | 5 | 3 | 5 | 4 |
| 7 | Implement a real Bedrock Agent with typed Lambda action groups | 5 | L | 4 | 3 | 3 | 5 | 5 | 4 |
| 8 | Demonstrate immutable, attributed human approvals | 5 | M | 5 | 3 | 5 | 3 | 3 | 4 |
| 9 | Add policy/visa/risk source adapters with confidence/fallbacks | 4 | L | 5 | 3 | 3 | 4 | 5 | 3 |
| 10 | Add quality dashboard from real golden evaluations | 4 | M | 4 | 3 | 4 | 4 | 5 | 3 |
| 11 | Build a polished 2-minute live demo and recorded backup | 5 | M | 5 | 3 | 2 | 4 | 4 | 4 |
| 12 | Add tenant isolation, provenance, and consent to every memory query | 4 | M | 5 | 3 | 5 | 3 | 4 | 5 |
| 13 | Add e2e, migration, RAG, and workflow failure tests | 4 | M | 4 | 2 | 4 | 4 | 4 | 3 |
| 14 | Add Cockroach backup/restore demonstration and RPO/RTO | 4 | M | 4 | 3 | 5 | 3 | 1 | 4 |
| 15 | Implement outbox-to-EventBridge reliability pattern | 4 | M | 4 | 4 | 5 | 5 | 2 | 4 |
| 16 | Add evidence-based cost/latency/performance benchmark | 4 | M | 4 | 2 | 3 | 4 | 4 | 2 |
| 17 | Add secure production identity: OIDC, least privilege, secrets rotation | 4 | M | 5 | 2 | 3 | 5 | 2 | 2 |
| 18 | Add memory consolidation, retention, and deletion policies | 4 | M | 4 | 5 | 5 | 2 | 3 | 5 |
| 19 | Create travel-operations KPI baseline and measured improvement | 4 | M | 5 | 3 | 1 | 1 | 3 | 2 |
| 20 | Implement document ingestion with validation, versioning, and provenance | 4 | M | 4 | 3 | 4 | 4 | 5 | 3 |
| 21 | Add observability: traces, alarms, DLQ and security dashboards | 3 | M | 4 | 2 | 2 | 5 | 2 | 2 |
| 22 | Add a reviewer-friendly seeded sandbox and reset script | 4 | S | 4 | 2 | 3 | 3 | 3 | 3 |
| 23 | Add approval delegation/escalation and policy exceptions | 3 | M | 5 | 3 | 4 | 3 | 3 | 3 |
| 24 | Add vector recall, citation-accuracy, and prompt regression gates | 4 | M | 4 | 3 | 4 | 2 | 5 | 4 |
| 25 | Publish architecture evidence, runbooks, and ADRs from real implementation | 3 | S | 3 | 2 | 3 | 3 | 3 | 3 |

## Top 10 Demo Improvements

1. Demo a real employee request submitted through the API, not a slide.
2. Show CockroachDB records for the request, memory events, tool calls, citations, and approval.
3. Show an injected Lambda/tool failure, retry, DLQ, checkpoint recovery, and replay.
4. Show a policy PDF source, exact retrieved chunks, and cited recommendation.
5. Show approval/rejection by a different authenticated user and immutable audit history.
6. Show the next session retrieving relevant prior approved travel preferences with consent.
7. Show the quality dashboard: citation accuracy, groundedness, latency, and regression trend.
8. Show a CockroachDB restore/checkpoint recovery path, not just a schema screenshot.
9. Quantify time saved versus manual triage on the same travel request.
10. Provide a recorded fallback demo plus a one-command reviewer sandbox.

## Top 10 Architecture Improvements

1. Introduce a CockroachDB transactional outbox for exactly-once-ish event publication.
2. Make the workflow state machine executable with deployed Lambda ARNs, Catch paths, DLQs, and idempotency keys.
3. Add `agent_sessions`, `memory_events`, `tool_executions`, `workflow_checkpoints`, and `approval_decisions` as first-class tables.
4. Use a shared correlation ID across API, database, EventBridge, Step Functions, tool, and audit records.
5. Add tenant/user authorization predicates to every transactional and vector query.
6. Store source/version/chunk/retrieval provenance on every recommendation and memory event.
7. Compose Terraform environments fully with remote state, OIDC, alarms, and explicit module interfaces.
8. Add asynchronous ingestion with S3 events, content validation, deduplication, and poison-message handling.
9. Define a multi-region Cockroach strategy and documented RPO/RTO/restore plan.
10. Separate deterministic policy checks from LLM reasoning and require confidence/fallback rules.

## Top 10 AI Improvements

1. Replace static agent specs with actual Bedrock Agents/action groups and observed executions.
2. Enforce structured outputs, tool schemas, and per-agent authorization.
3. Build a policy/visa/risk golden set large enough to show meaningful regression results.
4. Measure faithfulness with citation entailment, not token overlap.
5. Add retrieval precision/recall, unsupported-claim rate, and citation completeness metrics.
6. Add prompt release metadata: owner, model, parameters, eval gate, rollback version.
7. Implement confidence scoring and “insufficient evidence” fallback behavior.
8. Apply prompt-injection and PII controls at ingestion, retrieval, tool, and output stages.
9. Show multi-agent handoff records backed by durable shared memory.
10. Demonstrate model/cost fallback and Bedrock Guardrails in an actual execution.

## Top 10 CockroachDB Improvements

1. Make CockroachDB the durable agent-memory system rather than only a request store.
2. Repair migration lineage and test schema upgrades, rollbacks, and zero-downtime changes.
3. Add tenant-aware compound indexes for session, user, status, time, and memory type.
4. Build vector + metadata + authorization filtered retrieval with measured recall.
5. Persist append-only decision/tool/reasoning provenance for replay.
6. Add memory versioning, supersession, consolidation, retention, and GDPR deletion workflows.
7. Demonstrate serializable transaction retries and idempotency under duplicate events.
8. Use an outbox/inbox model for reliable EventBridge consumption/publication.
9. Demonstrate backup, restore, and point-in-time recovery evidence.
10. Show multi-region survivability or a truthful staged path with measurable latency.

## Top 10 Documentation Improvements

1. Replace aspirational statements with a verified “what works today” matrix.
2. Add one architecture diagram showing deployed resources and data ownership.
3. Add a sequence diagram showing request, memory write, retrieval, tools, approval, replay.
4. Publish a two-minute demo script with exact expected outputs.
5. Add a CockroachDB memory schema and lifecycle document.
6. Add security/data-classification/retention and approval audit documentation.
7. Add a deployment guide that actually works from a clean account.
8. Add benchmark and evaluation methodology, datasets, thresholds, and results.
9. Add incident runbooks for RAG failure, approval delay, DLQ growth, restore, and secret rotation.
10. Add a precise business-impact section with assumptions and measured outcomes.

## Top 10 Judging Risks

1. Judges cannot run or see a complete end-to-end workflow.
2. The CockroachDB “agent memory” claim has no implementation proof.
3. Broken Alembic revision lineage invalidates the setup instructions.
4. Terraform modules are presented as production infrastructure but are not composed.
5. Bedrock Agent claims are static files, not AWS resources/executions.
6. RAG claims lack a valid ingestion-to-retrieval path and quality evidence.
7. README has placeholder organization/license claims and stale milestone language.
8. Security controls are helpers, not enforced data-flow controls.
9. No meaningful tests, performance evidence, recovery evidence, or demo data journey.
10. Travel value is unproven without policy sources, integrations, KPIs, and user workflow proof.

## Probability Estimates

| Outcome | Current probability | Reasoning |
| --- | ---: | --- |
| Top 10% | 8% | The architecture and problem are credible, but evidence is thin. |
| Top 3 | 2% | Top projects will show deployed, reliable, distinctive agent workflows. |
| First place | <1% | There is no live differentiator or demonstrated CockroachDB memory advantage today. |

If improvements 1–11 are delivered and demonstrated, the project could reasonably move to
**Top 10%: 45%**, **Top 3: 20%**, **First place: 8%**. Those estimates require real
deployment, measured evaluation results, a polished live demo, and CockroachDB-backed
memory/replay—not expanded scaffolding.
