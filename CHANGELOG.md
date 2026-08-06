# 1.0.0 (2026-08-06)


### Features

* add CockroachDB persistence ([9b6ab05](https://github.com/sandhya19/aws-travel-operations-platform/commit/9b6ab051e3fced3a7bb59410a0cb3bd246119fa9))
* add travel lifecycle events ([5abbb0d](https://github.com/sandhya19/aws-travel-operations-platform/commit/5abbb0d600275d11be15c0afdeff7e9e7a72a959))
* implement resilient travel workflow and AWS foundations ([606a3a5](https://github.com/sandhya19/aws-travel-operations-platform/commit/606a3a5d7a1d6a136c908e93735b1675be03084b))
* implement travel request API ([92bbdb1](https://github.com/sandhya19/aws-travel-operations-platform/commit/92bbdb1dcd436b37b0050620c8e0e24ae05f7804))
* initialize repository ([c3affa6](https://github.com/sandhya19/aws-travel-operations-platform/commit/c3affa608d6a9766a478985f797045f72fb6a57a))

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
