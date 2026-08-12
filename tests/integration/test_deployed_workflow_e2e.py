"""Opt-in authenticated cloud E2E coverage for the deployed dev vertical slice."""

import os

import pytest
from scripts.run_dev_workflow_demo import run_workflow_demo


@pytest.mark.cloud  # type: ignore[misc]
def test_deployed_request_approval_workflow_completes() -> None:
    """Create, approve, and verify a fresh dev request through the public API."""
    if os.getenv("RUN_CLOUD_E2E") != "1":
        pytest.skip("Set RUN_CLOUD_E2E=1 to run against the deployed dev stack")
    api_url = os.environ["DEV_API_URL"]
    jwt_secret = os.environ["JWT_SECRET"]

    result = run_workflow_demo(api_url, 120, jwt_secret)

    assert result["status"] == "COMPLETED"
    assert result["request_id"]
