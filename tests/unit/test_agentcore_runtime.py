import importlib.util
import io
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from uuid import uuid4

import pytest


def _load_runtime_module(monkeypatch: pytest.MonkeyPatch) -> Any:
    """Load the runtime entry point with a small local AgentCore SDK substitute."""
    class App:
        def entrypoint(self, function: object) -> object:
            return function

        def run(self) -> None:
            return None

    module = SimpleNamespace(BedrockAgentCoreApp=App)
    monkeypatch.setitem(__import__("sys").modules, "bedrock_agentcore", module)
    spec = importlib.util.spec_from_file_location(
        "agentcore_runtime_under_test",
        Path(__file__).parents[2] / "agent_runtime" / "agent.py",
    )
    assert spec is not None and spec.loader is not None
    runtime = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runtime)
    return runtime


def test_runtime_requires_a_complete_tenant_context(monkeypatch: pytest.MonkeyPatch) -> None:
    runtime = _load_runtime_module(monkeypatch)
    request_id = str(uuid4())

    assert runtime._required_context({"travel_request_id": request_id}) is None
    assert runtime._required_context(
        {"travel_request_id": request_id, "tenant_id": "acme", "user_id": "employee"}
    ) == (request_id, "acme", "employee")


def test_runtime_tool_event_does_not_include_prompt_content(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime = _load_runtime_module(monkeypatch)

    event = runtime._tool_event(str(uuid4()), "acme", "employee")

    assert event["function"] == "lookup_policy"
    assert event["parameters"] == []
    assert event["sessionAttributes"]["tenant_id"] == "acme"


def test_runtime_delegates_to_the_fixed_specialist_plan(monkeypatch: pytest.MonkeyPatch) -> None:
    runtime = _load_runtime_module(monkeypatch)

    events = runtime._delegated_tool_events(str(uuid4()), "acme", "employee")

    assert [event["function"] for event in events] == [
        "profile_requirements",
        "policy_compliance_review",
        "travel_risk_review",
        "inventory_research",
        "itinerary_draft",
        "financial_triage",
    ]
    assert all(event["parameters"] == [] for event in events)


def test_runtime_raises_a_generic_error_when_the_tool_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    runtime = _load_runtime_module(monkeypatch)

    class FailingClient:
        def invoke(self, **_: object) -> dict[str, object]:
            return {"FunctionError": "Unhandled", "Payload": io.BytesIO(b"sensitive")}

    try:
        runtime._invoke_tool(FailingClient(), "agent-tools", {})
    except RuntimeError as error:
        assert str(error) == "Travel policy tool invocation failed"
    else:
        raise AssertionError("A failed tool invocation must raise a generic error")
