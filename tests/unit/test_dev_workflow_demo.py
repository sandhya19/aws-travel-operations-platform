"""Contracts for the dev-only workflow demonstration runner."""

import jwt
from scripts.run_dev_workflow_demo import make_token


def test_demo_tokens_contain_subject_and_roles() -> None:
    secret = "test-secret-with-at-least-thirty-two-bytes"
    token = make_token("demo.employee", ["travel:approve"], secret)

    assert jwt.decode(token, secret, algorithms=["HS256"])["roles"] == ["travel:approve"]
