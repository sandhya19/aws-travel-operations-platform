# Production security controls

Terraform IAM roles are service-scoped and must use least-privilege inline policies.
KMS encrypts queues, topics, logs, storage, and Secrets Manager entries; credentials are
provided only through Secrets Manager. API schemas validate inputs, prompt-bound text is
screened for instruction override attempts, and audit logs mask common email/card PII.
Every request should carry a correlation ID for audit and incident investigation.

## JWT signing material

The dev API Lambda receives `JWT_SECRET_SECRET_ARN` and resolves the signing material from its
dedicated KMS-encrypted Secrets Manager secret. `JWT_SECRET` remains a local-development-only
environment variable and is never configured on the deployed Lambda.

## Security dashboard

The monitoring module provisions a CloudWatch security dashboard for Lambda errors and
API Gateway 4XX/5XX signals. Production deployments must add alarms for authentication
failures, Secrets Manager access failures, KMS failures, DLQ depth, and anomalous IAM
denials; alert routing is environment-owned.
