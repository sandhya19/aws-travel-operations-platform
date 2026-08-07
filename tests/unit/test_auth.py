"""Authorization tests for travel-request actions."""

from unittest.mock import Mock

import pytest
from fastapi import HTTPException

import travel_operations.auth as auth
from travel_operations.auth import AuthenticatedUser, require_approver


def test_approver_role_is_required() -> None:
    with pytest.raises(HTTPException, match="Approver role required") as error:
        require_approver(AuthenticatedUser(subject="employee", roles=frozenset()))

    assert error.value.status_code == 403


def test_approver_role_is_accepted() -> None:
    approver = AuthenticatedUser(subject="travel.manager", roles=frozenset({"travel:approve"}))

    assert require_approver(approver) == approver


def test_jwt_secret_reads_secrets_manager_when_local_secret_is_absent(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("JWT_SECRET", raising=False)
    monkeypatch.setenv("JWT_SECRET_SECRET_ARN", "arn:aws:secretsmanager:region:account:secret:jwt")
    client = Mock()
    client.get_secret_value.return_value = {"SecretString": "runtime-secret"}
    monkeypatch.setattr(auth.boto3, "client", lambda _: client)
    auth.load_jwt_secret.cache_clear()

    assert auth.load_jwt_secret() == "runtime-secret"
    client.get_secret_value.assert_called_once()
