"""Domain-event publication for the travel workflow."""

import json
import os
from datetime import UTC, datetime
from uuid import UUID

import boto3


def publish_travel_request_created(request_id: UUID, requester_id: str, event_id: UUID) -> None:
    """Publish the event that starts the AWS workflow when configured."""
    event_bus_name = os.getenv("EVENT_BUS_NAME")
    if not event_bus_name:
        return
    response = boto3.client("events").put_events(
        Entries=[
            {
                "EventBusName": event_bus_name,
                "Source": "travel.operations",
                "DetailType": "TravelRequestCreated",
                "Detail": json.dumps(
                    {
                        "request_id": str(request_id),
                        "requester_id": requester_id,
                        "event_id": str(event_id),
                        "occurred_at": datetime.now(UTC).isoformat(),
                        "schema_version": 1,
                    }
                ),
            }
        ]
    )
    if response["FailedEntryCount"]:
        raise RuntimeError("EventBridge did not accept TravelRequestCreated")
