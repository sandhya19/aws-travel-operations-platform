"""Seed non-AI development metadata."""

from datetime import date

from travel_operations.database import SessionFactory
from travel_operations.repositories.travel_requests import TravelRequestRepository

with SessionFactory.begin() as session:
    TravelRequestRepository(session).add(
        "demo.employee", "GB", date(2026, 9, 1), date(2026, 9, 5), "Client meeting"
    )
