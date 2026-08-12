# Architecture overview

## Scope

This document records both the target architecture direction and the deployed development
vertical slice. The current slice accepts travel requests, persists them in CockroachDB,
publishes an EventBridge event, creates an auditable itinerary draft through a centralized
specialist coordinator when requested, waits for authenticated human approval in Step Functions,
and then completes the request. Supplier booking and model-backed policy decisions remain outside
this development slice.

## Target context

Employees submit travel requests. Travel operations staff receive AI-generated,
grounded recommendations and retain human approval authority. The platform consumes
company policy and external travel knowledge, while maintaining auditability.

## Target building blocks

- API Gateway and Lambda expose narrowly scoped APIs.
- EventBridge, Step Functions, SQS, and SNS coordinate asynchronous workflows.
- CockroachDB stores transactional records through PostgreSQL-compatible access.
- Amazon Bedrock provides model access; RAG grounds responses in approved sources.
- S3 stores controlled documents and artifacts; Secrets Manager and KMS protect data.
- CloudWatch, X-Ray, and encrypted SNS provide logs, traces, an operations dashboard, and
  actionable alarms for workflow/Lambda failure, DLQ, API client/authentication signals, latency,
  and KMS errors.

## Principles

1. AI recommends; humans approve.
2. Responses are explainable and cited.
3. Domain events decouple workflow stages.
4. Each Lambda has one responsibility.
5. Terraform provisions all infrastructure.
6. Security and observability are designed in, not bolted on.
7. Tenant identity is enforced at the persistence query boundary, not inferred from a request ID.

Terraform provisions the development API Gateway, Lambda functions, EventBridge rules, Step
Functions workflow, SQS DLQ, CloudWatch logging, KMS keys, and Secrets Manager entries used by
the vertical slice. The broader AI, RAG, and external-provider integrations remain target-state
components.

The development composition also includes a private, KMS-encrypted knowledge bucket and a narrowly
scoped ingestion Lambda. It creates approved tenant-owned CockroachDB document versions and
embeddings. CockroachDB retrieval applies tenant/role filters and returns versioned citations. The
interactive itinerary endpoint delegates profile, policy/compliance, risk, inventory research,
itinerary, and financial-triage work through a hub-and-spoke coordinator. Every result is a
non-booking, human-review draft with durable tool and memory provenance.

Operational evidence is collected outside the request path: a bounded synthetic workflow benchmark
measures completed journey latency/throughput, the checkpoint replay drill proves callback recovery,
and the CockroachDB DR runbook validates an isolated point-in-time restore of durable case data.
