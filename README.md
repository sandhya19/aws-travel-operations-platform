# AI Travel Operations Platform

An enterprise platform for accelerating travel-request operations with explainable,
document-grounded AI recommendations. Human approvers retain all final decisions.

## Status

Milestone 0 establishes repository conventions and delivery tooling only. No runtime
application, cloud resources, or AI workflow has been implemented.

## Technology direction

- Python 3.12 and Poetry for application services
- AWS serverless and event-driven services, provisioned exclusively with Terraform
- CockroachDB Serverless as the transactional data store
- Amazon Bedrock and RAG for grounded recommendations

## Repository layout

| Path | Purpose |
| --- | --- |
| `src/` | Future Python application packages |
| `tests/` | Unit, integration, and contract test suites |
| `terraform/` | Reusable Terraform modules and environment composition |
| `docs/` | Architecture, ADRs, runbooks, prompts, and evaluation guidance |
| `prompts/` | Versioned prompt source files (future milestones) |
| `evaluations/` | Golden datasets and evaluation assets (future milestones) |
| `knowledge_base/` | Controlled source documents for retrieval (future milestones) |
| `.github/workflows/` | Continuous-integration workflows |

## Local setup

1. Install Python 3.12, Poetry 1.8+, Terraform 1.7+, and Git.
2. Run `poetry install --with dev`.
3. Run `poetry run pre-commit install`.
4. Validate with `poetry run ruff check .`, `poetry run black --check .`,
   `poetry run mypy src tests`, and `poetry run pytest`.

See [the roadmap](ROADMAP.md) and [architecture overview](docs/architecture/overview.md)
for the planned delivery sequence.
