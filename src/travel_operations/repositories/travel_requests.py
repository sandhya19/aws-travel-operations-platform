"""CockroachDB repository for travel-request metadata."""

from datetime import UTC, date, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from travel_operations.models import (
    ApprovalDecisionModel,
    ApprovalTaskModel,
    TravelRequestModel,
    WorkflowOutboxEventModel,
)


class TravelRequestRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(
        self,
        requester_id: str,
        destination_country: str,
        departure_date: date,
        return_date: date,
        purpose: str,
    ) -> TravelRequestModel:
        request = TravelRequestModel(
            requester_id=requester_id,
            destination_country=destination_country,
            departure_date=departure_date,
            return_date=return_date,
            purpose=purpose,
        )
        self._session.add(request)
        self._session.flush()
        return request

    def get(self, request_id: UUID) -> TravelRequestModel | None:
        return self._session.scalar(
            select(TravelRequestModel).where(TravelRequestModel.id == request_id)
        )

    def create_approval_task(self, request_id: UUID, task_token: str) -> ApprovalTaskModel:
        task = ApprovalTaskModel(travel_request_id=request_id, task_token=task_token)
        self._session.add(task)
        self._session.flush()
        return task

    def create_outbox_event(
        self, request_id: UUID, event_type: str, payload: str
    ) -> WorkflowOutboxEventModel:
        event = WorkflowOutboxEventModel(
            travel_request_id=request_id,
            event_type=event_type,
            payload=payload,
        )
        self._session.add(event)
        self._session.flush()
        return event

    def mark_outbox_event_published(self, event_id: UUID) -> None:
        event = self._session.get(WorkflowOutboxEventModel, event_id)
        if event is not None:
            event.status = "PUBLISHED"
            event.published_at = datetime.now(UTC)

    def pending_outbox_events(self, limit: int = 25) -> list[WorkflowOutboxEventModel]:
        return list(
            self._session.scalars(
                select(WorkflowOutboxEventModel)
                .where(WorkflowOutboxEventModel.status == "PENDING")
                .order_by(WorkflowOutboxEventModel.created_at)
                .limit(limit)
                .with_for_update(skip_locked=True)
            )
        )

    def record_outbox_failure(self, event_id: UUID, error: str, max_attempts: int) -> bool:
        event = self._session.get(WorkflowOutboxEventModel, event_id)
        if event is not None:
            event.attempts += 1
            event.last_error = error[:1000]
            if event.attempts >= max_attempts:
                event.status = "FAILED"
                return True
        return False

    def commit(self) -> None:
        self._session.commit()

    def approve(self, request_id: UUID, approver_id: str) -> ApprovalTaskModel | None:
        task = self._session.scalar(
            select(ApprovalTaskModel).where(
                ApprovalTaskModel.travel_request_id == request_id,
                ApprovalTaskModel.status == "PENDING",
            )
        )
        if task is not None:
            task.status = "APPROVED"
            task.approver_id = approver_id
            self._session.add(
                ApprovalDecisionModel(
                    approval_task_id=task.id,
                    decision="APPROVED",
                    approver_id=approver_id,
                )
            )
        return task

    def mark_completed(self, request_id: UUID) -> TravelRequestModel | None:
        request = self.get(request_id)
        if request is not None:
            request.status = "COMPLETED"
        return request
