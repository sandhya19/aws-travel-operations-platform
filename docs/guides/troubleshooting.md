# Troubleshooting

**Migration failure:** verify `DATABASE_URL`, CockroachDB TLS settings, and network allowlists.

**401 API response:** supply a valid HS256 Bearer JWT with a `sub` claim and matching `JWT_SECRET`.

**Terraform provider failure:** run `terraform init` from the environment directory and verify registry access.
