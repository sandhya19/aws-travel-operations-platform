"""Service layer for travel-request metadata."""

import json
import os
from datetime import UTC, date, datetime, timedelta
from uuid import UUID

from travel_operations.models import (
    AgentMemoryEventModel,
    TravelRequestModel,
    WorkflowOutboxEventModel,
)
from travel_operations.repositories.travel_requests import TravelRequestRepository
from travel_operations.services.itineraries import ItineraryRequirements, create_itinerary_draft


class TravelRequestNotFound(Exception):
    """Raised when a request is absent or belongs to another user."""


class TravelRequestService:
    """Coordinates transactional repository operations without AI behavior."""

    def __init__(self, repository: TravelRequestRepository) -> None:
        self._repository = repository

    def create(
        self,
        requester_id: str,
        tenant_id: str,
        destination_country: str,
        departure_date: date,
        return_date: date,
        purpose: str,
    ) -> TravelRequestModel:
        request = self._repository.add(
            requester_id, tenant_id, destination_country, departure_date, return_date, purpose
        )
        session = self._repository.create_agent_session(
            request.id,
            tenant_id,
            requester_id,
            datetime.now(UTC) + timedelta(days=memory_retention_days()),
        )
        self._repository.create_agent_plan(
            session,
            "travel_request_workflow",
            "v1",
            "travel_operations.workflow",
            json.dumps({"steps": ["validate", "await_approval", "complete"]}),
        )
        self._repository.append_memory_event(
            session,
            "travel_request_submitted",
            requester_id,
            "travel_operations.api",
            json.dumps({"status": request.status, "destination_country": destination_country}),
        )
        self._repository.append_memory_event(
            session,
            "workflow_plan_created",
            "travel_operations.workflow",
            "travel_operations.workflow",
            json.dumps({"plan_type": "travel_request_workflow", "plan_version": "v1"}),
        )
        return request

    def get(self, request_id: UUID, requester_id: str, tenant_id: str) -> TravelRequestModel:
        request = self._repository.get_for_tenant(request_id, tenant_id)
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

    def approve(self, request_id: UUID, approver_id: str, tenant_id: str) -> str:
        if self._repository.get_for_tenant(request_id, tenant_id) is None:
            raise TravelRequestNotFound("Travel request not found")
        task = self._repository.approve(request_id, approver_id)
        if task is None:
            raise TravelRequestNotFound("Pending approval task not found")
        self.record_memory_event(
            request_id,
            "approval_decided",
            approver_id,
            "travel_operations.api",
            {"decision": "APPROVED"},
        )
        self.record_workflow_checkpoint(request_id, "APPROVAL_APPROVED", {"decision": "APPROVED"})
        return task.task_token

    def reject(self, request_id: UUID, approver_id: str, tenant_id: str) -> str:
        if self._repository.get_for_tenant(request_id, tenant_id) is None:
            raise TravelRequestNotFound("Travel request not found")
        task = self._repository.reject(request_id, approver_id)
        if task is None:
            raise TravelRequestNotFound("Pending approval task not found")
        self.record_memory_event(
            request_id,
            "approval_decided",
            approver_id,
            "travel_operations.api",
            {"decision": "REJECTED"},
        )
        self.record_workflow_checkpoint(request_id, "APPROVAL_REJECTED", {"decision": "REJECTED"})
        return task.task_token

    def complete(self, request_id: UUID) -> None:
        if self._repository.mark_completed(request_id) is None:
            raise TravelRequestNotFound("Travel request not found")
        self.record_memory_event(
            request_id,
            "travel_request_completed",
            "travel_operations.workflow",
            "travel_operations.workflow",
            {"status": "COMPLETED"},
        )

    def reject_complete(self, request_id: UUID) -> None:
        if self._repository.mark_rejected(request_id) is None:
            raise TravelRequestNotFound("Travel request not found")
        self.record_memory_event(
            request_id,
            "travel_request_rejected",
            "travel_operations.workflow",
            "travel_operations.workflow",
            {"status": "REJECTED"},
        )
        self.record_workflow_checkpoint(request_id, "REJECTED", {"status": "REJECTED"})

    def record_memory_event(
        self, request_id: UUID, event_type: str, actor_id: str, source: str, payload: dict[str, str]
    ) -> None:
        """Record an immutable operational event when the request has a memory session."""
        session = self._repository.get_agent_session_for_request(request_id)
        if session is not None:
            self._repository.append_memory_event(
                session, event_type, actor_id, source, json.dumps(payload)
            )

    def record_workflow_checkpoint(
        self, request_id: UUID, state: str, payload: dict[str, str]
    ) -> None:
        """Persist an idempotent recovery point for a durable workflow transition."""
        session = self._repository.get_agent_session_for_request(request_id)
        if session is not None:
            checkpoint, created = self._repository.create_workflow_checkpoint(
                session, state, json.dumps(payload)
            )
            if created:
                self._repository.append_memory_event(
                    session,
                    "workflow_checkpoint_created",
                    "travel_operations.workflow",
                    "travel_operations.workflow",
                    json.dumps({"checkpoint_id": str(checkpoint.id), "state": state}),
                )

    def approved_callback_token_for_replay(self, request_id: UUID) -> str:
        """Return a callback token only from an approved, incomplete recovery point."""
        request = self._repository.get(request_id)
        checkpoint = self._repository.latest_workflow_checkpoint(request_id)
        task = self._repository.approved_task(request_id)
        if (
            request is None
            or request.status == "COMPLETED"
            or checkpoint is None
            or checkpoint.state != "APPROVAL_APPROVED"
            or task is None
        ):
            raise TravelRequestNotFound("No approved callback checkpoint available for replay")
        return task.task_token

    def memory_events(
        self, request_id: UUID, requester_id: str, tenant_id: str
    ) -> list[AgentMemoryEventModel]:
        self.get(request_id, requester_id, tenant_id)
        session = self._repository.get_agent_session(request_id, tenant_id, requester_id)
        if session is None:
            raise TravelRequestNotFound("Travel request memory not found")
        return self._repository.memory_events(session.id)

    def approval_history(self, request_id: UUID, tenant_id: str) -> list[object]:
        """Return decisions only when the approver is in the request's tenant."""
        if self._repository.get_for_tenant(request_id, tenant_id) is None:
            raise TravelRequestNotFound("Travel request not found")
        return self._repository.approval_decisions(request_id)

    def create_itinerary_draft(
        self, request_id: UUID, tenant_id: str, user_id: str, requirements: ItineraryRequirements
    ) -> dict[str, object]:
        """Create one auditable, non-booking draft for the authenticated travel case."""
        return create_itinerary_draft(
            self._repository, request_id, tenant_id, user_id, requirements
        )


def memory_retention_days() -> int:
    """Read the bounded retention period used when a travel-case session starts."""
    days = int(os.getenv("MEMORY_RETENTION_DAYS", "365"))
    if days < 1:
        raise ValueError("MEMORY_RETENTION_DAYS must be at least one day")
    return days
