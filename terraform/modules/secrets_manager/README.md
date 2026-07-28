# Secrets Manager module

Creates a KMS-encrypted secret container. Prefer injecting the value through a secure
CI secret; leaving `secret_string` null creates no secret version.
