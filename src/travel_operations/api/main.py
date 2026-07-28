"""FastAPI Lambda entry point for travel-request metadata."""
import logging
import os
from datetime import date
from uuid import UUID

from fastapi import Depends, FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from mangum import Mangum
from pydantic import BaseModel, ConfigDict, Field

from travel_operations.auth import AuthenticatedUser, require_user
from travel_operations.services.travel_requests import TravelRequestNotFound, TravelRequestService

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"), format="%(message)s")
logger = logging.getLogger(__name__)
service = TravelRequestService()


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


@app.exception_handler(TravelRequestNotFound)
async def travel_request_not_found(_: Request, error: TravelRequestNotFound) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(error)})


@app.exception_handler(RequestValidationError)
async def validation_error(_: Request, error: RequestValidationError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": error.errors()})


@app.post("/travel-request", response_model=TravelRequestResponse, status_code=status.HTTP_201_CREATED)
def create_travel_request(
    payload: TravelRequestCreate, user: AuthenticatedUser = Depends(require_user)
) -> TravelRequestResponse:
    """Create a metadata-only travel request for the authenticated employee."""
    if payload.return_date < payload.departure_date:
        return JSONResponse(status_code=422, content={"detail": "return_date must not precede departure_date"})
    request = service.create(user.subject, payload.destination_country, payload.departure_date, payload.return_date, payload.purpose)
    logger.info("travel_request_created id=%s requester_id=%s", request.id, user.subject)
    return TravelRequestResponse.model_validate(request)


@app.get("/travel-request/{request_id}", response_model=TravelRequestResponse)
def get_travel_request(request_id: UUID, user: AuthenticatedUser = Depends(require_user)) -> TravelRequestResponse:
    """Return a request only when it belongs to the authenticated employee."""
    request = service.get(request_id, user.subject)
    logger.info("travel_request_retrieved id=%s requester_id=%s", request.id, user.subject)
    return TravelRequestResponse.model_validate(request)


handler = Mangum(app, lifespan="off")
