"""Service layer for travel-request metadata."""
from datetime import date
from uuid import UUID

from travel_operations.models import TravelRequestModel
from travel_operations.repositories.travel_requests import TravelRequestRepository


class TravelRequestNotFound(Exception):
    """Raised when a request is absent or belongs to another user."""


class TravelRequestService:
    """Coordinates transactional repository operations without AI behavior."""

    def __init__(self, repository: TravelRequestRepository) -> None:
        self._repository = repository

    def create(
        self, requester_id: str, destination_country: str, departure_date: date, return_date: date, purpose: str
    ) -> TravelRequestModel:
        return self._repository.add(requester_id, destination_country, departure_date, return_date, purpose)

    def get(self, request_id: UUID, requester_id: str) -> TravelRequestModel:
        request = self._repository.get(request_id)
        if request is None or request.requester_id != requester_id:
            raise TravelRequestNotFound("Travel request not found")
        return request
