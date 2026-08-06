# ADR 0003: EventBridge starts a callback-based approval workflow

## Status

Accepted (2026-07-30).

## Context

Travel request submission must not synchronously wait for human approval. The workflow
needs durable delivery, retry handling, and a way to resume after a human decision.

## Decision

The API emits `TravelRequestCreated` on the custom EventBridge bus. An EventBridge rule
starts a Standard Step Functions state machine and sends failed deliveries to an SQS DLQ.
The workflow uses the Step Functions callback task-token pattern. Its Lambda records the
token in CockroachDB; the authenticated approval endpoint sends task success and the
workflow marks the request complete.

## Consequences

This makes the approval wait durable and observable without holding an HTTP request open.
The current demo slice has no transactional outbox and the approval route does not yet
enforce a distinct approver role; both are explicitly deferred follow-up concerns.
