"""RAG value objects."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RetrievedChunk:
    document_id: str
    chunk_id: str
    content: str
    source_uri: str
    score: float
    version: str
    page_number: int

    @property
    def citation(self) -> str:
        citation_id = self.citation_id
        return f"[{citation_id}]({self.source_uri}#page={self.page_number})"

    @property
    def citation_id(self) -> str:
        return f"{self.document_id}:{self.chunk_id}:{self.version}"
