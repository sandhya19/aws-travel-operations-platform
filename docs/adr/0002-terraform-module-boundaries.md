# ADR 0002: Use reusable Terraform modules for platform boundaries

## Status

Accepted — 2026-07-28

## Context

The platform must provision AWS infrastructure consistently across environments while
keeping service ownership explicit and avoiding application packaging in Terraform.

## Decision

Use one focused module per platform boundary: networking, encryption, secrets, IAM,
observability, messaging, API, orchestration, database connectivity, storage, Bedrock,
and Lambda. Modules expose inputs and outputs, with artifact paths supplied externally
to the Lambda module.

## Consequences

Infrastructure is composable and reviewable. Environment owners must wire module
instances and supply deployment-specific values; remote-state adoption requires a
separate decision.
