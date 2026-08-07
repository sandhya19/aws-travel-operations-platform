"""Retry publication of durable workflow outbox events."""

import json
import os

import boto3

from travel_operations.database import SessionFactory
from travel_operations.events import publish_travel_request_created
from travel_operations.repositories.travel_requests import TravelRequestRepository
from travel_operations.services.travel_requests import TravelRequestService


def send_to_dlq(event: object, error: str) -> None:
    """Send only recovery identifiers and failure context to the configured DLQ."""
    queue_url = os.environ["OUTBOX_DLQ_URL"]
    boto3.client("sqs").send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(
            {
                "event_id": str(event.id),
                "event_type": event.event_type,
                "error": error,
            }
        ),
    )


def handler(_: dict[str, object], __: object) -> dict[str, int]:
    """Publish pending events and route exhausted retries to the DLQ."""
    published = 0
    failed = 0
    dlq = 0
    max_attempts = max(1, int(os.getenv("OUTBOX_MAX_ATTEMPTS", "3")))
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
                if service.record_outbox_failure(event.id, str(error), max_attempts):
                    send_to_dlq(event, str(error))
                    dlq += 1
                failed += 1
            else:
                service.mark_outbox_event_published(event.id)
                published += 1
        session.commit()
    return {"published": published, "failed": failed, "dlq": dlq}
