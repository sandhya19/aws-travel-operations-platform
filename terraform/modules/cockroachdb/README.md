# CockroachDB connectivity module

Creates a least-privilege outbound security group for TLS PostgreSQL-compatible
CockroachDB Serverless access. It does not provision a database; credentials remain in
Secrets Manager and CIDRs must be sourced from CockroachDB's published network ranges.
