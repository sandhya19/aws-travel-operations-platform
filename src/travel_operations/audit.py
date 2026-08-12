"""Structured, PII-safe audit logging."""

import json
import logging

from travel_operations.security import AuditEvent, mask_pii

logger = logging.getLogger("travel_operations.audit")


def record(event: AuditEvent) -> None:
    logger.info(
        json.dumps(
            {
                "actor_id": mask_pii(event.actor_id),
                "action": mask_pii(event.action),
                "resource_id": mask_pii(event.resource_id),
                "correlation_id": mask_pii(event.correlation_id),
            }
        )
    )
