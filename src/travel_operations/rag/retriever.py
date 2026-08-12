"""CockroachDB vector retrieval with tenant and document-role filtering."""

from sqlalchemy import bindparam, text
from sqlalchemy.orm import Session

from travel_operations.rag.models import RetrievedChunk


class EmbeddingRetriever:
    def __init__(self, session: Session) -> None:
        self._session = session

    def search(
        self, tenant_id: str, roles: frozenset[str], embedding: list[float], limit: int = 8
    ) -> list[RetrievedChunk]:
        """Retrieve only chunks visible to the tenant and caller's roles."""
        if not 1 <= limit <= 20:
            raise ValueError("limit must be between one and twenty")
        role_clause = (
            "NOT EXISTS (SELECT 1 FROM knowledge_document_access AS access "
            "WHERE access.document_id = chunk.document_id)"
        )
        parameters: dict[str, object] = {
            "tenant_id": tenant_id,
            "embedding": str(embedding),
            "limit": limit,
        }
        if roles:
            role_clause = (
                f"({role_clause} OR EXISTS (SELECT 1 FROM knowledge_document_access AS access "
                "WHERE access.document_id = chunk.document_id AND access.role IN :roles))"
            )
            parameters["roles"] = list(roles)
        statement = text(
            "SELECT chunk.document_id, chunk.chunk_id, chunk.content, chunk.source_uri, "
            "1 - (chunk.embedding <=> CAST(:embedding AS VECTOR(1024))) AS score, chunk.version, "
            "chunk.page_number "
            "FROM knowledge_chunks AS chunk "
            "WHERE chunk.tenant_id = :tenant_id AND chunk.embedding IS NOT NULL "
            f"AND {role_clause} "
            "ORDER BY chunk.embedding <=> CAST(:embedding AS VECTOR(1024)) LIMIT :limit"
        )
        if roles:
            statement = statement.bindparams(bindparam("roles", expanding=True))
        rows = self._session.execute(statement, parameters)
        return [RetrievedChunk(*row) for row in rows]
