"""CockroachDB metadata tables; no AI processing data is stored here."""
from datetime import date
from uuid import UUID, uuid4

from sqlalchemy import Date, Index, String, Text
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
