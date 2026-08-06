"""CockroachDB metadata tables; no AI processing data is stored here."""

from datetime import UTC, date, datetime
from uuid import UUID, uuid4

from sqlalchemy import Date, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Uuid

from travel_operations.database import Base


class TravelRequestModel(Base):
    __tablename__ = "travel_requests"
    __table_args__ = (Index("ix_travel_requests_requester_status", "requester_id", "status"),)

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    requester_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    destination_country: Mapped[str] = mapped_column(String(2), nullable=False)
    departure_date: Mapped[date] = mapped_column(Date, nullable=False)
    return_date: Mapped[date] = mapped_column(Date, nullable=False)
    purpose: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="SUBMITTED")


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
