"""Opt-in CockroachDB persistence coverage for IMP-006."""

import os
from datetime import UTC, date, datetime, timedelta

import pytest
from sqlalchemy import delete

from travel_operations.database import SessionFactory
from travel_operations.models import AgentMemoryEventModel, AgentSessionModel, TravelRequestModel
from travel_operations.repositories.travel_requests import TravelRequestRepository


@pytest.mark.database  # type: ignore[misc]
def test_agent_session_and_memory_event_persist_to_cockroachdb() -> None:
    """Verify the migrated session/event tables survive a transaction boundary."""
    if os.getenv("RUN_DATABASE_INTEGRATION") != "1":
        pytest.skip("Set RUN_DATABASE_INTEGRATION=1 to run against the configured database")

    request_id = None
    try:
        with SessionFactory.begin() as session:
            repository = TravelRequestRepository(session)
            request = repository.add(
                "integration-test-user",
                "integration-test-tenant",
                "GB",
                date(2026, 9, 1),
                date(2026, 9, 3),
                "Migration verification",
            )
            request_id = request.id
            agent_session = repository.create_agent_session(
                request.id,
                "integration-test-tenant",
                "integration-test-user",
                datetime.now(UTC) + timedelta(days=1),
            )
            repository.append_memory_event(
                agent_session,
                "integration_test",
                "integration-test-user",
                "pytest",
                "{}",
            )

        with SessionFactory() as session:
            repository = TravelRequestRepository(session)
            assert request_id is not None
            agent_session = repository.get_agent_session(
                request_id, "integration-test-tenant", "integration-test-user"
            )
            assert agent_session is not None
            assert [event.event_type for event in repository.memory_events(agent_session.id)] == [
                "integration_test"
            ]
            assert repository.get_for_tenant(request_id, "other-tenant") is None
    finally:
        if request_id is not None:
            with SessionFactory.begin() as session:
                session.execute(
                    delete(AgentMemoryEventModel).where(
                        AgentMemoryEventModel.correlation_id == request_id
                    )
                )
                session.execute(
                    delete(AgentSessionModel).where(
                        AgentSessionModel.travel_request_id == request_id
                    )
                )
                session.execute(
                    delete(TravelRequestModel).where(TravelRequestModel.id == request_id)
                )
