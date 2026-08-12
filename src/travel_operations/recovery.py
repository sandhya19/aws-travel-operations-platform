"""Guards for controlled workflow-recovery exercises."""

import os


def should_simulate_approval_callback_failure() -> bool:
    """Permit a recovery drill only for an explicitly configured dev runtime."""
    return (
        os.getenv("ENVIRONMENT") == "dev"
        and os.getenv("SIMULATE_APPROVAL_CALLBACK_FAILURE", "false").lower() == "true"
    )
