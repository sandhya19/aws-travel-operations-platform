"""Retry contracts for durable workflow outbox publication."""

import json
from types import SimpleNamespace
from uuid import uuid4

from travel_operations import outbox_dispatcher


class FakeSession:
    def __enter__(self) -> "FakeSession":
        return self

    def __exit__(self, *_: object) -> None:
        return None

    def commit(self) -> None:
        return None


class FakeService:
    def __init__(self, event: object, exhausted: bool = False) -> None:
        self._event = event
        self._exhausted = exhausted
        self.published: list[object] = []
        self.failures: list[tuple[object, str, int]] = []

    def pending_outbox_events(self) -> list[object]:
        return [self._event]

    def mark_outbox_event_published(self, event_id: object) -> None:
        self.published.append(event_id)

    def record_outbox_failure(self, event_id: object, error: str, max_attempts: int) -> bool:
        self.failures.append((event_id, error, max_attempts))
        return self._exhausted


def test_dispatcher_marks_successful_event_published(monkeypatch: object) -> None:
    event = SimpleNamespace(
        id=uuid4(),
        travel_request_id=uuid4(),
        payload=json.dumps({"requester_id": "employee"}),
    )
    service = FakeService(event)
    monkeypatch.setattr(outbox_dispatcher, "SessionFactory", lambda: FakeSession())
    monkeypatch.setattr(outbox_dispatcher, "TravelRequestService", lambda _: service)
    monkeypatch.setattr(outbox_dispatcher, "publish_travel_request_created", lambda *_: None)

    assert outbox_dispatcher.handler({}, object()) == {"published": 1, "failed": 0, "dlq": 0}
    assert service.published == [event.id]


def test_dispatcher_leaves_failed_event_pending_for_retry(monkeypatch: object) -> None:
    event = SimpleNamespace(
        id=uuid4(),
        travel_request_id=uuid4(),
        payload=json.dumps({"requester_id": "employee"}),
    )
    service = FakeService(event)
    monkeypatch.setattr(outbox_dispatcher, "SessionFactory", lambda: FakeSession())
    monkeypatch.setattr(outbox_dispatcher, "TravelRequestService", lambda _: service)
    monkeypatch.setattr(
        outbox_dispatcher,
        "publish_travel_request_created",
        lambda *_: (_ for _ in ()).throw(RuntimeError("EventBridge unavailable")),
    )

    assert outbox_dispatcher.handler({}, object()) == {"published": 0, "failed": 1, "dlq": 0}
    assert service.failures == [(event.id, "EventBridge unavailable", 3)]


def test_dispatcher_routes_exhausted_event_to_dlq(monkeypatch: object) -> None:
    event = SimpleNamespace(
        id=uuid4(),
        travel_request_id=uuid4(),
        event_type="TravelRequestCreated",
        payload=json.dumps({"requester_id": "employee"}),
    )
    service = FakeService(event, exhausted=True)
    monkeypatch.setattr(outbox_dispatcher, "SessionFactory", lambda: FakeSession())
    monkeypatch.setattr(outbox_dispatcher, "TravelRequestService", lambda _: service)
    monkeypatch.setattr(
        outbox_dispatcher,
        "publish_travel_request_created",
        lambda *_: (_ for _ in ()).throw(RuntimeError("EventBridge unavailable")),
    )
    dlq = []
    monkeypatch.setattr(outbox_dispatcher, "send_to_dlq", lambda *args: dlq.append(args))

    assert outbox_dispatcher.handler({}, object()) == {"published": 0, "failed": 1, "dlq": 1}
    assert len(dlq) == 1
    assert dlq[0][0] == event
    assert isinstance(dlq[0][1], RuntimeError)


def test_dlq_message_uses_error_type_without_raw_failure_details(monkeypatch: object) -> None:
    event = SimpleNamespace(id=uuid4(), event_type="TravelRequestCreated")
    message: dict[str, object] = {}
    monkeypatch.setenv("OUTBOX_DLQ_URL", "https://sqs.example.test/dlq")
    client = SimpleNamespace(
        send_message=lambda **kwargs: message.update(kwargs),
    )
    monkeypatch.setattr(outbox_dispatcher.boto3, "client", lambda _: client)

    outbox_dispatcher.send_to_dlq(event, RuntimeError("contains an internal ARN"))

    assert json.loads(str(message["MessageBody"])) == {
        "event_id": str(event.id),
        "event_type": "TravelRequestCreated",
        "error_type": "RuntimeError",
    }
