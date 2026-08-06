"""RAG value objects."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RetrievedChunk:
    document_id: str
    chunk_id: str
    content: str
    source_uri: str
    score: float

    @property
    def citation(self) -> str:
        return f"[{self.document_id}:{self.chunk_id}]({self.source_uri})"
