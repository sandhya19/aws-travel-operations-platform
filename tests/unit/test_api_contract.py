"""API contract checks for the IMP-003 approval endpoint."""

import ast
from pathlib import Path

import pytest

from travel_operations.recovery import should_simulate_approval_callback_failure


def test_approval_endpoint_declares_accepted_response() -> None:
    """The Lambda adapter declares the asynchronous approval endpoint contract."""
    source_path = Path(__file__).parents[2] / "src" / "travel_operations" / "api" / "main.py"
    module = ast.parse(source_path.read_text(encoding="utf-8"))
    approval = next(
        node
        for node in module.body
        if isinstance(node, ast.FunctionDef) and node.name == "approve_travel_request"
    )
    decorator = next(
        node
        for node in approval.decorator_list
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "post"
        and isinstance(node.args[0], ast.Constant)
        and node.args[0].value == "/travel-request/{request_id}/approval"
    )

    assert any(
        isinstance(keyword.value, ast.Attribute)
        and keyword.arg == "status_code"
        and keyword.value.attr == "HTTP_202_ACCEPTED"
        for keyword in decorator.keywords
    )


def test_request_commit_precedes_eventbridge_publication() -> None:
    """The request and outbox event must commit before an AWS side effect."""
    source_path = Path(__file__).parents[2] / "src" / "travel_operations" / "api" / "main.py"
    module = ast.parse(source_path.read_text(encoding="utf-8"))
    endpoint = next(
        node
        for node in module.body
        if isinstance(node, ast.FunctionDef) and node.name == "create_travel_request"
    )
    calls = [
        call.func.attr
        for call in ast.walk(endpoint)
        if isinstance(call, ast.Call)
        and isinstance(call.func, ast.Attribute)
        and isinstance(call.func.value, ast.Name)
        and call.func.value.id == "service"
    ]

    assert calls.index("commit") < calls.index("mark_outbox_event_published")


def test_memory_endpoint_is_scoped_to_a_travel_request() -> None:
    source_path = Path(__file__).parents[2] / "src" / "travel_operations" / "api" / "main.py"
    module = ast.parse(source_path.read_text(encoding="utf-8"))

    endpoint = next(
        node
        for node in module.body
        if isinstance(node, ast.FunctionDef) and node.name == "get_travel_request_memory"
    )
    decorator = next(
        node
        for node in endpoint.decorator_list
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "get"
    )

    assert decorator.args[0].value == "/travel-request/{request_id}/memory"


def test_recovery_drill_switch_requires_dev_and_explicit_enablement(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("SIMULATE_APPROVAL_CALLBACK_FAILURE", "true")
    monkeypatch.setenv("ENVIRONMENT", "prod")
    assert not should_simulate_approval_callback_failure()

    monkeypatch.setenv("ENVIRONMENT", "dev")
    assert should_simulate_approval_callback_failure()


def test_rejection_and_approval_history_routes_are_declared() -> None:
    source_path = Path(__file__).parents[2] / "src" / "travel_operations" / "api" / "main.py"
    source = source_path.read_text(encoding="utf-8")

    assert '"/travel-request/{request_id}/rejection"' in source
    assert '"/travel-request/{request_id}/approval-history"' in source


def test_interactive_itinerary_route_is_declared_as_a_non_booking_draft() -> None:
    source_path = Path(__file__).parents[2] / "src" / "travel_operations" / "api" / "main.py"
    source = source_path.read_text(encoding="utf-8")
    itinerary_source = (
        Path(__file__).parents[2]
        / "src"
        / "travel_operations"
        / "services"
        / "itineraries.py"
    ).read_text(encoding="utf-8")

    assert '@app.post("/itineraries"' in source
    assert '"booking_status": "NOT_BOOKED"' in itinerary_source


def test_itinerary_requirements_apply_prompt_injection_validation() -> None:
    source_path = Path(__file__).parents[2] / "src" / "travel_operations" / "api" / "main.py"
    source = source_path.read_text(encoding="utf-8")

    assert '@field_validator("purpose")' in source
    assert '@field_validator("interests")' in source
    assert "reject_prompt_injection" in source
