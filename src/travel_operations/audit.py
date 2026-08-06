"""Structured, PII-safe audit logging."""

import json
import logging

from travel_operations.security import AuditEvent

logger = logging.getLogger("travel_operations.audit")


def record(event: AuditEvent) -> None:
    logger.info(
        json.dumps(
            {
                "actor_id": event.actor_id,
                "action": event.action,
                "resource_id": event.resource_id,
                "correlation_id": event.correlation_id,
            }
        )
    )
