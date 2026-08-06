"""CockroachDB vector similarity retrieval."""

from sqlalchemy import text
from sqlalchemy.orm import Session

from travel_operations.rag.models import RetrievedChunk


class EmbeddingRetriever:
    """Ranks approved knowledge chunks by cosine distance."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def search(self, embedding: list[float], limit: int = 8) -> list[RetrievedChunk]:
        rows = self._session.execute(
            text(
                "SELECT document_id, chunk_id, content, source_uri, 1 - (embedding <=> CAST(:embedding AS VECTOR)) AS score FROM knowledge_chunks WHERE embedding IS NOT NULL ORDER BY embedding <=> CAST(:embedding AS VECTOR) LIMIT :limit"
            ),
            {"embedding": str(embedding), "limit": limit},
        )
        return [RetrievedChunk(*row) for row in rows]
