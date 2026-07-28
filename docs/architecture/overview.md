# Architecture overview

## Scope

This document records the target architecture direction, not a deployed design.
Milestone 0 creates repository boundaries only.

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
- CloudWatch and X-Ray provide logs, metrics, dashboards, and traces.

## Principles

1. AI recommends; humans approve.
2. Responses are explainable and cited.
3. Domain events decouple workflow stages.
4. Each Lambda has one responsibility.
5. Terraform provisions all infrastructure.
6. Security and observability are designed in, not bolted on.

The Terraform module library now captures the infrastructure boundaries. Application
routes, event consumers, and workflow states remain deferred until their owning
milestones; no application code is provisioned by Terraform.
