# ADR 0003: Use AgentCore Runtime for the travel-policy coordinator

## Status

Accepted — 2026-08-11

## Context

The development AWS account cannot create new Amazon Bedrock Agents because the Bedrock Agents
service is in maintenance mode for accounts without prior usage. The existing Terraform resource
therefore prevents an otherwise valid deployment.

## Decision

Replace the Bedrock Agent and action group with an Amazon Bedrock AgentCore Runtime direct-code
deployment. It calls the existing `lookup_policy` Lambda using the same tenant/user/request context
and retains CockroachDB provenance. The runtime package is stored in a private, versioned,
KMS-encrypted S3 bucket. The runtime uses the existing HTTP protocol and IAM invocation model.

## Consequences

- The deployment no longer depends on Bedrock Agents account eligibility.
- The public FastAPI and approval interfaces remain unchanged.
- AgentCore direct-code artifacts must be assembled for Linux ARM64 before Terraform applies them.
- This focused replacement does not add a user-facing conversational endpoint, autonomous model
  reasoning, or AgentCore Memory; those would need separate authorization and safety design.
