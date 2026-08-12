"""AgentCore typed-tool handler with durable execution provenance."""

import json
from typing import Any
from uuid import UUID, uuid4

from travel_operations.database import SessionFactory
from travel_operations.repositories.travel_requests import TravelRequestRepository

SPECIALIST_TOOLS = {
    "profile_requirements": "profile_agent",
    "policy_compliance_review": "policy_compliance_agent",
    "travel_risk_review": "travel_risk_agent",
    "inventory_research": "inventory_research_agent",
    "itinerary_draft": "itinerary_agent",
    "financial_triage": "sales_orchestrator",
    "lookup_policy": "policy_compliance_agent",
}


def _travel_request_context(event: dict[str, Any]) -> tuple[UUID, str, str] | None:
    """Read the tenant-bound case context supplied by the owning workflow."""
    attributes = event.get("sessionAttributes", {})
    if not isinstance(attributes, dict):
        return None
    request_id = attributes.get("travel_request_id")
    tenant_id = attributes.get("tenant_id")
    user_id = attributes.get("user_id")
    if (
        not isinstance(request_id, str)
        or not request_id
        or not isinstance(tenant_id, str)
        or not tenant_id
        or not isinstance(user_id, str)
        or not user_id
    ):
        return None
    try:
        return UUID(request_id), tenant_id, user_id
    except ValueError:
        return None


def handler(event: dict[str, Any], _: Any) -> dict[str, Any]:
    """Return the typed tool response consumed by the AgentCore coordinator."""
    action = event.get("actionGroup", "unknown")
    function = event.get("function", "unknown")
    response: dict[str, Any] = {
        "messageVersion": "1.0",
        "response": {
            "actionGroup": action,
            "function": function,
            "functionResponse": {
                "responseBody": {"TEXT": {"body": "Tool execution requires its owning workflow."}}
            },
        },
    }
    context = _travel_request_context(event)
    if context is None:
        return response
    request_id, tenant_id, user_id = context
    if function not in SPECIALIST_TOOLS:
        return response

    with SessionFactory.begin() as session:
        repository = TravelRequestRepository(session)
        agent_session = repository.get_agent_session(request_id, tenant_id, user_id)
        if agent_session is None:
            raise ValueError("A durable agent session is required for tool execution")
        request = repository.get_for_tenant(request_id, tenant_id)
        if request is None or request.requester_id != user_id:
            raise ValueError("A tenant-scoped travel request is required for tool execution")
        body = _specialist_result(str(function), request)
        response["response"]["functionResponse"]["responseBody"]["TEXT"]["body"] = body
        _, created = repository.create_tool_execution(
            agent_session,
            str(function),
            str(event.get("invocationId", uuid4())),
            json.dumps(event.get("parameters", [])),
            json.dumps(response["response"]["functionResponse"]),
        )
        if created:
            repository.append_memory_event(
                agent_session,
                "tool_execution_completed",
                "travel_operations.agent_tools",
                "travel_operations.agent_tools",
                json.dumps({"tool_name": str(function), "status": "COMPLETED"}),
            )
    return response


def _specialist_result(function: str, request: Any) -> str:
    """Return a transparent, non-booking specialist result from durable request metadata."""
    if function == "itinerary_draft":
        return json.dumps(
            {
                "status": "DRAFT",
                "destination_country": request.destination_country,
                "departure_date": request.departure_date.isoformat(),
                "return_date": request.return_date.isoformat(),
                "purpose": request.purpose,
                "booking": "NOT_BOOKED",
            }
        )
    if function == "profile_requirements":
        return json.dumps(
            {
                "status": "PROFILED",
                "destination_country": request.destination_country,
                "departure_date": request.departure_date.isoformat(),
                "return_date": request.return_date.isoformat(),
            }
        )
    if function == "inventory_research":
        return json.dumps(
            {
                "status": "RESEARCH_REQUIRED",
                "destination_country": request.destination_country,
                "reason": "Live GDS and hotel supplier integrations are not configured.",
            }
        )
    if function == "financial_triage":
        return json.dumps(
            {
                "status": "REQUIRES_HUMAN_FINANCIAL_REVIEW",
                "reason": "No customer budget is attached to this runtime invocation.",
            }
        )
    if function == "policy_compliance_review":
        return json.dumps(
            {
                "status": "REQUIRES_HUMAN_POLICY_REVIEW",
                "destination_country": request.destination_country,
                "reason": "No authorized model-backed policy decision is exposed by this tool.",
            }
        )
    return json.dumps(
        {
            "status": "REQUIRES_HUMAN_RISK_REVIEW",
            "destination_country": request.destination_country,
            "reason": "No external duty-of-care provider is configured.",
        }
    )
