"""Start Standard Step Functions executions idempotently from EventBridge."""

import json
import os

import boto3
from botocore.exceptions import ClientError


def handler(event: dict[str, object], _: object) -> dict[str, str]:
    """Use the durable outbox event identifier as the execution name."""
    detail = event["detail"]
    if not isinstance(detail, dict) or "event_id" not in detail:
        raise ValueError("TravelRequestCreated event_id is required")
    event_id = str(detail["event_id"])
    try:
        response = boto3.client("stepfunctions").start_execution(
            stateMachineArn=os.environ["WORKFLOW_STATE_MACHINE_ARN"],
            name=event_id,
            input=json.dumps(event),
        )
    except ClientError as error:
        if error.response["Error"]["Code"] == "ExecutionAlreadyExists":
            return {"status": "DUPLICATE", "event_id": event_id}
        raise
    return {"status": "STARTED", "execution_arn": response["executionArn"]}
