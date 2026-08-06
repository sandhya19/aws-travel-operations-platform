# Installation

Install Python 3.12, Poetry, Terraform, and Docker. Run `poetry install --with dev`, copy environment values from your secure secret store, set `JWT_SECRET` and `DATABASE_URL`, then run `poetry run alembic upgrade head`.

Alembic revisions are linear: `0001` travel metadata, `0002` versioned knowledge chunks,
and `0003` evaluation history. Verify setup with `poetry run pytest tests/unit/test_migration_lineage.py tests/integration/test_migration_contract.py`.
