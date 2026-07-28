# Terraform

Terraform is the sole mechanism for provisioning platform infrastructure. Reusable
modules belong in `modules/`; environment-specific composition belongs in
`environments/<environment>/`.

Do not commit state files, credentials, or production variable values. Remote-state,
provider, and deployment configuration will be introduced with the infrastructure
milestone.

## Modules

The module library covers API Gateway, Lambda, IAM, SQS, SNS, EventBridge, Step
Functions, CockroachDB connectivity, Secrets Manager, KMS, CloudWatch, X-Ray, S3,
Bedrock Guardrails, and networking. Every module has `variables.tf`, `outputs.tf`, a
README, and a commented example. Lambda artifacts are an explicit input; Terraform
does not create application code.

Run `terraform init -backend=false` followed by `terraform validate` from each
environment directory. Remote state is intentionally not configured until an approved
state-storage decision is made.
