"""Source-controlled prompt release selection and rollback validation."""

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PromptRelease:
    prompt_id: str
    version: str
    template: str
    owner: str
    model: str
    evaluation_dataset: str
    minimum_groundedness: float
    minimum_citation_accuracy: float
    rollback_version: str
    status: str

    def is_eligible(self, groundedness: float, citation_accuracy: float) -> bool:
        """Require both configured release gates to pass."""
        return (
            groundedness >= self.minimum_groundedness
            and citation_accuracy >= self.minimum_citation_accuracy
        )


class PromptReleaseRegistry:
    """Load reviewed prompt releases from the version-controlled registry."""

    def __init__(self, repository_root: Path) -> None:
        self._root = repository_root
        self._releases = self._load()

    def active(self, prompt_id: str) -> PromptRelease:
        """Return the exactly one release eligible for new traffic."""
        matches = [
            release
            for release in self._releases
            if release.prompt_id == prompt_id and release.status == "ACTIVE"
        ]
        if len(matches) != 1:
            raise ValueError(f"Prompt {prompt_id!r} must have exactly one active release")
        return matches[0]

    def rollback(self, prompt_id: str) -> PromptRelease:
        """Resolve the reviewed fallback for the active release."""
        active = self.active(prompt_id)
        for release in self._releases:
            if release.prompt_id == prompt_id and release.version == active.rollback_version:
                return release
        raise ValueError(f"Prompt {prompt_id!r} has no valid rollback release")

    def _load(self) -> tuple[PromptRelease, ...]:
        registry = self._root / "prompts" / "releases.json"
        raw = json.loads(registry.read_text(encoding="utf-8"))
        values = raw.get("releases")
        if not isinstance(values, list):
            raise ValueError("Prompt release registry must contain a releases list")
        releases = tuple(PromptRelease(**value) for value in values)
        for release in releases:
            self._validate(release)
        return releases

    def _validate(self, release: PromptRelease) -> None:
        if not all(
            (
                release.prompt_id,
                release.version,
                release.template,
                release.owner,
                release.model,
                release.evaluation_dataset,
                release.rollback_version,
            )
        ):
            raise ValueError("Prompt release metadata fields must not be empty")
        if release.status not in {"ACTIVE", "RETIRED"}:
            raise ValueError("Prompt release status must be ACTIVE or RETIRED")
        if not 0 <= release.minimum_groundedness <= 1:
            raise ValueError("Prompt groundedness gate must be between zero and one")
        if not 0 <= release.minimum_citation_accuracy <= 1:
            raise ValueError("Prompt citation-accuracy gate must be between zero and one")
        if not (self._root / "prompts" / release.template).is_file():
            raise ValueError(f"Prompt template does not exist: {release.template}")
        if not (self._root / release.evaluation_dataset).is_file():
            raise ValueError(
                f"Prompt evaluation dataset does not exist: {release.evaluation_dataset}"
            )
