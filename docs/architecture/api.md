# Travel Request API

FastAPI is exposed through Mangum as an AWS Lambda handler:
`travel_operations.api.main.handler`.

All endpoints require a Bearer JWT signed with HS256 using `JWT_SECRET` from Secrets
Manager. The authenticated `sub` claim is the request owner. A `tenant_id` claim is optional
for backwards compatibility and defaults to `default`; it scopes the travel request and all
associated durable travel-case memory. A request identifier is never sufficient authorization
on its own: user-facing reads and approver actions must also match the token tenant.

Each API request owns one transactional database session: successful calls commit, failed
calls roll back, and all sessions close before returning to the pool.

For request creation, the request and its outbox record commit before EventBridge is
called. This keeps the durable request state independent of an external publication
failure.

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/travel-request` | Create metadata and emit `TravelRequestCreated` |
| POST | `/itineraries` | Create a travel case and return an auditable, non-booking multi-agent draft |
| GET | `/travel-request/{id}` | Read the caller's request metadata |
| GET | `/travel-request/{id}/memory` | Read the caller's ordered durable travel-case history |
| POST | `/travel-request/{id}/approval` | Complete the pending human-approval callback |

OpenAPI is served at `/openapi.json`. `POST /itineraries` runs the bounded centralized itinerary
coordinator: profile, policy/compliance, risk, inventory research, itinerary, and financial-triage
specialists write durable CockroachDB provenance. The result is a transparent non-booking draft;
policy/risk and supplier results require human review. Metadata and pending
Step Functions approval tokens and append-only travel-case memory events are persisted in CockroachDB. The deployed HTTP API routes
to a Mangum-hosted Lambda function; EventBridge starts the approval state machine.
