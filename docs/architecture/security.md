# Production security controls

Terraform IAM roles are service-scoped and must use least-privilege inline policies.
KMS encrypts queues, topics, logs, storage, and Secrets Manager entries; credentials are
provided only through Secrets Manager. API schemas validate inputs, prompt-bound text is
screened for instruction override attempts, and audit logs mask common email/card PII.
Every request should carry a correlation ID for audit and incident investigation. The implemented
travel-request create, retrieve, and approval paths emit structured audit events; the audit
adapter masks every logged field before it reaches the log.

## Tenant isolation

The JWT `tenant_id` claim is the authorization boundary for a travel case. It defaults to
`default` only for backwards-compatible local tokens. CockroachDB stores the same value on the
travel request and the related memory session; API and action-group paths use it as a query
predicate, returning the same not-found response for an inaccessible cross-tenant identifier.
The action-group handler requires `travel_request_id`, `tenant_id`, and `user_id` session
attributes before recording durable tool provenance.

## Knowledge-source ingestion

The knowledge bucket is private, versioned, and KMS-encrypted. Its ingestion Lambda can read only
objects in that bucket, invoke only Titan Text Embeddings V2, and read only the database TLS
secrets it needs. The handler rejects objects outside the tenant-prefixed PDF namespace, malformed
or encrypted PDFs, excessive payloads, unsafe instruction text, and malformed embedding responses.

## Retrieval authorization

Knowledge retrieval is authorization-filtered in CockroachDB. The caller tenant is mandatory; role
metadata permits either tenant-wide documents (no role rows) or documents restricted to matching
roles. Citation verification rejects answer references that were not present in the filtered result.
The grounded-answer safety gate returns an explicit insufficient-evidence outcome below the
configured retrieval confidence threshold and a generic safe fallback for generation or citation
validation failures. It does not disclose the failed model/tool payload.

## JWT signing material

The dev API Lambda receives `JWT_SECRET_SECRET_ARN` and resolves the signing material from its
dedicated KMS-encrypted Secrets Manager secret. `JWT_SECRET` remains a local-development-only
environment variable and is never configured on the deployed Lambda.

## Security dashboard

The dev composition provisions a CloudWatch operations dashboard and encrypted SNS alarm topic for
Lambda/Step Functions errors, DLQ depth, API 4XX client/authentication signals, API latency, and
KMS key errors. `operations_alert_email` is optional and requires explicit SNS confirmation.
The 4XX alarm is deliberately triaged against access logs because it also includes valid input
errors. Secrets Manager and IAM-denial detection remain log-investigation controls until a central
CloudTrail logging account is introduced.
