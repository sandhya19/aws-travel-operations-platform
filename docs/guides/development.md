# Developer guide

Use small service/repository boundaries, version prompts, add tests with every tool, and run `ruff`, `black`, `mypy`, `pytest`, and `terraform fmt -check -recursive terraform` before review.

## Test tiers

The default suite is local and has no cloud dependency. Database integration tests run only with
`RUN_DATABASE_INTEGRATION=1` and a migrated `DATABASE_URL`. The authenticated deployed dev workflow
test is intentionally opt-in and creates a real request:

```bash
export DEV_API_URL="$(terraform -chdir=terraform/environments/dev output -raw travel_api_endpoint)"
export RUN_CLOUD_E2E=1
PYTHONPATH=src python -m pytest tests/integration/test_deployed_workflow_e2e.py -m cloud
```

Set `JWT_SECRET` from the secure dev value before this command. Never run cloud tests against a
production environment or print bearer tokens in logs.
