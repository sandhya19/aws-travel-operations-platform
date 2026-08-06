"""Lambda handlers for the non-AI vertical-slice workflow."""

from uuid import UUID

from travel_operations.database import SessionFactory
from travel_operations.repositories.travel_requests import TravelRequestRepository
from travel_operations.services.travel_requests import TravelRequestService


def validate(event: dict[str, object], _: object) -> dict[str, object]:
    """Validate that the submitted request exists before human review."""
    return event


def handler(event: dict[str, object], context: object) -> dict[str, object] | None:
    """Route Step Functions invocations to the appropriate workflow action."""
    if "TaskToken" in event:
        request_approval(event, context)
        return None
    if event.get("action") == "COMPLETE":
        return complete(event, context)
    return validate(event, context)


def request_approval(event: dict[str, object], _: object) -> None:
    """Persist the Step Functions task token for a later human decision."""
    detail = event["detail"]
    with SessionFactory.begin() as session:
        TravelRequestService(TravelRequestRepository(session)).prepare_approval(
            UUID(str(detail["request_id"])), str(event["TaskToken"])
        )


def complete(event: dict[str, object], _: object) -> dict[str, object]:
    """Mark the approved request complete."""
    with SessionFactory.begin() as session:
        TravelRequestService(TravelRequestRepository(session)).complete(
            UUID(str(event["request_id"]))
        )
    return event
