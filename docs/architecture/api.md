# Travel Request API

FastAPI is exposed through Mangum as an AWS Lambda handler:
`travel_operations.api.main.handler`.

Both endpoints require a Bearer JWT signed with HS256 using `JWT_SECRET` from Secrets
Manager. The authenticated `sub` claim is the request owner.

| Method | Path | Purpose |
| --- | --- | --- |
| POST | `/travel-request` | Create validated travel-request metadata |
| GET | `/travel-request/{id}` | Read the caller's request metadata |

OpenAPI is served at `/openapi.json`. No AI processing is invoked. Metadata uses an
in-memory repository until the CockroachDB milestone.
