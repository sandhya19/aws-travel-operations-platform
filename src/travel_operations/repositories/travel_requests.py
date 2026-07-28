"""Repository boundary for travel-request metadata."""
from dataclasses import dataclass
from datetime import date
from uuid import UUID, uuid4


@dataclass(frozen=True)
class TravelRequest:
    id: UUID
    requester_id: str
    destination_country: str
    departure_date: date
    return_date: date
    purpose: str
    status: str = "SUBMITTED"


class TravelRequestRepository:
    """In-memory metadata repository; replace with CockroachDB in Milestone 4."""

    def __init__(self) -> None:
        self._records: dict[UUID, TravelRequest] = {}

    def add(self, requester_id: str, destination_country: str, departure_date: date, return_date: date, purpose: str) -> TravelRequest:
        request = TravelRequest(uuid4(), requester_id, destination_country, departure_date, return_date, purpose)
        self._records[request.id] = request
        return request

    def get(self, request_id: UUID) -> TravelRequest | None:
        return self._records.get(request_id)
