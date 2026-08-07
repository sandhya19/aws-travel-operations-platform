# Demo data

Run `poetry run python scripts/seed_data.py` after migrations. It creates one safe, fictional travel request for `demo.employee`; it contains no PII or production policy content.

## Deployed dev demonstration

With `JWT_SECRET` set from the ignored `.env`, run:

```bash
python scripts/run_dev_workflow_demo.py --api-url "$(terraform -chdir=terraform/environments/dev output -raw travel_api_endpoint)"
```

The runner creates a request, waits for the callback task, submits authorized approval, and
prints its ID only after the API reports `COMPLETED`.
