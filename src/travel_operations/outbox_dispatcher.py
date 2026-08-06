"""Retry publication of durable workflow outbox events."""

import json

from travel_operations.database import SessionFactory
from travel_operations.events import publish_travel_request_created
from travel_operations.repositories.travel_requests import TravelRequestRepository
from travel_operations.services.travel_requests import TravelRequestService


def handler(_: dict[str, object], __: object) -> dict[str, int]:
    """Publish pending events; failed entries remain pending for the next invocation."""
    published = 0
    failed = 0
    with SessionFactory() as session:
        service = TravelRequestService(TravelRequestRepository(session))
        for event in service.pending_outbox_events():
            payload = json.loads(event.payload)
            try:
                publish_travel_request_created(
                    event.travel_request_id,
                    str(payload["requester_id"]),
                    event.id,
                )
            except Exception as error:
                service.record_outbox_failure(event.id, str(error))
                failed += 1
            else:
                service.mark_outbox_event_published(event.id)
                published += 1
        session.commit()
    return {"published": published, "failed": failed}
