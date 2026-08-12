"""Customer-facing itinerary orchestration contracts."""

import json
from datetime import date
from types import SimpleNamespace
from uuid import uuid4

from travel_operations.services.itineraries import ItineraryRequirements, create_itinerary_draft


class RecordingRepository:
    def __init__(self) -> None:
        self.request_id = uuid4()
        self.session = SimpleNamespace(id=uuid4(), tenant_id="acme", user_id="employee")
        self.tools: list[tuple[object, ...]] = []
        self.events: list[tuple[object, ...]] = []
        self.request = SimpleNamespace(
            requester_id="employee",
            destination_country="GB",
            departure_date=date(2026, 11, 10),
            return_date=date(2026, 11, 12),
        )

    def get_for_tenant(self, request_id: object, tenant_id: str) -> object | None:
        return self.request if request_id == self.request_id and tenant_id == "acme" else None

    def get_agent_session(self, request_id: object, tenant_id: str, user_id: str) -> object | None:
        if request_id == self.request_id and (tenant_id, user_id) == ("acme", "employee"):
            return self.session
        return None

    def create_agent_plan(self, *_: object) -> object:
        return object()

    def create_tool_execution(self, *args: object) -> tuple[object, bool]:
        self.tools.append(args)
        return object(), True

    def append_memory_event(self, *args: object) -> object:
        self.events.append(args)
        return object()


def test_itinerary_draft_delegates_and_records_a_non_booking_result() -> None:
    repository = RecordingRepository()

    draft = create_itinerary_draft(
        repository,  # type: ignore[arg-type]
        repository.request_id,
        "acme",
        "employee",
        ItineraryRequirements(2, 2_000, "GBP", ("food", "art")),
    )

    assert draft["status"] == "DRAFT_REQUIRES_HUMAN_APPROVAL"
    assert draft["booking_status"] == "NOT_BOOKED"
    assert [entry["agent"] for entry in draft["delegations"]] == [
        "profile_agent",
        "policy_compliance_agent",
        "travel_risk_agent",
        "inventory_research_agent",
        "itinerary_agent",
        "sales_orchestrator",
    ]
    assert len(repository.tools) == 6
    final_event = json.loads(repository.events[-1][4])
    assert final_event["approval_required"] is True
    assert "supplier availability" in final_event["trust_notice"]
