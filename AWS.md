# AWS, security, and observability direction

Planned AWS services include API Gateway, Lambda, EventBridge, Step Functions, SQS,
SNS, CloudWatch, X-Ray, Secrets Manager, IAM, KMS, S3, Parameter Store, and Amazon
Bedrock (including Knowledge Bases and Guardrails).

Security requirements are least-privilege IAM, encrypted and TLS-protected data,
Secrets Manager-backed credentials, input validation, prompt-injection protection, PII
masking, audit logs, and human approval checkpoints.

Application controls reject common prompt-injection instructions, validate API data, mask
common PII before audit logging, and use correlation IDs for traceable audit events.

Services will emit structured logs with correlation IDs, traces, metrics, and dashboards.
Infrastructure implementation starts in Milestone 1.
