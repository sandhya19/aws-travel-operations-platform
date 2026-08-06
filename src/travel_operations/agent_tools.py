"""Pure Lambda-tool handlers; persistence and agent memory are deliberately absent."""

from typing import Any


def handler(event: dict[str, Any], _: Any) -> dict[str, Any]:
    """Return a typed tool response for Bedrock action-group integration."""
    action = event.get("actionGroup", "unknown")
    return {
        "messageVersion": "1.0",
        "response": {
            "actionGroup": action,
            "function": event.get("function", "unknown"),
            "functionResponse": {
                "responseBody": {"TEXT": {"body": "Tool execution requires its owning workflow."}}
            },
        },
    }
