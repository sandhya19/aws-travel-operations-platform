# Terraform

Terraform is the sole mechanism for provisioning platform infrastructure. Reusable
modules belong in `modules/`; environment-specific composition belongs in
`environments/<environment>/`. This milestone intentionally defines no resources.

Do not commit state files, credentials, or production variable values. Remote-state,
provider, and deployment configuration will be introduced with the infrastructure
milestone.
