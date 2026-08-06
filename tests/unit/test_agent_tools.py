from travel_operations.agent_tools import handler


def test_lambda_tool_response_includes_action_group() -> None:
    response = handler({"actionGroup": "policy", "function": "lookup_policy"}, None)
    assert response["response"]["actionGroup"] == "policy"
