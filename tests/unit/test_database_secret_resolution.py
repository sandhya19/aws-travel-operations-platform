"""Database URL secret-resolution tests."""

from unittest.mock import Mock

import pytest

import travel_operations.database as database


def test_load_database_url_reads_secret_manager_when_no_direct_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("DATABASE_URL_SECRET_ARN", "arn:aws:secretsmanager:region:account:secret:db")
    secret_client = Mock()
    secret_client.get_secret_value.return_value = {
        "SecretString": "postgresql://user:password@example.com:26257/defaultdb"
    }
    monkeypatch.setattr(database.boto3, "client", lambda service: secret_client)

    database_url = database.load_database_url()

    assert database_url == "cockroachdb://user:password@example.com:26257/defaultdb"
    secret_client.get_secret_value.assert_called_once_with(
        SecretId="arn:aws:secretsmanager:region:account:secret:db"
    )
