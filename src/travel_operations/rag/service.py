"""Grounded answer orchestration over approved, ACL-filtered retrieved context."""

from collections.abc import Callable
from dataclasses import dataclass

from travel_operations.rag.context import ContextBuilder
from travel_operations.rag.grounding import has_valid_citations
from travel_operations.rag.retriever import EmbeddingRetriever
from travel_operations.security import reject_prompt_injection


@dataclass(frozen=True)
class GroundedAnswer:
    answer: str
    citations: tuple[str, ...]
    confidence: float = 0.0
    outcome: str = "INSUFFICIENT_EVIDENCE"


_INSUFFICIENT_EVIDENCE = "Insufficient approved evidence to answer."
_SAFE_FALLBACK = "Unable to provide a grounded answer from the approved evidence."


class GroundedAnswerService:
    def __init__(self, retriever: EmbeddingRetriever, minimum_confidence: float = 0.75) -> None:
        if not 0 <= minimum_confidence <= 1:
            raise ValueError("minimum_confidence must be between zero and one")
        self._retriever = retriever
        self._minimum_confidence = minimum_confidence
        self._context = ContextBuilder()

    def answer(
        self,
        question: str,
        tenant_id: str,
        roles: frozenset[str],
        query_embedding: list[float],
        generate: Callable[[str, str], str],
    ) -> GroundedAnswer:
        """Generate only from filtered context and reject absent or fabricated citations."""
        reject_prompt_injection(question)
        chunks = self._retriever.search(tenant_id, roles, query_embedding)
        context = self._context.build(chunks)
        confidence = max((chunk.score for chunk in chunks), default=0.0)
        if not context or confidence < self._minimum_confidence:
            return GroundedAnswer(_INSUFFICIENT_EVIDENCE, (), confidence)
        try:
            answer = generate(question, context)
        except Exception:
            return GroundedAnswer(_SAFE_FALLBACK, (), confidence, "SAFE_FALLBACK")
        if not has_valid_citations(answer, chunks):
            return GroundedAnswer(_SAFE_FALLBACK, (), confidence, "SAFE_FALLBACK")
        return GroundedAnswer(
            answer,
            tuple(chunk.citation_id for chunk in chunks),
            confidence,
            "GROUNDED",
        )
