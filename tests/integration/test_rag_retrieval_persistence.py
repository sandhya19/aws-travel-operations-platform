"""Opt-in CockroachDB coverage for tenant and role-filtered vector retrieval."""

import os

import pytest
from sqlalchemy import text

from travel_operations.database import SessionFactory
from travel_operations.models import KnowledgeDocumentAccessModel, KnowledgeDocumentModel
from travel_operations.rag.retriever import EmbeddingRetriever
from travel_operations.repositories.knowledge_documents import KnowledgeDocumentRepository


@pytest.mark.database  # type: ignore[misc]
def test_retrieval_filters_by_tenant_and_document_role() -> None:
    if os.getenv("RUN_DATABASE_INTEGRATION") != "1":
        pytest.skip("Set RUN_DATABASE_INTEGRATION=1 to run against the configured database")

    document_id = "c" * 64
    version = "d" * 64
    try:
        with SessionFactory.begin() as session:
            document = KnowledgeDocumentRepository(session).add_document(
                document_id,
                "integration-rag-tenant",
                "integration-rag/policy.pdf",
                version,
                "application/pdf",
                1,
                ("travel:read",),
            )
            KnowledgeDocumentRepository(session).add_chunks(
                document,
                [("1-0", 1, "Approved policy evidence", [0.1] * 1024)],
                "s3://integration-rag/integration-rag/policy.pdf",
            )

        with SessionFactory() as session:
            retriever = EmbeddingRetriever(session)
            assert (
                len(
                    retriever.search(
                        "integration-rag-tenant", frozenset({"travel:read"}), [0.1] * 1024
                    )
                )
                == 1
            )
            assert retriever.search("integration-rag-tenant", frozenset(), [0.1] * 1024) == []
            assert retriever.search("other-tenant", frozenset({"travel:read"}), [0.1] * 1024) == []
    finally:
        with SessionFactory.begin() as session:
            session.execute(
                text("DELETE FROM knowledge_chunks WHERE document_id = :document_id"),
                {"document_id": document_id},
            )
            session.query(KnowledgeDocumentAccessModel).filter_by(document_id=document_id).delete()
            session.query(KnowledgeDocumentModel).filter_by(document_id=document_id).delete()
