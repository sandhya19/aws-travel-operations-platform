"""Bounded, explainable itinerary orchestration for a saved travel case."""

import json
from dataclasses import asdict, dataclass
from datetime import date, timedelta
from typing import Protocol, cast
from uuid import UUID, uuid4

from travel_operations.repositories.travel_requests import TravelRequestRepository


class TravelCase(Protocol):
    """The persisted travel-request fields visible to itinerary specialists."""

    requester_id: str
    destination_country: str
    departure_date: date
    return_date: date


@dataclass(frozen=True)
class ItineraryRequirements:
    """Validated customer preferences used by the specialist plan."""

    travelers: int
    budget_amount: int
    budget_currency: str
    interests: tuple[str, ...]


def create_itinerary_draft(
    repository: TravelRequestRepository,
    request_id: UUID,
    tenant_id: str,
    user_id: str,
    requirements: ItineraryRequirements,
) -> dict[str, object]:
    """Delegate a bounded specialist plan and persist every result as case provenance."""
    request = repository.get_for_tenant(request_id, tenant_id)
    session = repository.get_agent_session(request_id, tenant_id, user_id)
    if request is None or request.requester_id != user_id or session is None:
        raise ValueError("A tenant-scoped travel case is required for itinerary orchestration")

    input_payload = json.dumps(asdict(requirements), sort_keys=True)
    repository.create_agent_plan(
        session,
        "itinerary_orchestration",
        "v1",
        "travel_operations.itinerary_coordinator",
        json.dumps(
            {
                "steps": [
                    "profile_requirements",
                    "policy_compliance_review",
                    "travel_risk_review",
                    "inventory_research",
                    "itinerary_draft",
                    "financial_triage",
                ]
            }
        ),
    )

    travel_case = cast(TravelCase, request)
    specialists = [
        ("profile_agent", _profile_result(travel_case, requirements)),
        ("policy_compliance_agent", _policy_result(travel_case)),
        ("travel_risk_agent", _risk_result(travel_case)),
        ("inventory_research_agent", _inventory_result(travel_case, requirements)),
        ("itinerary_agent", _itinerary_result(travel_case, requirements)),
        ("sales_orchestrator", _financial_result(requirements)),
    ]
    delegations: list[dict[str, object]] = []
    for agent, result in specialists:
        output_payload = json.dumps(result, sort_keys=True)
        repository.create_tool_execution(
            session,
            agent,
            str(uuid4()),
            input_payload,
            output_payload,
        )
        repository.append_memory_event(
            session,
            "itinerary_specialist_completed",
            agent,
            "travel_operations.itinerary_coordinator",
            json.dumps({"agent": agent, "status": result["status"]}),
        )
        delegations.append({"agent": agent, "result": result})

    draft = {
        "status": "DRAFT_REQUIRES_HUMAN_APPROVAL",
        "travel_request_id": str(request_id),
        "destination_country": request.destination_country,
        "approval_required": True,
        "booking_status": "NOT_BOOKED",
        "delegations": delegations,
        "trust_notice": (
            "Policy, risk, and inventory results are review inputs. No supplier availability, "
            "price, policy approval, or booking is asserted without an authorized integration "
            "and human approval."
        ),
    }
    repository.append_memory_event(
        session,
        "itinerary_draft_prepared",
        "travel_itinerary_coordinator",
        "travel_operations.itinerary_coordinator",
        json.dumps(draft, sort_keys=True),
    )
    return draft


def _profile_result(request: TravelCase, requirements: ItineraryRequirements) -> dict[str, object]:
    return {
        "status": "PROFILED",
        "destination_country": request.destination_country,
        "departure_date": request.departure_date.isoformat(),
        "return_date": request.return_date.isoformat(),
        "travelers": requirements.travelers,
        "interests": list(requirements.interests),
    }


def _policy_result(request: TravelCase) -> dict[str, object]:
    return {
        "status": "REQUIRES_HUMAN_POLICY_REVIEW",
        "destination_country": request.destination_country,
        "reason": "No authorized model-backed policy decision is exposed by this draft service.",
    }


def _risk_result(request: TravelCase) -> dict[str, object]:
    return {
        "status": "REQUIRES_HUMAN_RISK_REVIEW",
        "destination_country": request.destination_country,
        "reason": "No external duty-of-care provider is configured.",
    }


def _inventory_result(
    request: TravelCase, requirements: ItineraryRequirements
) -> dict[str, object]:
    return {
        "status": "RESEARCH_REQUIRED",
        "destination_country": request.destination_country,
        "segment_budget": {
            "transport": round(requirements.budget_amount * 0.45),
            "lodging": round(requirements.budget_amount * 0.35),
        },
        "reason": "Live GDS and hotel supplier integrations are not configured.",
    }


def _itinerary_result(
    request: TravelCase, requirements: ItineraryRequirements
) -> dict[str, object]:
    day_count = (request.return_date - request.departure_date).days + 1
    interests = requirements.interests or ("local culture",)
    daily_plan = []
    for offset in range(day_count):
        activity = interests[offset % len(interests)]
        daily_plan.append(
            {
                "date": (request.departure_date + timedelta(days=offset)).isoformat(),
                "theme": activity,
                "status": "DRAFT_ACTIVITY_RESEARCH_REQUIRED",
            }
        )
    return {"status": "DRAFT", "daily_plan": daily_plan, "booking": "NOT_BOOKED"}


def _financial_result(requirements: ItineraryRequirements) -> dict[str, object]:
    allocation = {
        "transport": round(requirements.budget_amount * 0.45),
        "lodging": round(requirements.budget_amount * 0.35),
        "activities": round(requirements.budget_amount * 0.15),
        "contingency": round(requirements.budget_amount * 0.05),
    }
    return {
        "status": "BUDGET_ALLOCATION_DRAFT",
        "currency": requirements.budget_currency,
        "total_budget": requirements.budget_amount,
        "allocation": allocation,
        "allocation_total": sum(allocation.values()),
    }
