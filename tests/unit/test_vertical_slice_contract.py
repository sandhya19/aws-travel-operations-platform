"""Contract checks for the deployable IMP-003 workflow definition."""

import re
from pathlib import Path


def test_approval_callback_preserves_request_detail() -> None:
    """Completion must retain the EventBridge request identifier after approval."""
    definition = (
        Path(__file__).parents[2] / "terraform" / "environments" / "dev" / "vertical_slice.tf"
    ).read_text(encoding="utf-8")

    assert 'ResultPath = "$.approval"' in definition
    assert '"request_id.$" = "$.detail.request_id"' in definition
    assert 'Next = "WorkflowFailed"' in definition
    assert 'WorkflowFailed = { Type = "Fail"' in definition


def test_lambdas_read_database_url_from_the_kms_encrypted_secret() -> None:
    """Both Lambda roles must be able to read and decrypt the database secret."""
    definition = (
        Path(__file__).parents[2] / "terraform" / "environments" / "dev" / "vertical_slice.tf"
    ).read_text(encoding="utf-8")

    assert re.search(r"DATABASE_URL_SECRET_ARN\s+= module\.database_secret\.secret_arn", definition)
    assert definition.count('Action = ["secretsmanager:GetSecretValue"]') >= 2
    assert definition.count('Action = ["kms:Decrypt"]') >= 2
