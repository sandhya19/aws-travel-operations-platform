"""Deterministic RAG evaluation metrics and prompt comparison."""

import re
from collections.abc import Mapping
from dataclasses import dataclass

from travel_operations.prompts import PromptRelease


@dataclass(frozen=True)
class EvaluationResult:
    groundedness: float
    faithfulness: float
    latency_ms: float
    citation_accuracy: float


@dataclass(frozen=True)
class ReleaseEvaluation:
    prompt_id: str
    prompt_version: str
    passed: bool
    groundedness: float
    citation_accuracy: float
    case_count: int


def evaluate(
    answer: str, context: str, expected_citations: list[str], elapsed_seconds: float
) -> EvaluationResult:
    citations = set(re.findall(r"\[([^\]]+)\]", answer))
    if not context.strip() and not expected_citations:
        safe_outcome = answer.strip() == "Insufficient approved evidence to answer."
        score = 1.0 if safe_outcome else 0.0
        return EvaluationResult(score, score, elapsed_seconds * 1000, score)
    answer_terms = {term.lower() for term in re.findall(r"\w+", answer) if len(term) > 3}
    context_terms = {term.lower() for term in re.findall(r"\w+", context) if len(term) > 3}
    groundedness = len(answer_terms & context_terms) / max(1, len(answer_terms))
    citation_accuracy = len(citations & set(expected_citations)) / max(1, len(citations))
    return EvaluationResult(groundedness, groundedness, elapsed_seconds * 1000, citation_accuracy)


def compare_prompts(results: dict[str, EvaluationResult]) -> str:
    return max(
        results,
        key=lambda version: results[version].groundedness + results[version].citation_accuracy,
    )


def evaluate_release(
    release: PromptRelease,
    dataset: list[dict[str, object]],
    answers: Mapping[str, str],
) -> ReleaseEvaluation:
    """Evaluate a candidate release against every linked golden-dataset case."""
    results: list[EvaluationResult] = []
    expected_ids: set[str] = set()
    for case in dataset:
        case_id = case.get("id")
        context = case.get("context")
        citations = case.get("expected_citations")
        valid_case = (
            isinstance(case_id, str) and isinstance(context, str) and isinstance(citations, list)
        )
        if not valid_case:
            raise ValueError("Each evaluation case requires id, context, and expected_citations")
        if not all(isinstance(citation, str) for citation in citations):
            raise ValueError("Expected citations must be strings")
        if case_id not in answers:
            raise ValueError(f"Missing candidate answer for evaluation case {case_id!r}")
        expected_ids.add(case_id)
        results.append(evaluate(answers[case_id], context, citations, 0.0))
    if set(answers) != expected_ids:
        raise ValueError("Candidate answers must match the evaluation dataset case IDs exactly")
    if not results:
        raise ValueError("Evaluation dataset must not be empty")
    groundedness = sum(result.groundedness for result in results) / len(results)
    citation_accuracy = sum(result.citation_accuracy for result in results) / len(results)
    return ReleaseEvaluation(
        release.prompt_id,
        release.version,
        release.is_eligible(groundedness, citation_accuracy),
        groundedness,
        citation_accuracy,
        len(results),
    )
