# Project charter

Large organizations often process employee travel requests manually: policy validation,
visa checks, insurance calculations, budget review, risk assessment, and travel
recommendations can take hours or days.

This platform will reduce that work to minutes through AI-assisted, document-grounded
recommendations. The system never makes final approval decisions; a human retains
approval authority. Every recommendation must be explainable and cite its supporting
company documentation.

## Goals

- Deliver a production-minded, enterprise monorepo using Python, AWS, Terraform,
  CockroachDB, Amazon Bedrock, RAG, and event-driven architecture.
- Keep components loosely coupled, auditable, observable, and secure.
- Separate applications, infrastructure, documentation, tests, prompts, evaluations,
  knowledge-base material, and C4/event-flow diagrams.

## Users

- Employees submitting travel requests
- Travel-operations specialists reviewing AI recommendations
- Human approvers making final approval decisions
- Platform, security, and compliance operators

## Non-functional expectations

The platform will apply least privilege, TLS and KMS encryption, structured logging,
correlation IDs, traceability, audit logs, input validation, PII protection, and human
approval checkpoints. Detailed design is tracked in `docs/` and ADRs.
