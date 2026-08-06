# Travel Request API

FastAPI is exposed through Mangum as an AWS Lambda handler:
`travel_operations.api.main.handler`.

Both endpoints require a Bearer JWT signed with HS256 using `JWT_SECRET` from Secrets
Manager. The authenticated `sub` claim is the request owner.

Each API request owns one transactional database session: successful calls commit, failed
calls roll back, and all sessions close before returning to the pool.

For request creation, the request and its outbox record commit before EventBridge is
called. This keeps the durable request state independent of an external publication
failure.

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/travel-request` | Create metadata and emit `TravelRequestCreated` |
| GET | `/travel-request/{id}` | Read the caller's request metadata |
| POST | `/travel-request/{id}/approval` | Complete the pending human-approval callback |

OpenAPI is served at `/openapi.json`. No AI processing is invoked. Metadata and pending
Step Functions approval tokens are persisted in CockroachDB. The deployed HTTP API routes
to a Mangum-hosted Lambda function; EventBridge starts the approval state machine.
