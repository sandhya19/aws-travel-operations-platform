"""Contracts for the IMP-006 durable travel-case memory foundation."""

from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

import pytest

from travel_operations.services.travel_requests import TravelRequestNotFound, TravelRequestService


class MemoryRepository:
    def __init__(self) -> None:
        self.request = SimpleNamespace(id=uuid4(), status="SUBMITTED", requester_id="employee")
        self.session = SimpleNamespace(
            id=uuid4(), tenant_id="acme", user_id="employee", correlation_id=self.request.id
        )
        self.events: list[SimpleNamespace] = []

    def add(self, *_: object) -> SimpleNamespace:
        return self.request

    def create_agent_session(
        self, request_id: object, tenant_id: str, user_id: str, _: object
    ) -> SimpleNamespace:
        assert request_id == self.request.id
        assert (tenant_id, user_id) == ("acme", "employee")
        return self.session

    def create_agent_plan(self, *_: object) -> SimpleNamespace:
        return SimpleNamespace()

    def append_memory_event(
        self,
        session: SimpleNamespace,
        event_type: str,
        actor_id: str,
        source: str,
        payload: str,
    ) -> SimpleNamespace:
        event = SimpleNamespace(
            agent_session_id=session.id,
            event_type=event_type,
            actor_id=actor_id,
            source=source,
            payload=payload,
            created_at=datetime.now(UTC),
        )
        self.events.append(event)
        return event

    def get(self, request_id: object) -> SimpleNamespace | None:
        return self.request if request_id == self.request.id else None

    def get_for_tenant(self, request_id: object, tenant_id: str) -> SimpleNamespace | None:
        if request_id == self.request.id and tenant_id == "acme":
            return self.request
        return None

    def get_agent_session(
        self, request_id: object, tenant_id: str, user_id: str
    ) -> SimpleNamespace | None:
        if request_id == self.request.id and (tenant_id, user_id) == ("acme", "employee"):
            return self.session
        return None

    def get_agent_session_for_request(self, request_id: object) -> SimpleNamespace | None:
        return self.session if request_id == self.request.id else None

    def memory_events(self, session_id: object) -> list[SimpleNamespace]:
        assert session_id == self.session.id
        return self.events


def test_request_creation_starts_a_tenant_scoped_memory_session() -> None:
    repository = MemoryRepository()

    request = TravelRequestService(repository).create(  # type: ignore[arg-type]
        "employee",
        "acme",
        "GB",
        datetime(2026, 9, 1).date(),
        datetime(2026, 9, 3).date(),
        "Workshop",
    )

    assert request == repository.request
    assert repository.events[0].event_type == "travel_request_submitted"
    assert repository.events[0].actor_id == "employee"


def test_memory_retrieval_requires_the_request_owner_and_tenant() -> None:
    repository = MemoryRepository()
    service = TravelRequestService(repository)  # type: ignore[arg-type]
    repository.append_memory_event(
        repository.session, "travel_request_submitted", "employee", "api", "{}"
    )

    assert service.memory_events(repository.request.id, "employee", "acme") == repository.events
    with pytest.raises(TravelRequestNotFound):
        service.memory_events(repository.request.id, "employee", "other-tenant")


def test_request_retrieval_denies_a_matching_user_in_another_tenant() -> None:
    repository = MemoryRepository()
    service = TravelRequestService(repository)  # type: ignore[arg-type]

    with pytest.raises(TravelRequestNotFound):
        service.get(repository.request.id, "employee", "other-tenant")
