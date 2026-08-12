# 1.0.0 (2026-08-06)


### Features

* add CockroachDB persistence ([9b6ab05](https://github.com/sandhya19/aws-travel-operations-platform/commit/9b6ab051e3fced3a7bb59410a0cb3bd246119fa9))
* add travel lifecycle events ([5abbb0d](https://github.com/sandhya19/aws-travel-operations-platform/commit/5abbb0d600275d11be15c0afdeff7e9e7a72a959))
* implement resilient travel workflow and AWS foundations ([606a3a5](https://github.com/sandhya19/aws-travel-operations-platform/commit/606a3a5d7a1d6a136c908e93735b1675be03084b))
* implement travel request API ([92bbdb1](https://github.com/sandhya19/aws-travel-operations-platform/commit/92bbdb1dcd436b37b0050620c8e0e24ae05f7804))
* initialize repository ([c3affa6](https://github.com/sandhya19/aws-travel-operations-platform/commit/c3affa608d6a9766a478985f797045f72fb6a57a))

# Changelog

All notable changes are generated automatically from Conventional Commits by semantic-release.

## Unreleased

### Added

- Added the authenticated `POST /itineraries` interactive journey. It creates one travel case,
  delegates six bounded specialists through a centralized coordinator, returns a transparent
  non-booking draft, and stores its complete CockroachDB provenance before human approval.

- Added a bounded AgentCore itinerary coordinator that delegates durable policy/compliance, risk,
  and itinerary-draft specialist tool calls, returning a non-booking, human-review draft.

- Added Milestone 4 operational evidence tooling: bounded concurrent workflow benchmarks and KPI
  comparison, checkpoint fault/recovery procedures, Terraform-managed CloudWatch/SNS alarms and
  operations dashboard, plus CockroachDB restore-drill evidence validation and runbooks.

- Completed IMP-019 test automation foundation: push/pull-request CI triggers, an opt-in deployed
  authenticated request-to-approval E2E test, reusable workflow-runner evidence, and documented
  database/cloud test tiers.

- Completed IMP-018 reproducible prompt-release benchmark: version-linked golden dataset coverage,
  deterministic insufficient-evidence evaluation, aggregate groundedness/citation quality gates,
  reviewed v2 baseline, and a non-zero failing release command.

- Completed IMP-017 prompt release governance with versioned active/rollback metadata, owner/model
  assumptions, linked evaluation gates, prompt-injection-hardened grounded-answer v2, and release
  registry tests.

- Completed IMP-016 grounded-answer safety controls: deterministic confidence threshold,
  insufficient-evidence and safe-fallback outcomes, adversarial failure coverage, and a baseline
  Terraform-managed Bedrock Guardrail for the future model-invocation boundary.

- Completed IMP-015 with an AgentCore Runtime direct-code coordinator, typed Lambda tool, narrowly
  scoped invocation permissions, and durable CockroachDB tool provenance. This replaces the
  unavailable Bedrock Agent/action-group resource for accounts in Bedrock Agents maintenance mode.

- Completed IMP-014 citation RAG foundation with CockroachDB tenant/role query filters, versioned
  citations, grounded-answer validation, and citation regression coverage.

- Completed IMP-013 secure document ingestion with tenant-prefixed PDF validation, immutable
  CockroachDB document versions, Titan embedding validation, and scoped S3/Lambda/IAM resources.

- Completed IMP-011 tenant-aware memory retrieval. Travel requests are now tenant-owned and
  tenant-scoped request, memory, approval, approval-history, and action-group provenance queries
  deny cross-tenant access.

- Started IMP-006 with CockroachDB-backed, tenant-scoped travel-case sessions and append-only
  memory events. The authenticated request owner can retrieve the recorded case history.

- Started IMP-007 with durable deterministic workflow plans and idempotent action-group tool
  execution provenance, correlated to each travel case.

- Started IMP-008 with idempotent CockroachDB checkpoints for the travel approval workflow.

- Started IMP-009 with immutable rejection decisions, approval history, and workflow branching.

- Started IMP-010 with scheduled expiry of terminal travel-case memory and immutable lifecycle evidence.

- Moved the dev API JWT signing secret from Lambda environment configuration to a dedicated
  KMS-encrypted Secrets Manager runtime secret.

- Added the deployed EventBridge-to-Step-Functions approval vertical slice, SQS delivery DLQ,
  CockroachDB approval-task migration, and authenticated approval endpoint.

### Fixed

- Preserve the EventBridge request detail after the Step Functions approval callback so
  the IMP-003 workflow can mark the correct travel request complete.
- Added Linux Lambda packaging guidance, artifact hashing, and the CockroachDB dialect runtime dependency.
- Wired the development JWT secret into the deployed API Lambda as a sensitive Terraform input.

### Fixed

- Made travel-request repository sessions commit, roll back, and close deterministically.

### Fixed

- Restored the Alembic `0001` → `0002` → `0003` migration chain and added migration-lineage coverage.
