# Architecture decisions and constraints

The planned architecture is microservice-inspired, domain-driven, serverless, and
event-driven. Lambdas have one responsibility; orchestration and domain events prevent
god functions and tight coupling.

## Planned domain event flow

`TravelRequestSubmitted` → `TravelRequestValidated` → `PolicyRetrieved` →
`VisaChecked` → `RiskAssessed` → `InsuranceCalculated` →
`RecommendationGenerated` → `ApprovalRequested` → `ApprovalCompleted` →
`TravelRequestCompleted`

Event schemas, consumers, retry strategy, and idempotency rules will be designed in
Milestone 3 and documented under `docs/architecture/`.

## Data boundary

CockroachDB Serverless is the primary transactional database, accessed through a
PostgreSQL driver. Planned records include travel requests, users, quotes, policies,
prompt versions, evaluations, audit logs, approval history, and AI conversations.
DynamoDB must not be used for transactional platform data.
