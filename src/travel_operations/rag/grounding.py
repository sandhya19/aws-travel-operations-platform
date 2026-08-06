"""Deterministic grounding guardrails."""

import re

from travel_operations.rag.models import RetrievedChunk


def has_valid_citations(answer: str, chunks: list[RetrievedChunk]) -> bool:
    """Require at least one citation and reject citations outside retrieved sources."""
    citations = set(re.findall(r"\[([^\]]+)\]", answer))
    allowed = {f"{chunk.document_id}:{chunk.chunk_id}" for chunk in chunks}
    return bool(citations) and citations.issubset(allowed)
