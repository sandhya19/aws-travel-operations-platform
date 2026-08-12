"""Lambda handlers for the non-AI vertical-slice workflow."""

from uuid import UUID

from travel_operations.database import SessionFactory
from travel_operations.repositories.travel_requests import TravelRequestRepository
from travel_operations.services.travel_requests import TravelRequestService


def validate(event: dict[str, object], _: object) -> dict[str, object]:
    """Validate that the submitted request exists before human review."""
    detail = event.get("detail")
    if isinstance(detail, dict) and "request_id" in detail:
        with SessionFactory.begin() as session:
            TravelRequestService(TravelRequestRepository(session)).record_workflow_checkpoint(
                UUID(str(detail["request_id"])), "VALIDATED", {"status": "VALIDATED"}
            )
    return event


def handler(event: dict[str, object], context: object) -> dict[str, object] | None:
    """Route Step Functions invocations to the appropriate workflow action."""
    if "TaskToken" in event:
        request_approval(event, context)
        return None
    if event.get("action") == "COMPLETE":
        return complete(event, context)
    if event.get("action") == "REJECT":
        return reject(event, context)
    return validate(event, context)


def request_approval(event: dict[str, object], _: object) -> None:
    """Persist the Step Functions task token for a later human decision."""
    detail = event["detail"]
    with SessionFactory.begin() as session:
        service = TravelRequestService(TravelRequestRepository(session))
        request_id = UUID(str(detail["request_id"]))
        service.prepare_approval(request_id, str(event["TaskToken"]))
        service.record_memory_event(
            request_id,
            "approval_requested",
            "travel_operations.workflow",
            "travel_operations.workflow",
            {"status": "PENDING"},
        )
        service.record_workflow_checkpoint(request_id, "AWAITING_APPROVAL", {"status": "PENDING"})


def complete(event: dict[str, object], _: object) -> dict[str, object]:
    """Mark the approved request complete."""
    with SessionFactory.begin() as session:
        request_id = UUID(str(event["request_id"]))
        service = TravelRequestService(TravelRequestRepository(session))
        service.complete(request_id)
        service.record_workflow_checkpoint(request_id, "COMPLETED", {"status": "COMPLETED"})
    return event


def reject(event: dict[str, object], _: object) -> dict[str, object]:
    """Mark the request rejected after the human decision callback."""
    with SessionFactory.begin() as session:
        TravelRequestService(TravelRequestRepository(session)).reject_complete(
            UUID(str(event["request_id"]))
        )
    return event
