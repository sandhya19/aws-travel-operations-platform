# Terraform standards

All cloud infrastructure must be provisioned through Terraform. Reusable modules use
explicit variables and outputs, consistent naming, and no environment-specific values.
Environment composition lives under `terraform/environments/` and modules under
`terraform/modules/`.

Remote-state design and resource definitions are intentionally deferred to Milestone 1.
Do not commit state, credentials, or non-example variable files.
