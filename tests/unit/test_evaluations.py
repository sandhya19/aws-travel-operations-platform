from travel_operations.evaluations import compare_prompts, evaluate


def test_evaluation_scores_grounded_cited_answer() -> None:
    result = evaluate(
        "Business class requires approval [policy:12].",
        "Business class requires executive approval.",
        ["policy:12"],
        0.1,
    )
    assert result.citation_accuracy == 1
    assert result.groundedness > 0


def test_prompt_comparison_prefers_grounded_prompt() -> None:
    low = evaluate("Unknown", "Policy text", [], 0.1)
    high = evaluate("Policy [policy:1]", "Policy text", ["policy:1"], 0.1)
    assert compare_prompts({"v1": low, "v2": high}) == "v2"
