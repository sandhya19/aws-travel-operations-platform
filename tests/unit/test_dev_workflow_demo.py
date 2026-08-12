"""Contracts for the dev-only workflow demonstration runner."""

import jwt
from scripts.run_dev_workflow_demo import make_token, run_workflow_demo


def test_demo_tokens_contain_subject_and_roles() -> None:
    secret = "test-secret-with-at-least-thirty-two-bytes"
    token = make_token("demo.employee", ["travel:approve"], secret)

    assert jwt.decode(token, secret, algorithms=["HS256"])["roles"] == ["travel:approve"]


def test_workflow_demo_returns_completed_evidence(monkeypatch: object) -> None:
    responses = iter(
        [
            (201, {"id": "request-123"}),
            (202, {}),
            (200, {"status": "COMPLETED"}),
        ]
    )
    monkeypatch.setattr("scripts.run_dev_workflow_demo.request_json", lambda *_: next(responses))

    result = run_workflow_demo("https://example.invalid", 1, "test-secret-with-at-least-thirty-two")

    assert result == {"request_id": "request-123", "status": "COMPLETED"}
