"""Scheduled expiry of terminal travel-case memory sessions."""

from datetime import UTC, datetime

from travel_operations.database import SessionFactory
from travel_operations.repositories.travel_requests import TravelRequestRepository


def handler(_: dict[str, object], __: object) -> dict[str, int]:
    """Expire due terminal sessions and retain immutable expiry evidence."""
    with SessionFactory.begin() as session:
        expired = TravelRequestRepository(session).expire_due_agent_sessions(datetime.now(UTC))
    return {"expired": len(expired)}
