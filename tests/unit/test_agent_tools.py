from datetime import date
from types import SimpleNamespace
from uuid import uuid4

import pytest

import travel_operations.agent_tools as agent_tools
from travel_operations.agent_tools import handler


def test_lambda_tool_response_includes_action_group() -> None:
    response = handler({"actionGroup": "policy", "function": "lookup_policy"}, None)
    assert response["response"]["actionGroup"] == "policy"


class ContextManager:
    def __enter__(self) -> object:
        return object()

    def __exit__(self, *_: object) -> None:
        return None


class FakeSessionFactory:
    @staticmethod
    def begin() -> ContextManager:
        return ContextManager()


class RecordingRepository:
    def __init__(self) -> None:
        self.session = SimpleNamespace(
            id=uuid4(), tenant_id="acme", user_id="employee", correlation_id=uuid4()
        )
        self.executions: list[tuple[object, ...]] = []
        self.events: list[tuple[object, ...]] = []

    def get_agent_session(self, _: object, tenant_id: str, user_id: str) -> SimpleNamespace | None:
        if (tenant_id, user_id) == ("acme", "employee"):
            return self.session
        return None

    def get_for_tenant(self, _: object, tenant_id: str) -> SimpleNamespace | None:
        if tenant_id != "acme":
            return None
        return SimpleNamespace(
            requester_id="employee",
            destination_country="GB",
            departure_date=date(2026, 11, 10),
            return_date=date(2026, 11, 14),
            purpose="Customer workshop",
        )

    def create_tool_execution(self, *args: object) -> tuple[SimpleNamespace, bool]:
        self.executions.append(args)
        return SimpleNamespace(), True

    def append_memory_event(self, *args: object) -> SimpleNamespace:
        self.events.append(args)
        return SimpleNamespace()


def test_tool_invocation_records_durable_provenance(monkeypatch: pytest.MonkeyPatch) -> None:
    repository = RecordingRepository()
    monkeypatch.setattr(agent_tools, "SessionFactory", FakeSessionFactory)
    monkeypatch.setattr(agent_tools, "TravelRequestRepository", lambda _: repository)

    response = handler(
        {
            "actionGroup": "policy",
            "function": "lookup_policy",
            "invocationId": "tool-call-1",
            "parameters": [{"name": "country", "value": "GB"}],
            "sessionAttributes": {
                "travel_request_id": str(uuid4()),
                "tenant_id": "acme",
                "user_id": "employee",
            },
        },
        None,
    )

    assert response["response"]["function"] == "lookup_policy"
    assert repository.executions[0][1:3] == ("lookup_policy", "tool-call-1")
    assert repository.events[0][1] == "tool_execution_completed"


def test_itinerary_tool_returns_a_non_booking_draft(monkeypatch: pytest.MonkeyPatch) -> None:
    repository = RecordingRepository()
    monkeypatch.setattr(agent_tools, "SessionFactory", FakeSessionFactory)
    monkeypatch.setattr(agent_tools, "TravelRequestRepository", lambda _: repository)

    response = handler(
        {
            "actionGroup": "travel_operations_tools",
            "function": "itinerary_draft",
            "sessionAttributes": {
                "travel_request_id": str(uuid4()),
                "tenant_id": "acme",
                "user_id": "employee",
            },
        },
        None,
    )

    body = response["response"]["functionResponse"]["responseBody"]["TEXT"]["body"]
    assert '"status": "DRAFT"' in body
    assert '"booking": "NOT_BOOKED"' in body


def test_tool_invocation_does_not_query_an_unscoped_session(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository = RecordingRepository()
    monkeypatch.setattr(agent_tools, "SessionFactory", FakeSessionFactory)
    monkeypatch.setattr(agent_tools, "TravelRequestRepository", lambda _: repository)

    handler(
        {
            "actionGroup": "policy",
            "function": "lookup_policy",
            "sessionAttributes": {"travel_request_id": str(uuid4())},
        },
        None,
    )

    assert repository.executions == []
