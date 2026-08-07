# ADR 0004: Resolve JWT signing material from Secrets Manager at runtime

## Decision

The dev API Lambda receives a JWT secret ARN, not the JWT value. It resolves and caches the
value from the existing KMS-encrypted Secrets Manager pattern at runtime. Local development
continues to use `JWT_SECRET` from the ignored environment file.

## Consequences

The API role can read only its database, CockroachDB certificate, and JWT secret ARNs. Secret
rotation requires publishing a new `AWSCURRENT` version and recycling Lambda execution
environments; automatic rotation orchestration remains future work.
