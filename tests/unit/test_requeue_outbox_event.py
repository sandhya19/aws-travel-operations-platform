"""Recovery contracts for failed outbox events."""

from types import SimpleNamespace

import pytest
from scripts.requeue_outbox_event import requeue


def test_requeue_resets_only_retry_state() -> None:
    event = SimpleNamespace(status="FAILED", attempts=3, last_error="EventBridge unavailable")

    requeue(event)

    assert event.status == "PENDING"
    assert event.attempts == 0
    assert event.last_error is None


def test_requeue_rejects_non_failed_event() -> None:
    with pytest.raises(ValueError, match="Only FAILED"):
        requeue(SimpleNamespace(status="PUBLISHED", attempts=0, last_error=None))
