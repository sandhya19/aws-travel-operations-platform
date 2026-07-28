# ADR 0001: Adopt a monorepo with explicit platform boundaries

## Status

Accepted — 2026-07-28

## Context

The platform needs coordinated application code, infrastructure, tests, prompts,
evaluations, controlled knowledge sources, and operational documentation.

## Decision

Use a single repository with top-level boundaries for each concern. Python source uses
the `src/` layout; Terraform separates reusable modules from environment composition.

## Consequences

Shared standards and CI apply consistently. Ownership boundaries must remain explicit
as services are added; a monorepo does not authorize cross-domain coupling.
