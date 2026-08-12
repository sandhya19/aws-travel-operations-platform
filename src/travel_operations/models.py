"""CockroachDB metadata tables; no AI processing data is stored here."""

from datetime import UTC, date, datetime
from uuid import UUID, uuid4

from sqlalchemy import Date, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

from travel_operations.database import Base


class TravelRequestModel(Base):
    __tablename__ = "travel_requests"
    __table_args__ = (
        Index("ix_travel_requests_requester_status", "requester_id", "status"),
        Index(
            "ix_travel_requests_tenant_requester_status",
            "tenant_id",
            "requester_id",
            "status",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(String(255), nullable=False)
    requester_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    destination_country: Mapped[str] = mapped_column(String(2), nullable=False)
    departure_date: Mapped[date] = mapped_column(Date, nullable=False)
    return_date: Mapped[date] = mapped_column(Date, nullable=False)
    purpose: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="SUBMITTED")


class KnowledgeDocumentModel(Base):
    """A tenant-owned, immutable version of an approved knowledge source."""

    __tablename__ = "knowledge_documents"
    __table_args__ = (Index("ix_knowledge_documents_tenant_source", "tenant_id", "source_key"),)

    document_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String(255), nullable=False)
    source_key: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[str] = mapped_column(String(64), nullable=False)
    content_type: Mapped[str] = mapped_column(String(64), nullable=False)
    page_count: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=lambda: datetime.now(UTC))


class KnowledgeDocumentAccessModel(Base):
    """A role permitted to retrieve one tenant-owned knowledge document."""

    __tablename__ = "knowledge_document_access"
    document_id: Mapped[str] = mapped_column(
        String(64), ForeignKey("knowledge_documents.document_id"), primary_key=True
    )
    role: Mapped[str] = mapped_column(String(255), primary_key=True)


class ApprovalTaskModel(Base):
    """A Step Functions callback token awaiting a human decision."""

    __tablename__ = "approval_tasks"
    __table_args__ = (Index("ix_approval_tasks_request_status", "travel_request_id", "status"),)

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    travel_request_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("travel_requests.id"), nullable=False
    )
    task_token: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="PENDING")
    approver_id: Mapped[str | None] = mapped_column(String(255), nullable=True)


class ApprovalDecisionModel(Base):
    """An immutable record of a human approval decision."""

    __tablename__ = "approval_decisions"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    approval_task_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("approval_tasks.id"), nullable=False
    )
    decision: Mapped[str] = mapped_column(String(32), nullable=False)
    approver_id: Mapped[str] = mapped_column(String(255), nullable=False)
    decided_at: Mapped[datetime] = mapped_column(nullable=False, default=lambda: datetime.now(UTC))


class WorkflowOutboxEventModel(Base):
    """A durable domain event awaiting publication to the workflow bus."""

    __tablename__ = "workflow_outbox_events"
    __table_args__ = (Index("ix_outbox_status_created", "status", "created_at"),)

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    travel_request_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("travel_requests.id"), nullable=False
    )
    event_type: Mapped[str] = mapped_column(String(128), nullable=False)
    payload: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="PENDING")
    attempts: Mapped[int] = mapped_column(nullable=False, default=0)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=lambda: datetime.now(UTC))
    published_at: Mapped[datetime | None] = mapped_column(nullable=True)


class AgentSessionModel(Base):
    """Durable, tenant-scoped operational context for one travel case."""

    __tablename__ = "agent_sessions"
    __table_args__ = (
        Index("ix_agent_sessions_tenant_user_created", "tenant_id", "user_id", "created_at"),
        Index("ix_agent_sessions_correlation", "correlation_id", unique=True),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    travel_request_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("travel_requests.id"), nullable=False, unique=True
    )
    tenant_id: Mapped[str] = mapped_column(String(255), nullable=False)
    user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    correlation_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=lambda: datetime.now(UTC))
    updated_at: Mapped[datetime] = mapped_column(nullable=False, default=lambda: datetime.now(UTC))
    expires_at: Mapped[datetime] = mapped_column(nullable=False)
    expired_at: Mapped[datetime | None] = mapped_column(nullable=True)


class AgentMemoryEventModel(Base):
    """Append-only, attributable history for an agent-assisted travel case."""

    __tablename__ = "agent_memory_events"
    __table_args__ = (
        Index("ix_memory_events_session_created", "agent_session_id", "created_at"),
        Index("ix_memory_events_tenant_correlation", "tenant_id", "correlation_id", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    agent_session_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("agent_sessions.id"), nullable=False
    )
    tenant_id: Mapped[str] = mapped_column(String(255), nullable=False)
    user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    correlation_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    event_type: Mapped[str] = mapped_column(String(128), nullable=False)
    actor_id: Mapped[str] = mapped_column(String(255), nullable=False)
    source: Mapped[str] = mapped_column(String(128), nullable=False)
    payload: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=lambda: datetime.now(UTC))


class AgentPlanModel(Base):
    """An immutable deterministic or agent-generated plan for a travel case."""

    __tablename__ = "agent_plans"
    __table_args__ = (Index("ix_agent_plans_session_created", "agent_session_id", "created_at"),)

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    agent_session_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("agent_sessions.id"), nullable=False
    )
    tenant_id: Mapped[str] = mapped_column(String(255), nullable=False)
    user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    correlation_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    plan_type: Mapped[str] = mapped_column(String(128), nullable=False)
    plan_version: Mapped[str] = mapped_column(String(64), nullable=False)
    source: Mapped[str] = mapped_column(String(128), nullable=False)
    payload: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=lambda: datetime.now(UTC))


class ToolExecutionModel(Base):
    """An immutable record of one Lambda action-group tool invocation."""

    __tablename__ = "tool_executions"
    __table_args__ = (
        Index("ix_tool_executions_session_started", "agent_session_id", "started_at"),
        Index("ix_tool_executions_tenant_correlation", "tenant_id", "correlation_id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    agent_session_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("agent_sessions.id"), nullable=False
    )
    tenant_id: Mapped[str] = mapped_column(String(255), nullable=False)
    user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    correlation_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    tool_name: Mapped[str] = mapped_column(String(128), nullable=False)
    invocation_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    input_payload: Mapped[str] = mapped_column(Text, nullable=False)
    output_payload: Mapped[str] = mapped_column(Text, nullable=False)
    started_at: Mapped[datetime] = mapped_column(nullable=False, default=lambda: datetime.now(UTC))
    completed_at: Mapped[datetime] = mapped_column(
        nullable=False, default=lambda: datetime.now(UTC)
    )


class WorkflowCheckpointModel(Base):
    """Idempotent durable recovery point for the travel approval workflow."""

    __tablename__ = "workflow_checkpoints"
    __table_args__ = (
        Index("ix_workflow_checkpoints_session_created", "agent_session_id", "created_at"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    agent_session_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("agent_sessions.id"), nullable=False
    )
    correlation_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    state: Mapped[str] = mapped_column(String(64), nullable=False)
    payload: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False, default=lambda: datetime.now(UTC))


class MemoryLifecycleRecordModel(Base):
    """Immutable evidence that a durable memory-retention action occurred."""

    __tablename__ = "memory_lifecycle_records"
    __table_args__ = (Index("ix_memory_lifecycle_correlation", "correlation_id", "occurred_at"),)

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    agent_session_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    correlation_id: Mapped[UUID] = mapped_column(Uuid, nullable=False)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    occurred_at: Mapped[datetime] = mapped_column(nullable=False, default=lambda: datetime.now(UTC))
