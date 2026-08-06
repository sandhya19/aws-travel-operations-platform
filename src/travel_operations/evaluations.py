"""Deterministic RAG evaluation metrics and prompt comparison."""

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class EvaluationResult:
    groundedness: float
    faithfulness: float
    latency_ms: float
    citation_accuracy: float


def evaluate(
    answer: str, context: str, expected_citations: list[str], elapsed_seconds: float
) -> EvaluationResult:
    citations = set(re.findall(r"\[([^\]]+)\]", answer))
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
