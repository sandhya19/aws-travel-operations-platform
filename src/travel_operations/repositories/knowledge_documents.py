"""CockroachDB persistence boundary for approved knowledge-document versions."""

from collections.abc import Sequence

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from travel_operations.models import KnowledgeDocumentAccessModel, KnowledgeDocumentModel


class KnowledgeDocumentRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def find_version(
        self, tenant_id: str, source_key: str, version: str
    ) -> KnowledgeDocumentModel | None:
        return self._session.scalar(
            select(KnowledgeDocumentModel).where(
                KnowledgeDocumentModel.tenant_id == tenant_id,
                KnowledgeDocumentModel.source_key == source_key,
                KnowledgeDocumentModel.version == version,
            )
        )

    def add_document(
        self,
        document_id: str,
        tenant_id: str,
        source_key: str,
        version: str,
        content_type: str,
        page_count: int,
        allowed_roles: tuple[str, ...] = (),
    ) -> KnowledgeDocumentModel:
        document = KnowledgeDocumentModel(
            document_id=document_id,
            tenant_id=tenant_id,
            source_key=source_key,
            version=version,
            content_type=content_type,
            page_count=page_count,
        )
        self._session.add(document)
        self._session.flush()
        self._session.add_all(
            KnowledgeDocumentAccessModel(document_id=document_id, role=role)
            for role in allowed_roles
        )
        self._session.flush()
        return document

    def chunk_count(self, document_id: str, version: str) -> int:
        count = self._session.scalar(
            text(
                "SELECT count(*) FROM knowledge_chunks "
                "WHERE document_id = :document_id AND version = :version"
            ),
            {"document_id": document_id, "version": version},
        )
        return int(count or 0)

    def add_chunks(
        self,
        document: KnowledgeDocumentModel,
        chunks: Sequence[tuple[str, int, str, list[float]]],
        source_uri: str,
    ) -> None:
        statement = text(
            "INSERT INTO knowledge_chunks "
            "(document_id, chunk_id, content, source_uri, version, page_count, tenant_id, "
            "page_number, embedding) "
            "VALUES (:document_id, :chunk_id, :content, :source_uri, :version, :page_count, "
            ":tenant_id, :page_number, CAST(:embedding AS VECTOR))"
        )
        for chunk_id, page_number, content, embedding in chunks:
            self._session.execute(
                statement,
                {
                    "document_id": document.document_id,
                    "chunk_id": chunk_id,
                    "content": content,
                    "source_uri": source_uri,
                    "version": document.version,
                    "page_count": document.page_count,
                    "tenant_id": document.tenant_id,
                    "page_number": page_number,
                    "embedding": str(embedding),
                },
            )
