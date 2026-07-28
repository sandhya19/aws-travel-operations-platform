"""CockroachDB repository for travel-request metadata."""
from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from travel_operations.models import TravelRequestModel


class TravelRequestRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, requester_id: str, destination_country: str, departure_date: date, return_date: date, purpose: str) -> TravelRequestModel:
        request = TravelRequestModel(requester_id=requester_id, destination_country=destination_country, departure_date=departure_date, return_date=return_date, purpose=purpose)
        self._session.add(request)
        self._session.flush()
        return request

    def get(self, request_id: UUID) -> TravelRequestModel | None:
        return self._session.scalar(select(TravelRequestModel).where(TravelRequestModel.id == request_id))
