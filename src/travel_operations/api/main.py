"""FastAPI Lambda entry point for travel-request metadata."""

import logging
import os
from collections.abc import Generator
from datetime import date, datetime
from typing import Any
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from mangum import Mangum
from pydantic import BaseModel, ConfigDict, Field, field_validator

from travel_operations.audit import record
from travel_operations.auth import AuthenticatedUser, require_approver, require_user
from travel_operations.database import session_scope
from travel_operations.events import publish_travel_request_created
from travel_operations.recovery import should_simulate_approval_callback_failure
from travel_operations.repositories.travel_requests import TravelRequestRepository
from travel_operations.security import AuditEvent, reject_prompt_injection
from travel_operations.services.itineraries import ItineraryRequirements
from travel_operations.services.travel_requests import TravelRequestNotFound, TravelRequestService

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format="%(message)s")


class TravelRequestCreate(BaseModel):
    """Metadata accepted when an employee submits a travel request."""

    destination_country: str = Field(min_length=2, max_length=2, pattern="^[A-Z]{2}$")
    departure_date: date
    return_date: date
    purpose: str = Field(min_length=3, max_length=500)

    @field_validator("purpose")
    @classmethod
    def reject_unsafe_purpose(cls, value: str) -> str:
        """Keep untrusted customer text out of current and future agent prompts."""
        return reject_prompt_injection(value)


class TravelRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    requester_id: str
    destination_country: str
    departure_date: date
    return_date: date
    purpose: str
    status: str


class ItineraryCreate(TravelRequestCreate):
    """Customer requirements accepted for a transparent, non-booking itinerary draft."""

    travelers: int = Field(ge=1, le=9)
    budget_amount: int = Field(ge=200, le=100_000)
    budget_currency: str = Field(default="GBP", min_length=3, max_length=3, pattern="^[A-Z]{3}$")
    interests: list[str] = Field(default_factory=list, max_length=5)

    @field_validator("interests")
    @classmethod
    def reject_unsafe_interests(cls, values: list[str]) -> list[str]:
        return [reject_prompt_injection(value) for value in values]


class ItineraryResponse(BaseModel):
    """A customer-visible coordinator result with durable specialist provenance."""

    status: str
    travel_request_id: UUID
    destination_country: str
    approval_required: bool
    booking_status: str
    delegations: list[dict[str, Any]]
    trust_notice: str


class MemoryEventResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    event_type: str
    actor_id: str
    source: str
    payload: str
    created_at: datetime


class ApprovalDecisionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    decision: str
    approver_id: str
    decided_at: datetime


app = FastAPI(title="Travel Operations API", version="0.1.0", openapi_url="/openapi.json")


def get_service() -> Generator[TravelRequestService, None, None]:
    """Create a request-scoped service with commit/rollback semantics."""
    yield from (
        TravelRequestService(TravelRequestRepository(session)) for session in session_scope()
    )


@app.exception_handler(TravelRequestNotFound)
async def travel_request_not_found(_: Request, error: TravelRequestNotFound) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(error)})


@app.exception_handler(RequestValidationError)
async def validation_error(_: Request, error: RequestValidationError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": error.errors()})


@app.post(
    "/travel-request", response_model=TravelRequestResponse, status_code=status.HTTP_201_CREATED
)
def create_travel_request(
    payload: TravelRequestCreate,
    user: AuthenticatedUser = Depends(require_user),  # noqa: B008
    service: TravelRequestService = Depends(get_service),  # noqa: B008
) -> TravelRequestResponse:
    """Create a metadata-only travel request for the authenticated employee."""
    if payload.return_date < payload.departure_date:
        return JSONResponse(
            status_code=422, content={"detail": "return_date must not precede departure_date"}
        )
    request = service.create(
        user.subject,
        user.tenant_id,
        payload.destination_country,
        payload.departure_date,
        payload.return_date,
        payload.purpose,
    )
    outbox_event = service.enqueue_request_created(request)
    service.commit()
    publish_travel_request_created(request.id, user.subject, outbox_event.id)
    service.mark_outbox_event_published(outbox_event.id)
    record(
        AuditEvent(
            actor_id=user.subject,
            action="travel_request_created",
            resource_id=str(request.id),
            correlation_id=str(outbox_event.id),
        )
    )
    return TravelRequestResponse.model_validate(request)


@app.post("/itineraries", response_model=ItineraryResponse, status_code=status.HTTP_201_CREATED)
def create_itinerary(
    payload: ItineraryCreate,
    user: AuthenticatedUser = Depends(require_user),  # noqa: B008
    service: TravelRequestService = Depends(get_service),  # noqa: B008
) -> ItineraryResponse | JSONResponse:
    """Create a travel case and auditable draft; it never books or self-approves travel."""
    if payload.return_date < payload.departure_date:
        return JSONResponse(
            status_code=422, content={"detail": "return_date must not precede departure_date"}
        )
    request = service.create(
        user.subject,
        user.tenant_id,
        payload.destination_country,
        payload.departure_date,
        payload.return_date,
        payload.purpose,
    )
    draft = service.create_itinerary_draft(
        request.id,
        user.tenant_id,
        user.subject,
        ItineraryRequirements(
            payload.travelers,
            payload.budget_amount,
            payload.budget_currency,
            tuple(payload.interests),
        ),
    )
    outbox_event = service.enqueue_request_created(request)
    service.commit()
    publish_travel_request_created(request.id, user.subject, outbox_event.id)
    service.mark_outbox_event_published(outbox_event.id)
    record(
        AuditEvent(
            actor_id=user.subject,
            action="itinerary_draft_created",
            resource_id=str(request.id),
            correlation_id=str(outbox_event.id),
        )
    )
    return ItineraryResponse.model_validate(draft)


@app.post("/travel-request/{request_id}/approval", status_code=status.HTTP_202_ACCEPTED)
def approve_travel_request(
    request_id: UUID,
    user: AuthenticatedUser = Depends(require_approver),  # noqa: B008
    service: TravelRequestService = Depends(get_service),  # noqa: B008
) -> dict[str, str]:
    """Resolve the waiting workflow task with an authenticated human approval."""
    task_token = service.approve(request_id, user.subject, user.tenant_id)
    service.commit()
    if should_simulate_approval_callback_failure():
        record(
            AuditEvent(
                actor_id=user.subject,
                action="approval_callback_failure_simulated",
                resource_id=str(request_id),
                correlation_id=str(request_id),
            )
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Approval callback failure simulated; run the recovery drill replay command",
        )
    import boto3

    boto3.client("stepfunctions").send_task_success(
        taskToken=task_token, output='{"approved":true}'
    )
    record(
        AuditEvent(
            actor_id=user.subject,
            action="travel_request_approved",
            resource_id=str(request_id),
            correlation_id=str(request_id),
        )
    )
    return {"status": "APPROVED"}


@app.post("/travel-request/{request_id}/rejection", status_code=status.HTTP_202_ACCEPTED)
def reject_travel_request(
    request_id: UUID,
    user: AuthenticatedUser = Depends(require_approver),  # noqa: B008
    service: TravelRequestService = Depends(get_service),  # noqa: B008
) -> dict[str, str]:
    """Resolve the waiting workflow task with an authenticated rejection."""
    task_token = service.reject(request_id, user.subject, user.tenant_id)
    service.commit()
    import boto3

    boto3.client("stepfunctions").send_task_success(
        taskToken=task_token, output='{"approved":false}'
    )
    record(
        AuditEvent(
            actor_id=user.subject,
            action="travel_request_rejected",
            resource_id=str(request_id),
            correlation_id=str(request_id),
        )
    )
    return {"status": "REJECTED"}


@app.get("/travel-request/{request_id}", response_model=TravelRequestResponse)
def get_travel_request(
    request_id: UUID,
    user: AuthenticatedUser = Depends(require_user),  # noqa: B008
    service: TravelRequestService = Depends(get_service),  # noqa: B008
) -> TravelRequestResponse:
    """Return a request only when it belongs to the authenticated employee."""
    request = service.get(request_id, user.subject, user.tenant_id)
    record(
        AuditEvent(
            actor_id=user.subject,
            action="travel_request_retrieved",
            resource_id=str(request.id),
            correlation_id=str(request.id),
        )
    )
    return TravelRequestResponse.model_validate(request)


@app.get("/travel-request/{request_id}/memory", response_model=list[MemoryEventResponse])
def get_travel_request_memory(
    request_id: UUID,
    user: AuthenticatedUser = Depends(require_user),  # noqa: B008
    service: TravelRequestService = Depends(get_service),  # noqa: B008
) -> list[MemoryEventResponse]:
    """Return the authenticated requester's durable, ordered travel-case history."""
    return [
        MemoryEventResponse.model_validate(event)
        for event in service.memory_events(request_id, user.subject, user.tenant_id)
    ]


@app.get(
    "/travel-request/{request_id}/approval-history",
    response_model=list[ApprovalDecisionResponse],
)
def get_approval_history(
    request_id: UUID,
    user: AuthenticatedUser = Depends(require_approver),  # noqa: B008
    service: TravelRequestService = Depends(get_service),  # noqa: B008
) -> list[ApprovalDecisionResponse]:
    """Return immutable decisions to an authorized travel approver."""
    return [
        ApprovalDecisionResponse.model_validate(decision)
        for decision in service.approval_history(request_id, user.tenant_id)
    ]


handler = Mangum(app, lifespan="off")
