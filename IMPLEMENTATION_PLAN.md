# Hackathon Score-Maximizing Implementation Plan

## Current status â€” 2026-08-11

Completed: IMP-001, IMP-002, IMP-003, IMP-004, and IMP-012. The deployed development
slice persists authenticated requests and durable outbox events, starts an idempotent
Step Functions approval workflow through EventBridge, records immutable approval decisions,
and supports bounded retry/DLQ recovery.

IMP-005 is **partial**: runtime secrets and scoped runtime permissions are implemented; GitHub
OIDC, rotation automation, and IAM policy-scanner evidence remain outstanding. IMP-009 is
**partial**: attributed approval decisions are immutable, while rejection and a reviewer-facing
approval-history API remain future work.

**IMP-006 foundation is implemented.** CockroachDB-backed, tenant-scoped travel-case sessions
and append-only memory events record request submission, approval requested, approval decision,
and completion; the request owner can retrieve their ordered history. An opt-in CockroachDB
integration test is available and must run with `RUN_DATABASE_INTEGRATION=1` against a migrated
database.

**IMP-007 foundation is implemented.** Revision `0008` records a deterministic workflow plan and idempotent
action-group tool executions with the same session, tenant, user, and correlation provenance.
It does not claim LLM reasoning or Bedrock agent execution until IMP-015 connects real agents.

**Active work: IMP-008.** Revision `0009` adds idempotent CockroachDB workflow checkpoints for
validation, approval waiting, approval decision, and completion. The approved-callback replay
command resumes only a durable approved, incomplete request. An induced-failure cloud exercise
remains the next increment.

**IMP-009 has started.** The workflow now branches explicitly on a human approval or rejection;
each decision is immutable, and approvers can retrieve decision history. Authorization and
deployed rejection-path testing remain to be completed.

**IMP-010 has started.** New travel-case sessions receive a retention expiry. A daily dev Lambda
expires only terminal cases and writes immutable expiry evidence. Physical deletion,
consolidation, and a deployed expiry exercise remain future work.

**IMP-011 is complete.** Revision `0011` assigns every travel request to its JWT tenant,
backfills existing requests to `default`, and adds a tenant/requester/status index. Request,
memory, approval, approval-history, and action-group provenance lookups now require the caller's
tenant context; negative tests cover cross-tenant access.

**IMP-013 is complete.** Revision `0012` adds tenant-owned, immutable knowledge-document
versions and scoped chunk metadata. The private S3 ingestion Lambda accepts only tenant-prefixed
PDFs that pass size, type, signature, encryption, text-safety, and Titan embedding-shape checks.

**IMP-014 is complete.** Revision `0013` adds document-role metadata. CockroachDB vector queries
now filter by tenant and document role before ranking; versioned citations are verified against the
retrieved context, with deterministic regression evaluation coverage.

**IMP-015 is complete.** The unavailable Bedrock Agent/action-group deployment has been replaced
with an AgentCore Runtime direct-code coordinator. It invokes the typed `lookup_policy` Lambda with
tenant/user/request context and preserves durable CockroachDB provenance.

**IMP-016 is complete.** Grounded answers require a minimum retrieval confidence of `0.75` and
return deterministic insufficient-evidence or safe-fallback outcomes for low confidence, generation
failure, and citation validation failure. A baseline Bedrock Guardrail is provisioned for the future
model-invocation boundary.

**IMP-017 is complete.** The source-controlled prompt registry records owner, model assumption,
evaluation dataset/gates, release status, and rollback version. The active grounded-answer prompt
is `v2`; regression coverage validates release gates and malformed metadata.

**IMP-018 is complete.** A reproducible prompt-release benchmark validates complete candidate
coverage and gates promotion on configured aggregate groundedness and citation accuracy. The golden
dataset includes both cited policy evidence and insufficient-evidence behavior.

**IMP-019 is complete.** The default CI workflow runs on push and pull request. Opt-in database
integration and deployed authenticated approval E2E tests are documented and registered, while
remaining cloud RAG/AgentCore tests stay separate until a model-backed RAG endpoint exists.

**Milestone 4 operational implementation is ready for dev deployment.** IMP-020 adds bounded
workflow load measurement and documented checkpoint fault/recovery evidence; IMP-021 adds
CloudWatch/SNS alarms and an operations dashboard; IMP-022 adds the CockroachDB isolated-restore
drill and evidence validation; and IMP-023 adds a reproducible baseline-versus-assisted KPI
comparison. Their live acceptance records require the dev AWS/CockroachDB operator to run the
documented exercises.

**Hackathon interaction update:** the AgentCore Runtime is a centralized itinerary coordinator for
a saved tenant-scoped travel requirement. It delegates fixed profile, policy/compliance, risk,
inventory research, itinerary, and financial-triage specialist calls and preserves each delegation
in CockroachDB provenance. The judge-visible `POST /itineraries` journey is deterministic and
transparent: it returns a non-booking draft and starts the existing human approval workflow.
Specialist outputs remain human-review-only until real policy, duty-of-care, and booking
integrations are authorized.

## Post-pause hackathon finish plan

Use the three days after the pause to turn the deployed, tested vertical slice into a concise
reviewer experience. This is intentionally a submission plan, not authorization to add unsupported
supplier, booking, policy, or risk integrations.

1. **Reviewer journey (highest impact).** Add a small static reviewer page using the existing API
   contract: submit one itinerary requirement, render the six delegated specialist results, link to
   the tenant-scoped memory timeline, and make the required human-approval state unmistakable.
   Acceptance: a judge can complete the journey without a command-line client.
2. **Evidence and demo.** Record a two-minute narrated path: requirement submission, transparent
   coordinator delegation, CockroachDB memory/provenance query, and human approval. Capture a
   fallback video/screenshots and commit only redacted evidence and reproducible scripts.
3. **Submission rehearsal.** From a clean checkout, run the documented lint, unit, opt-in database
   integration, Terraform validation, and deployed demo steps. Confirm the SNS subscription and
   callback recovery drill evidence; do not claim a CockroachDB restore drill unless it is actually
   run and recorded.

Deferred until after the hackathon: live GDS/hotel inventory, autonomous bookings, external
duty-of-care decisions, and a production model-backed policy decision. The current draft correctly
labels each as requiring an authorized integration and/or human review.

## Ordering Principle

Backlog order maximizes demonstrable scoring gain while removing prerequisites and
delivery risk first. No milestone is complete until its acceptance criteria, tests, and
documentation are complete.

## Milestone 1 — Credibility and Runnable Core

- **IMP-001 — Repair Alembic lineage.** Category: Data reliability; Priority: Critical; Complexity: S; Dependencies: none; AWS: none; CockroachDB: migrations/schema; AI: none; Business value: deployable data layer; Scoring impact: 5/5; Risk if omitted: setup fails; Acceptance: clean `upgrade head` and downgrade/upgrade on empty DB; Docs: install/deployment; Tests: migration CI; Time: 0.5 day.
- **IMP-002 — Transaction-safe API repository lifecycle.** Category: API/data; Priority: Critical; Complexity: S; Dependencies: IMP-001; AWS: Lambda; CockroachDB: sessions/transactions; AI: none; Business: prevents lost requests; Impact: 4/5; Risk: leaked sessions/inconsistent writes; Acceptance: request commit/rollback verified; Docs: API; Tests: repository integration; Time: 1 day.
- **IMP-012 — Outbox/inbox event reliability.** Category: Architecture; Priority: Critical; Complexity: L; Dependencies: IMP-001–002; AWS: EventBridge/SQS; CockroachDB: transactional outbox/idempotency; AI: none; Business: trustworthy automation; Impact: 5/5; Risk: lost, duplicate, or prematurely consumed workflow events; Acceptance: request persistence and outbox write commit atomically; duplicate EventBridge deliveries are idempotent; retried publication and DLQ recovery are demonstrated; Docs: event contract/recovery; Tests: transaction, duplicate-delivery, retry, and DLQ tests; Time: 2 days.
- **IMP-003 — Full deployable vertical slice.** Category: Workflow; Priority: Critical; Complexity: XL; Dependencies: IMP-001–002, IMP-012; AWS: API Gateway, Lambda, EventBridge, Step Functions, SQS; CockroachDB: requests/status/outbox/approval state; AI: non-AI approval slice (bounded recommendation deferred to IMP-014–016); Business: prove product; Impact: 5/5; Risk: no demo; Acceptance: an authenticated request commits with its transactional outbox; duplicate-safe EventBridge handling starts a recoverable Step Functions workflow; an authorized approver resolves exactly one pending task; CockroachDB records `COMPLETED`; an authenticated cloud E2E test and scripted demo reproduce the path, including retry/DLQ recovery; all evidence is committed and reproducible from a clean checkout; Docs: demo/deploy/configuration consistency (deployed ASL is the sole workflow definition); Tests: cloud e2e, authorization, and failure-path tests; Time: 3 days.
- **IMP-004 — Compose Terraform environments.** Category: IaC; Priority: Critical; Complexity: L; Dependencies: IMP-003 interfaces; AWS: all core services; CockroachDB: secret/connectivity; AI: Bedrock IAM; Business: reproducible deployment; Impact: 5/5; Risk: architecture is unverifiable; Acceptance: plan/apply produces vertical slice; Docs: deployment; Tests: validate/plan; Time: 2 days.
- **IMP-005 — Least-privilege/OIDC/secret rotation.** Category: Security; Priority: High; Complexity: L; Dependencies: IMP-004; AWS: IAM, KMS, Secrets Manager, GitHub OIDC; CockroachDB: credential rotation; AI: Bedrock access; Business: enterprise trust; Impact: 4/5; Risk: unsafe demo/deployment; Acceptance: scoped roles and no static cloud keys; Docs: security; Tests: IAM policy checks; Time: 1.5 days.

## Milestone 2 — CockroachDB Agent Memory Differentiator

- **IMP-006 — Durable session and memory-event store.** Category: Agent memory; Priority: Critical; Complexity: XL; Dependencies: IMP-001; AWS: Lambda; CockroachDB: agent_sessions/memory_events; AI: all agents; Business: continuity; Impact: 5/5; Risk: no differentiator; Acceptance: append-only memory with tenant/user/correlation keys; Docs: memory schema; Tests: persistence; Time: 3 days.
- **IMP-007 — Tool, plan, and reasoning provenance.** Category: Agent memory; Priority: Critical; Complexity: L; Dependencies: IMP-006; AWS: Lambda/X-Ray; CockroachDB: tool_executions/plans; AI: action groups; Business: explainability; Impact: 5/5; Risk: unverifiable recommendations; Acceptance: every tool call/reasoning decision traceable; Docs: provenance; Tests: replay fixture; Time: 2 days.
- **IMP-008 — Checkpoint/recovery/replay.** Category: Resilience; Priority: Critical; Complexity: XL; Dependencies: IMP-006–007; AWS: Step Functions, SQS; CockroachDB: workflow_checkpoints; AI: state restoration; Business: recoverable operations; Impact: 5/5; Risk: workflow loss; Acceptance: induced failure resumes from checkpoint; Docs: runbook; Tests: chaos/e2e; Time: 3 days.
- **IMP-009 — Immutable approval history.** Category: Governance; Priority: Critical; Complexity: M; Dependencies: IMP-006; AWS: Lambda/API; CockroachDB: approval_decisions/audit; AI: approval packet; Business: compliance; Impact: 5/5; Risk: human-control claim unproven; Acceptance: attributed approve/reject/event history; Docs: approval flow; Tests: authorization; Time: 1.5 days.
- **IMP-010 — Memory lifecycle.** Category: Privacy; Priority: High; Complexity: M; Dependencies: IMP-006; AWS: EventBridge scheduler; CockroachDB: retention/supersession/deletion; AI: context freshness; Business: compliance; Impact: 4/5; Risk: PII retention; Acceptance: expiration, consolidation, deletion records; Docs: retention; Tests: lifecycle; Time: 1.5 days.
- **IMP-011 — Tenant-aware memory retrieval.** **Complete.** Category: Security/RAG; Priority: High; Complexity: L; Dependencies: IMP-006; AWS: API auth; CockroachDB: compound indexes; AI: context; Business: isolation; Impact: 5/5; Risk: cross-tenant data leak; Acceptance: authorization-filtered query plans; Docs: tenancy; Tests: negative access; Time: 2 days.

## Milestone 3 — Grounded AI and Real Agent Execution

- **IMP-013 — Secure document ingestion.** **Complete.** Category: Knowledge; Priority: High; Complexity: L; Dependencies: IMP-001/011; AWS: S3, Lambda, Bedrock; CockroachDB: documents/chunks/version; AI: Titan embeddings; Business: policy knowledge; Impact: 4/5; Risk: no factual basis; Acceptance: validated PDF-to-versioned chunks; Docs: ingestion; Tests: S3/PDF mocks; Time: 2 days.
- **IMP-014 — Citation RAG with metadata/ACL filters.** **Complete.** Category: RAG; Priority: Critical; Complexity: XL; Dependencies: IMP-011/013; AWS: Bedrock; CockroachDB: vector/index/provenance; AI: retrieval/context; Business: trusted answers; Impact: 5/5; Risk: hallucination; Acceptance: cited answer traceable to chunk/version; Docs: RAG; Tests: precision/recall; Time: 3 days.
- **IMP-015 — Bedrock agents/action groups.** **Complete.** Category: Agents; Priority: Critical; Complexity: XL; Dependencies: IMP-007/014; AWS: Bedrock, Lambda, IAM; CockroachDB: tool/memory records; AI: coordinator/policy/visa/risk/insurance; Business: automation; Impact: 5/5; Risk: static claims; Acceptance: real agent invokes typed tools; Docs: tools; Tests: contract; Time: 3 days.
- **IMP-016 — Confidence/fallback/guardrails.** Category: AI safety; Priority: High; Complexity: M; Dependencies: IMP-014–015; AWS: Bedrock Guardrails; CockroachDB: decision provenance; AI: confidence/fallback; Business: safe adoption; Impact: 4/5; Risk: unsafe recommendations; Acceptance: insufficient-evidence and fallback paths; Docs: safety; Tests: adversarial; Time: 1.5 days.
- **IMP-017 — Prompt release governance.** Category: Prompting; Priority: Medium; Complexity: M; Dependencies: IMP-014; AWS: S3/Bedrock; CockroachDB: prompt versions; AI: prompts; Business: controlled changes; Impact: 3/5; Risk: untraceable behavior; Acceptance: owner/model/eval/rollback metadata; Docs: prompt guide; Tests: regression; Time: 1 day.

## Milestone 4 — Evidence, Quality, and Operations

- **IMP-018 — Evaluation benchmark and quality gates.** Category: Evaluation; Priority: High; Complexity: L; Dependencies: IMP-014–015; AWS: Bedrock/CloudWatch; CockroachDB: evaluation history; AI: groundedness/faithfulness/citations; Business: measurable quality; Impact: 5/5; Risk: unverifiable AI; Acceptance: thresholds gate releases; Docs: methodology; Tests: golden regression; Time: 2 days.
- **IMP-019 — End-to-end/migration/RAG workflow tests.** Category: Testing; Priority: Critical; Complexity: L; Dependencies: IMP-003/014; AWS: LocalStack/sandbox; CockroachDB: Testcontainers; AI: mocked Bedrock; Business: reliability; Impact: 4/5; Risk: demo failures; Acceptance: CI green suite; Docs: test guide; Tests: e2e/integration; Time: 2 days.
- **IMP-020 — Load, fault, and recovery testing.** **Implementation ready; dev exercise pending.** Category: Resilience; Priority: Medium; Complexity: M; Dependencies: IMP-008/019; AWS: SQS/SFN; CockroachDB: transaction retries; AI: timeout fallback; Business: operating confidence; Impact: 3/5; Risk: hidden bottlenecks; Acceptance: documented limits/recovery; Docs: SLOs; Tests: bounded benchmark and callback-fault recovery.
- **IMP-021 — Observability/security dashboards and alarms.** **Implementation ready; dev apply and SNS confirmation pending.** Category: Operations; Priority: High; Complexity: M; Dependencies: IMP-003; AWS: CloudWatch/X-Ray/SNS; CockroachDB: health metrics; AI: quality metrics; Business: incident response; Impact: 3/5; Risk: silent failures; Acceptance: alerts for DLQ/auth/KMS/errors/latency; Docs: runbooks; Tests: Terraform contract validation.
- **IMP-022 — Backup/restore and DR proof.** **Runbook and evidence validation ready; recorded restore drill pending.** Category: DR; Priority: Medium; Complexity: M; Dependencies: IMP-006; AWS: S3/KMS; CockroachDB: backups/PITR; AI: memory restoration; Business: enterprise reliability; Impact: 4/5; Risk: data loss; Acceptance: recorded restore drill/RPO/RTO; Docs: DR runbook; Tests: evidence validation.
- **IMP-023 — Cost/latency/KPI benchmark.** **Measurement tooling ready; recorded comparison pending.** Category: Business evidence; Priority: High; Complexity: M; Dependencies: IMP-003/018; AWS: CloudWatch/Bedrock; CockroachDB: analytics; AI: latency/cost; Business: ROI; Impact: 4/5; Risk: no impact proof; Acceptance: baseline vs assisted results; Docs: KPI report; Tests: benchmark comparison.

## Milestone 5 — Submission Evidence

- **IMP-024 — Reviewer sandbox and demo data reset.** Category: Demo; Priority: High; Complexity: S; Dependencies: IMP-003/014; AWS: sandbox stack; CockroachDB: seeded tenant/data; AI: seeded cases; Business: judge usability; Impact: 5/5; Risk: judges cannot evaluate; Acceptance: one-command reset and scripted path; Docs: demo; Tests: smoke; Time: 1 day.
- **IMP-025 — Live/recorded demo and truthful evidence pack.** Category: Submission; Priority: Critical; Complexity: M; Dependencies: IMP-018–024; AWS: deployed environment; CockroachDB: memory/replay screens; AI: citations/evals; Business: winning narrative; Impact: 5/5; Risk: architecture-only judgment; Acceptance: 2-minute demo plus fallback video/screenshots; Docs: README/architecture/runbooks; Tests: demo rehearsal; Time: 1.5 days.

## Deferred After Submission

Approval delegation/escalation, supplier/GDS integrations, multi-region active-active,
and full enterprise reporting are high business value but lower score-per-risk than the
ordered backlog above. Implement only if milestones 1–5 are demonstrably complete.
