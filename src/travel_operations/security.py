"""Application-level security controls."""

import re
from dataclasses import dataclass

_INJECTION = re.compile(
    r"ignore (all |previous )?instructions|system prompt|developer message", re.I
)
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_CARD = re.compile(r"\b(?:\d[ -]*?){13,16}\b")


def reject_prompt_injection(value: str) -> str:
    if _INJECTION.search(value):
        raise ValueError("Unsafe prompt content detected")
    return value


def mask_pii(value: str) -> str:
    return _CARD.sub("[CARD_REDACTED]", _EMAIL.sub("[EMAIL_REDACTED]", value))


@dataclass(frozen=True)
class AuditEvent:
    actor_id: str
    action: str
    resource_id: str
    correlation_id: str
