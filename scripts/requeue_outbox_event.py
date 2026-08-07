"""Requeue one failed workflow outbox event after operator review."""

import argparse
from uuid import UUID

from travel_operations.database import SessionFactory
from travel_operations.models import WorkflowOutboxEventModel


def requeue(event: WorkflowOutboxEventModel) -> None:
    """Reset only an exhausted event so the scheduled dispatcher can retry it."""
    if event.status != "FAILED":
        raise ValueError("Only FAILED outbox events can be requeued")
    event.status = "PENDING"
    event.attempts = 0
    event.last_error = None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("event_id", type=UUID)
    event_id = parser.parse_args().event_id

    with SessionFactory.begin() as session:
        event = session.get(WorkflowOutboxEventModel, event_id)
        if event is None:
            raise ValueError("Outbox event not found")
        requeue(event)
    print(f"Requeued outbox event {event_id}")


if __name__ == "__main__":
    main()
