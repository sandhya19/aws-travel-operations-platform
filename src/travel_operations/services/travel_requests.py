"""Service layer for travel-request metadata."""
from datetime import date
from uuid import UUID

from travel_operations.repositories.travel_requests import TravelRequest, TravelRequestRepository


class TravelRequestNotFound(Exception):
    """Raised when a request is absent or belongs to another user."""


class TravelRequestService:
    def __init__(self, repository: TravelRequestRepository | None = None) -> None:
        self._repository = repository or TravelRequestRepository()

    def create(
        self, requester_id: str, destination_country: str, departure_date: date, return_date: date, purpose: str
    ) -> TravelRequest:
        return self._repository.add(requester_id, destination_country, departure_date, return_date, purpose)

    def get(self, request_id: UUID, requester_id: str) -> TravelRequest:
        request = self._repository.get(request_id)
        if request is None or request.requester_id != requester_id:
            raise TravelRequestNotFound("Travel request not found")
        return request
