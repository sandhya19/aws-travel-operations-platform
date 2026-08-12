"""CockroachDB repository for travel-request metadata."""

from datetime import UTC, date, datetime
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from travel_operations.models import (
    AgentMemoryEventModel,
    AgentPlanModel,
    AgentSessionModel,
    ApprovalDecisionModel,
    ApprovalTaskModel,
    MemoryLifecycleRecordModel,
    ToolExecutionModel,
    TravelRequestModel,
    WorkflowCheckpointModel,
    WorkflowOutboxEventModel,
)


class TravelRequestRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(
        self,
        requester_id: str,
        tenant_id: str,
        destination_country: str,
        departure_date: date,
        return_date: date,
        purpose: str,
    ) -> TravelRequestModel:
        request = TravelRequestModel(
            requester_id=requester_id,
            tenant_id=tenant_id,
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

    def get_for_tenant(self, request_id: UUID, tenant_id: str) -> TravelRequestModel | None:
        """Return a request only when it belongs to the authenticated tenant."""
        return self._session.scalar(
            select(TravelRequestModel).where(
                TravelRequestModel.id == request_id,
                TravelRequestModel.tenant_id == tenant_id,
            )
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

    def reject(self, request_id: UUID, approver_id: str) -> ApprovalTaskModel | None:
        task = self._session.scalar(
            select(ApprovalTaskModel).where(
                ApprovalTaskModel.travel_request_id == request_id,
                ApprovalTaskModel.status == "PENDING",
            )
        )
        if task is not None:
            task.status = "REJECTED"
            task.approver_id = approver_id
            self._session.add(
                ApprovalDecisionModel(
                    approval_task_id=task.id,
                    decision="REJECTED",
                    approver_id=approver_id,
                )
            )
        return task

    def approval_decisions(self, request_id: UUID) -> list[ApprovalDecisionModel]:
        return list(
            self._session.scalars(
                select(ApprovalDecisionModel)
                .join(ApprovalTaskModel)
                .where(ApprovalTaskModel.travel_request_id == request_id)
                .order_by(ApprovalDecisionModel.decided_at, ApprovalDecisionModel.id)
            )
        )

    def mark_completed(self, request_id: UUID) -> TravelRequestModel | None:
        request = self.get(request_id)
        if request is not None:
            request.status = "COMPLETED"
        return request

    def mark_rejected(self, request_id: UUID) -> TravelRequestModel | None:
        request = self.get(request_id)
        if request is not None:
            request.status = "REJECTED"
        return request

    def create_agent_session(
        self, request_id: UUID, tenant_id: str, user_id: str, expires_at: datetime
    ) -> AgentSessionModel:
        session = AgentSessionModel(
            travel_request_id=request_id,
            tenant_id=tenant_id,
            user_id=user_id,
            correlation_id=request_id,
            expires_at=expires_at,
        )
        self._session.add(session)
        self._session.flush()
        return session

    def expire_due_agent_sessions(self, now: datetime, limit: int = 50) -> list[AgentSessionModel]:
        sessions = list(
            self._session.scalars(
                select(AgentSessionModel)
                .join(TravelRequestModel)
                .where(
                    AgentSessionModel.status == "ACTIVE",
                    AgentSessionModel.expires_at <= now,
                    TravelRequestModel.status.in_(("COMPLETED", "REJECTED")),
                )
                .order_by(AgentSessionModel.expires_at)
                .limit(limit)
                .with_for_update(skip_locked=True)
            )
        )
        for agent_session in sessions:
            agent_session.status = "EXPIRED"
            agent_session.expired_at = now
            self._session.add(
                MemoryLifecycleRecordModel(
                    agent_session_id=agent_session.id,
                    correlation_id=agent_session.correlation_id,
                    action="EXPIRED",
                )
            )
        self._session.flush()
        return sessions

    def append_memory_event(
        self,
        agent_session: AgentSessionModel,
        event_type: str,
        actor_id: str,
        source: str,
        payload: str,
    ) -> AgentMemoryEventModel:
        event = AgentMemoryEventModel(
            agent_session_id=agent_session.id,
            tenant_id=agent_session.tenant_id,
            user_id=agent_session.user_id,
            correlation_id=agent_session.correlation_id,
            event_type=event_type,
            actor_id=actor_id,
            source=source,
            payload=payload,
        )
        self._session.add(event)
        self._session.flush()
        return event

    def get_agent_session(
        self, request_id: UUID, tenant_id: str, user_id: str
    ) -> AgentSessionModel | None:
        return self._session.scalar(
            select(AgentSessionModel).where(
                AgentSessionModel.travel_request_id == request_id,
                AgentSessionModel.tenant_id == tenant_id,
                AgentSessionModel.user_id == user_id,
            )
        )

    def get_agent_session_for_request(self, request_id: UUID) -> AgentSessionModel | None:
        return self._session.scalar(
            select(AgentSessionModel).where(AgentSessionModel.travel_request_id == request_id)
        )

    def memory_events(self, agent_session_id: UUID) -> list[AgentMemoryEventModel]:
        return list(
            self._session.scalars(
                select(AgentMemoryEventModel)
                .where(AgentMemoryEventModel.agent_session_id == agent_session_id)
                .order_by(AgentMemoryEventModel.created_at, AgentMemoryEventModel.id)
            )
        )

    def create_agent_plan(
        self,
        agent_session: AgentSessionModel,
        plan_type: str,
        plan_version: str,
        source: str,
        payload: str,
    ) -> AgentPlanModel:
        plan = AgentPlanModel(
            agent_session_id=agent_session.id,
            tenant_id=agent_session.tenant_id,
            user_id=agent_session.user_id,
            correlation_id=agent_session.correlation_id,
            plan_type=plan_type,
            plan_version=plan_version,
            source=source,
            payload=payload,
        )
        self._session.add(plan)
        self._session.flush()
        return plan

    def create_tool_execution(
        self,
        agent_session: AgentSessionModel,
        tool_name: str,
        invocation_id: str,
        input_payload: str,
        output_payload: str,
    ) -> tuple[ToolExecutionModel, bool]:
        existing = self._session.scalar(
            select(ToolExecutionModel).where(ToolExecutionModel.invocation_id == invocation_id)
        )
        if existing is not None:
            return existing, False
        execution = ToolExecutionModel(
            agent_session_id=agent_session.id,
            tenant_id=agent_session.tenant_id,
            user_id=agent_session.user_id,
            correlation_id=agent_session.correlation_id,
            tool_name=tool_name,
            invocation_id=invocation_id,
            status="COMPLETED",
            input_payload=input_payload,
            output_payload=output_payload,
        )
        self._session.add(execution)
        self._session.flush()
        return execution, True

    def create_workflow_checkpoint(
        self, agent_session: AgentSessionModel, state: str, payload: str
    ) -> tuple[WorkflowCheckpointModel, bool]:
        existing = self._session.scalar(
            select(WorkflowCheckpointModel).where(
                WorkflowCheckpointModel.agent_session_id == agent_session.id,
                WorkflowCheckpointModel.state == state,
            )
        )
        if existing is not None:
            return existing, False
        checkpoint = WorkflowCheckpointModel(
            agent_session_id=agent_session.id,
            correlation_id=agent_session.correlation_id,
            state=state,
            payload=payload,
        )
        self._session.add(checkpoint)
        self._session.flush()
        return checkpoint, True

    def latest_workflow_checkpoint(self, request_id: UUID) -> WorkflowCheckpointModel | None:
        return self._session.scalar(
            select(WorkflowCheckpointModel)
            .join(AgentSessionModel)
            .where(AgentSessionModel.travel_request_id == request_id)
            .order_by(WorkflowCheckpointModel.created_at.desc())
        )

    def approved_task(self, request_id: UUID) -> ApprovalTaskModel | None:
        return self._session.scalar(
            select(ApprovalTaskModel).where(
                ApprovalTaskModel.travel_request_id == request_id,
                ApprovalTaskModel.status == "APPROVED",
            )
        )
