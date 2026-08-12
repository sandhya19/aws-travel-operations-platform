"""Recovery contracts for the approval callback replay command."""

from types import SimpleNamespace
from uuid import uuid4

import pytest
from scripts import replay_approved_callback


class FakeSession:
    def __enter__(self) -> "FakeSession":
        return self

    def __exit__(self, *_: object) -> None:
        return None


def test_replay_sends_approved_callback(monkeypatch: pytest.MonkeyPatch) -> None:
    request_id = uuid4()
    calls: dict[str, object] = {}
    service = SimpleNamespace(approved_callback_token_for_replay=lambda _: "task-token")
    monkeypatch.setattr(replay_approved_callback, "SessionFactory", lambda: FakeSession())
    monkeypatch.setattr(replay_approved_callback, "TravelRequestRepository", lambda _: object())
    monkeypatch.setattr(replay_approved_callback, "TravelRequestService", lambda _: service)
    monkeypatch.setattr(
        replay_approved_callback.boto3,
        "client",
        lambda _: SimpleNamespace(send_task_success=lambda **kwargs: calls.update(kwargs)),
    )

    replay_approved_callback.replay(request_id)

    assert calls == {"taskToken": "task-token", "output": '{"approved":true,"replayed":true}'}
