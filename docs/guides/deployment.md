# Deployment

Build the Lambda artifact outside Terraform, store secrets in AWS Secrets Manager, review `terraform plan`, and apply only through the protected GitHub Actions environment. Configure a unique S3 bucket and CockroachDB TLS endpoint for every environment.

## Terraform state

The dev environment uses the private `travel-operations-terraform-state-489922706678-eu-west-2`
S3 backend, with versioning, public-access blocking, SSE-KMS using
`alias/travel-operations-terraform-state`, and DynamoDB locking through
`travel-operations-terraform-locks`. Authenticate with the configured AWS SSO profile before
running Terraform. Do not commit, copy, or share local `terraform.tfstate` files: state can hold
sensitive resource values. Rotate any credentials that were ever stored in a local state file.

Run `alembic upgrade head` before deploying a version that reads new schema objects. The
deployment pipeline must fail if migration-lineage tests or upgrade validation fail.

## Deployed development slice

The development stack is deployed in `eu-west-2`. It includes an HTTP API, purpose-specific Lambda
functions, a custom EventBridge bus, a Standard Step Functions approval workflow, SQS DLQ,
CloudWatch logging, X-Ray tracing, IAM roles, and a two-subnet VPC. The API endpoint is an
environment output; retrieve it with `terraform -chdir=terraform/environments/dev output -raw travel_api_endpoint`.

The Lambda artifact must contain Linux wheels. Use the repository package scripts from a
Linux build environment (or request `manylinux2014_x86_64` wheels) before applying Terraform.
`build_lambda_package.py` automatically packages the current `src/travel_operations` code over
the staged dependencies; do not manually copy source into `dist/lambda-package`. `source_code_hash`
is set so artifact changes update both functions.

## AgentCore Runtime artifact

The centralized itinerary coordinator is hosted by AgentCore Runtime because this AWS account cannot
create new Bedrock Agents. Build both the Lambda and direct-code ZIP artifacts before Terraform
plans or applies. AgentCore direct
deploy requires Linux ARM64 dependencies:

```bash
rm -rf .agentcore-build dist/agent-runtime-package
py -3.12 -m venv .agentcore-build
source .agentcore-build/Scripts/activate
python -m pip install --upgrade pip
python -m pip install --platform manylinux2014_aarch64 --implementation cp --python-version 312 \
  --only-binary=:all: --target dist/agent-runtime-package -r agent_runtime/requirements.txt
deactivate
python scripts/build_agent_runtime_package.py
terraform -chdir=terraform/environments/dev init -upgrade
terraform -chdir=terraform/environments/dev validate
terraform -chdir=terraform/environments/dev plan
terraform -chdir=terraform/environments/dev apply
```

`init -upgrade` is mandatory because AgentCore Runtime requires AWS provider v6.33 or newer. If
Terraform reports an SSO proxy connection error, renew the configured AWS SSO profile and correct
or remove the stale `HTTPS_PROXY`/`HTTP_PROXY` session variables before retrying; do not edit
`.terraform.lock.hcl` manually.

Use Git Bash or WSL for the command above. On Windows PowerShell, omit `rm -rf` and use
`Remove-Item -Recurse -Force dist/agent-runtime-package` only after confirming that exact folder is
the staging directory. The isolated `.agentcore-build` environment prevents AgentCore dependencies
from conflicting with the FastAPI application's dependencies. The apply creates a private
KMS-encrypted artifact bucket and an IAM-invoked AgentCore Runtime; it does not expose a public
conversational endpoint.

For the development stack, export `TF_VAR_jwt_secret` from the ignored `.env` value before
planning or applying. Terraform marks the input sensitive. Production deployment should
replace this development wiring with a Secrets Manager reference.

## Operations alarms and evidence tools

The Milestone 4 Terraform changes create the dev CloudWatch operations dashboard, encrypted SNS
alarm topic, and alarms for DLQ depth, Lambda/Step Functions failures, API client/authentication
signals, API p99 latency, and KMS errors. Set `TF_VAR_operations_alert_email` only when a monitored
mailbox is available; SNS sends a confirmation email that must be accepted before it can alert.

After a reviewed plan, apply the environment and retrieve the dashboard/topic outputs. The
benchmark, replay drill, and isolated CockroachDB restore drill are manual dev exercises; their
commands and safety constraints are in [Operational evidence](../operations.md) and the
[runbooks](../runbooks/README.md). Never place benchmark results, backup locations, restored
database URLs, or credentials in Terraform variables or version control.
