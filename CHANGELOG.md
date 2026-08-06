# Changelog

All notable changes are generated automatically from Conventional Commits by semantic-release.

## Unreleased

### Added

- Added the deployed EventBridge-to-Step-Functions approval vertical slice, SQS delivery DLQ,
  CockroachDB approval-task migration, and authenticated approval endpoint.

### Fixed

- Preserve the EventBridge request detail after the Step Functions approval callback so
  the IMP-003 workflow can mark the correct travel request complete.
- Added Linux Lambda packaging guidance, artifact hashing, and the CockroachDB dialect runtime dependency.
- Wired the development JWT secret into the deployed API Lambda as a sensitive Terraform input.

### Fixed

- Made travel-request repository sessions commit, roll back, and close deterministically.

### Fixed

- Restored the Alembic `0001` → `0002` → `0003` migration chain and added migration-lineage coverage.
