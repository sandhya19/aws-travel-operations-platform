"""Unit tests for Step Functions workflow-handler routing."""

from unittest.mock import patch

from travel_operations import workflow_handlers


def test_handler_routes_task_token_to_approval() -> None:
    event = {"TaskToken": "token", "detail": {"request_id": "request"}}
    with patch.object(workflow_handlers, "request_approval") as approval:
        assert workflow_handlers.handler(event, object()) is None
    approval.assert_called_once()


def test_handler_routes_complete_action() -> None:
    event = {"action": "COMPLETE", "request_id": "request"}
    with patch.object(workflow_handlers, "complete", return_value=event) as complete:
        assert workflow_handlers.handler(event, object()) == event
    complete.assert_called_once()


def test_handler_defaults_to_validation() -> None:
    event = {"detail": {"request_id": "request"}}
    with patch.object(workflow_handlers, "validate", return_value=event) as validate:
        assert workflow_handlers.handler(event, object()) == event
    validate.assert_called_once()
