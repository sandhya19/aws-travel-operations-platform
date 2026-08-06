"""API contract checks for the IMP-003 approval endpoint."""

import ast
from pathlib import Path


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
