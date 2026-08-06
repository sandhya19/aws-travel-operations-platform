# Deployment

Build the Lambda artifact outside Terraform, store secrets in AWS Secrets Manager, review `terraform plan`, and apply only through the protected GitHub Actions environment. Configure a unique S3 bucket and CockroachDB TLS endpoint for every environment.

Run `alembic upgrade head` before deploying a version that reads new schema objects. The
deployment pipeline must fail if migration-lineage tests or upgrade validation fail.

## Deployed development slice

The development stack is deployed in `eu-west-2`. It includes an HTTP API, two Lambda
functions, a custom EventBridge bus, a Standard Step Functions approval workflow, SQS DLQ,
CloudWatch logging, X-Ray tracing, IAM roles, and a two-subnet VPC. The API endpoint is an
environment output; retrieve it with `terraform -chdir=terraform/environments/dev output -raw travel_api_endpoint`.

The Lambda artifact must contain Linux wheels. Use the repository package scripts from a
Linux build environment (or request `manylinux2014_x86_64` wheels) before applying Terraform.
`source_code_hash` is set so artifact changes update both functions.

For the development stack, export `TF_VAR_jwt_secret` from the ignored `.env` value before
planning or applying. Terraform marks the input sensitive. Production deployment should
replace this development wiring with a Secrets Manager reference.
