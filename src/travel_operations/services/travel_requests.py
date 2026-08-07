"""Service layer for travel-request metadata."""

import json
from datetime import date
from uuid import UUID

from travel_operations.models import TravelRequestModel, WorkflowOutboxEventModel
from travel_operations.repositories.travel_requests import TravelRequestRepository


class TravelRequestNotFound(Exception):
    """Raised when a request is absent or belongs to another user."""


class TravelRequestService:
    """Coordinates transactional repository operations without AI behavior."""

    def __init__(self, repository: TravelRequestRepository) -> None:
        self._repository = repository

    def create(
        self,
        requester_id: str,
        destination_country: str,
        departure_date: date,
        return_date: date,
        purpose: str,
    ) -> TravelRequestModel:
        return self._repository.add(
            requester_id, destination_country, departure_date, return_date, purpose
        )

    def get(self, request_id: UUID, requester_id: str) -> TravelRequestModel:
        request = self._repository.get(request_id)
        if request is None or request.requester_id != requester_id:
            raise TravelRequestNotFound("Travel request not found")
        return request

    def enqueue_request_created(self, request: TravelRequestModel) -> WorkflowOutboxEventModel:
        return self._repository.create_outbox_event(
            request.id,
            "TravelRequestCreated",
            json.dumps({"request_id": str(request.id), "requester_id": request.requester_id}),
        )

    def mark_outbox_event_published(self, event_id: UUID) -> None:
        self._repository.mark_outbox_event_published(event_id)

    def pending_outbox_events(self) -> list[WorkflowOutboxEventModel]:
        return self._repository.pending_outbox_events()

    def record_outbox_failure(self, event_id: UUID, error: str, max_attempts: int) -> bool:
        return self._repository.record_outbox_failure(event_id, error, max_attempts)

    def commit(self) -> None:
        """Commit the durable state before making an external AWS call."""
        self._repository.commit()

    def prepare_approval(self, request_id: UUID, task_token: str) -> None:
        if self._repository.get(request_id) is None:
            raise TravelRequestNotFound("Travel request not found")
        self._repository.create_approval_task(request_id, task_token)

    def approve(self, request_id: UUID, approver_id: str) -> str:
        task = self._repository.approve(request_id, approver_id)
        if task is None:
            raise TravelRequestNotFound("Pending approval task not found")
        return task.task_token

    def complete(self, request_id: UUID) -> None:
        if self._repository.mark_completed(request_id) is None:
            raise TravelRequestNotFound("Travel request not found")
