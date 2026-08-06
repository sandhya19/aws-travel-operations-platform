"""Idempotency contracts for EventBridge workflow starts."""

from unittest.mock import Mock

from botocore.exceptions import ClientError

from travel_operations import workflow_starter


def test_starter_uses_outbox_event_id_as_execution_name(
    monkeypatch: object,
) -> None:
    monkeypatch.setenv(
        "WORKFLOW_STATE_MACHINE_ARN",
        "arn:aws:states:eu-west-2:123456789012:stateMachine:travel",
    )
    client = Mock()
    client.start_execution.return_value = {"executionArn": "arn:aws:states:execution"}
    monkeypatch.setattr(workflow_starter.boto3, "client", lambda _: client)

    result = workflow_starter.handler(
        {"detail": {"event_id": "outbox-event-1", "request_id": "request-1"}}, object()
    )

    assert result["status"] == "STARTED"
    assert client.start_execution.call_args.kwargs["name"] == "outbox-event-1"


def test_starter_treats_duplicate_execution_as_success(monkeypatch: object) -> None:
    monkeypatch.setenv("WORKFLOW_STATE_MACHINE_ARN", "arn:aws:states:stateMachine:travel")
    client = Mock()
    client.start_execution.side_effect = ClientError(
        {"Error": {"Code": "ExecutionAlreadyExists", "Message": "duplicate"}},
        "StartExecution",
    )
    monkeypatch.setattr(workflow_starter.boto3, "client", lambda _: client)

    result = workflow_starter.handler({"detail": {"event_id": "outbox-event-1"}}, object())

    assert result == {"status": "DUPLICATE", "event_id": "outbox-event-1"}
