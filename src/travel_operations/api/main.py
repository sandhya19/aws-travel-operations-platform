"""FastAPI Lambda entry point for travel-request metadata."""

import logging
import os
from collections.abc import Generator
from datetime import date
from uuid import UUID

from fastapi import Depends, FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from mangum import Mangum
from pydantic import BaseModel, ConfigDict, Field

from travel_operations.auth import AuthenticatedUser, require_approver, require_user
from travel_operations.database import session_scope
from travel_operations.events import publish_travel_request_created
from travel_operations.repositories.travel_requests import TravelRequestRepository
from travel_operations.services.travel_requests import TravelRequestNotFound, TravelRequestService

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format="%(message)s")
logger = logging.getLogger(__name__)


class TravelRequestCreate(BaseModel):
    """Metadata accepted when an employee submits a travel request."""

    destination_country: str = Field(min_length=2, max_length=2, pattern="^[A-Z]{2}$")
    departure_date: date
    return_date: date
    purpose: str = Field(min_length=3, max_length=500)


class TravelRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    requester_id: str
    destination_country: str
    departure_date: date
    return_date: date
    purpose: str
    status: str


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
    user: AuthenticatedUser = Depends(require_user),
    service: TravelRequestService = Depends(get_service),
) -> TravelRequestResponse:
    """Create a metadata-only travel request for the authenticated employee."""
    if payload.return_date < payload.departure_date:
        return JSONResponse(
            status_code=422, content={"detail": "return_date must not precede departure_date"}
        )
    request = service.create(
        user.subject,
        payload.destination_country,
        payload.departure_date,
        payload.return_date,
        payload.purpose,
    )
    outbox_event = service.enqueue_request_created(request)
    service.commit()
    publish_travel_request_created(request.id, user.subject, outbox_event.id)
    service.mark_outbox_event_published(outbox_event.id)
    logger.info("travel_request_created id=%s requester_id=%s", request.id, user.subject)
    return TravelRequestResponse.model_validate(request)


@app.post("/travel-request/{request_id}/approval", status_code=status.HTTP_202_ACCEPTED)
def approve_travel_request(
    request_id: UUID,
    user: AuthenticatedUser = Depends(require_approver),
    service: TravelRequestService = Depends(get_service),
) -> dict[str, str]:
    """Resolve the waiting workflow task with an authenticated human approval."""
    task_token = service.approve(request_id, user.subject)
    service.commit()
    import boto3

    boto3.client("stepfunctions").send_task_success(
        taskToken=task_token, output='{"approved":true}'
    )
    return {"status": "APPROVED"}


@app.get("/travel-request/{request_id}", response_model=TravelRequestResponse)
def get_travel_request(
    request_id: UUID,
    user: AuthenticatedUser = Depends(require_user),
    service: TravelRequestService = Depends(get_service),
) -> TravelRequestResponse:
    """Return a request only when it belongs to the authenticated employee."""
    request = service.get(request_id, user.subject)
    logger.info("travel_request_retrieved id=%s requester_id=%s", request.id, user.subject)
    return TravelRequestResponse.model_validate(request)


handler = Mangum(app, lifespan="off")
