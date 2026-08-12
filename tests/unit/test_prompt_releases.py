from pathlib import Path

import pytest

from travel_operations.prompts import PromptRelease, PromptReleaseRegistry

ROOT = Path(__file__).parents[2]


def test_active_prompt_has_required_governance_metadata_and_rollback() -> None:
    registry = PromptReleaseRegistry(ROOT)

    active = registry.active("rag_grounded_answer")
    rollback = registry.rollback("rag_grounded_answer")

    assert active.version == "v2"
    assert active.owner == "travel-operations-platform"
    assert active.model == "provider-agnostic-grounded-generator"
    assert active.evaluation_dataset == "evaluations/golden_datasets/travel_policy.json"
    assert rollback.version == "v1"


def test_prompt_release_requires_both_evaluation_gates() -> None:
    active = PromptReleaseRegistry(ROOT).active("rag_grounded_answer")

    assert active.is_eligible(0.75, 1.0)
    assert not active.is_eligible(0.74, 1.0)
    assert not active.is_eligible(1.0, 0.99)


def test_invalid_release_metadata_is_rejected() -> None:
    invalid = PromptRelease(
        prompt_id="policy",
        version="v1",
        template="rag_grounded_answer.md",
        owner="owner",
        model="model",
        evaluation_dataset="evaluations/golden_datasets/travel_policy.json",
        minimum_groundedness=1.1,
        minimum_citation_accuracy=1.0,
        rollback_version="v1",
        status="ACTIVE",
    )

    with pytest.raises(ValueError, match="groundedness"):
        PromptReleaseRegistry(ROOT)._validate(invalid)
