"""AgentCore itinerary orchestrator with tenant-scoped specialist delegations."""

import json
import os
from typing import Any, Protocol
from uuid import UUID, uuid4

import boto3
from bedrock_agentcore import BedrockAgentCoreApp

app = BedrockAgentCoreApp()


class LambdaInvoker(Protocol):
    """Minimal Lambda client contract used by the runtime entry point."""

    def invoke(self, **kwargs: Any) -> dict[str, Any]: ...


def _required_context(payload: dict[str, Any]) -> tuple[str, str, str] | None:
    """Accept only a complete tenant-bound travel-case context."""
    request_id = payload.get("travel_request_id")
    tenant_id = payload.get("tenant_id")
    user_id = payload.get("user_id")
    if not all(isinstance(value, str) and value for value in (request_id, tenant_id, user_id)):
        return None
    try:
        UUID(request_id)
    except ValueError:
        return None
    return request_id, tenant_id, user_id


def _tool_event(request_id: str, tenant_id: str, user_id: str) -> dict[str, Any]:
    """Build the existing typed-tool contract without forwarding user prompt content."""
    return {
        "actionGroup": "travel_operations_tools",
        "function": "lookup_policy",
        "invocationId": str(uuid4()),
        "parameters": [],
        "sessionAttributes": {
            "travel_request_id": request_id,
            "tenant_id": tenant_id,
            "user_id": user_id,
        },
    }


def _delegated_tool_events(request_id: str, tenant_id: str, user_id: str) -> list[dict[str, Any]]:
    """Create the fixed, reviewable specialist plan for one durable travel case."""
    return [
        {
            **_tool_event(request_id, tenant_id, user_id),
            "function": function,
        }
        for function in (
            "profile_requirements",
            "policy_compliance_review",
            "travel_risk_review",
            "inventory_research",
            "itinerary_draft",
            "financial_triage",
        )
    ]


def _invoke_tool(
    client: LambdaInvoker, function_name: str, event: dict[str, Any]
) -> dict[str, Any]:
    """Invoke the durable-provenance tool synchronously."""
    response = client.invoke(
        FunctionName=function_name,
        InvocationType="RequestResponse",
        Payload=json.dumps(event).encode("utf-8"),
    )
    if response.get("FunctionError"):
        raise RuntimeError("Travel policy tool invocation failed")
    payload = response["Payload"].read()
    return json.loads(payload.decode("utf-8"))


@app.entrypoint
def invoke(payload: dict[str, Any]) -> dict[str, Any]:
    """Delegate a saved travel requirement to bounded specialist tools."""
    context = _required_context(payload)
    if context is None:
        return {"result": "A valid tenant-scoped travel case is required."}

    function_name = os.environ["AGENT_TOOLS_FUNCTION_NAME"]
    responses = []
    for event in _delegated_tool_events(*context):
        tool_response = _invoke_tool(boto3.client("lambda"), function_name, event)
        responses.append(
            {
                "agent": event["function"],
                "result": tool_response["response"]["functionResponse"]["responseBody"]["TEXT"][
                    "body"
                ],
            }
        )
    return {
        "result": "Draft itinerary prepared; human approval is required before any booking.",
        "orchestrator": "travel_itinerary_coordinator",
        "delegations": responses,
    }


if __name__ == "__main__":
    app.run()
