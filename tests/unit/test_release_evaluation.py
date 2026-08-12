import json
from pathlib import Path

import pytest

from travel_operations.evaluations import evaluate, evaluate_release
from travel_operations.prompts import PromptReleaseRegistry

ROOT = Path(__file__).parents[2]


def _release_and_dataset() -> tuple[object, list[dict[str, object]]]:
    release = PromptReleaseRegistry(ROOT).active("rag_grounded_answer")
    dataset = json.loads((ROOT / release.evaluation_dataset).read_text(encoding="utf-8"))
    return release, dataset


def test_insufficient_evidence_reference_scores_as_safe_grounded_outcome() -> None:
    result = evaluate("Insufficient approved evidence to answer.", "", [], 0.0)

    assert result.groundedness == 1
    assert result.citation_accuracy == 1


def test_release_benchmark_passes_registered_baseline() -> None:
    release, dataset = _release_and_dataset()
    answers = json.loads(
        (ROOT / "evaluations" / "baselines" / "rag_grounded_answer.v2.json").read_text(
            encoding="utf-8"
        )
    )

    report = evaluate_release(release, dataset, answers)  # type: ignore[arg-type]

    assert report.passed
    assert report.case_count == 2
    assert report.citation_accuracy == 1


def test_release_benchmark_rejects_missing_or_failing_answers() -> None:
    release, dataset = _release_and_dataset()

    with pytest.raises(ValueError, match="Missing candidate answer"):
        evaluate_release(release, dataset, {"policy-001": "Unsupported"})  # type: ignore[arg-type]

    report = evaluate_release(
        release,
        dataset,
        {
            "policy-001": "Unsupported [other:1]",
            "policy-002-insufficient-evidence": "Private charter is approved.",
        },
    )  # type: ignore[arg-type]

    assert not report.passed
