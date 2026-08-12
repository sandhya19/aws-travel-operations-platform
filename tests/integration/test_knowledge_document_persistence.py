"""Opt-in CockroachDB persistence coverage for IMP-013 document versions."""

import os

import pytest
from sqlalchemy import text

from travel_operations.database import SessionFactory
from travel_operations.models import KnowledgeDocumentModel
from travel_operations.repositories.knowledge_documents import KnowledgeDocumentRepository


@pytest.mark.database  # type: ignore[misc]
def test_knowledge_document_version_and_chunk_persist_to_cockroachdb() -> None:
    if os.getenv("RUN_DATABASE_INTEGRATION") != "1":
        pytest.skip("Set RUN_DATABASE_INTEGRATION=1 to run against the configured database")

    document_id = "a" * 64
    version = "b" * 64
    try:
        with SessionFactory.begin() as session:
            repository = KnowledgeDocumentRepository(session)
            document = repository.add_document(
                document_id,
                "integration-test-tenant",
                "integration-test/policy.pdf",
                version,
                "application/pdf",
                1,
            )
            repository.add_chunks(
                document,
                [("1-0", 1, "Approved policy text", [0.1] * 1024)],
                "s3://integration-test/integration-test/policy.pdf",
            )

        with SessionFactory() as session:
            repository = KnowledgeDocumentRepository(session)
            stored = repository.find_version(
                "integration-test-tenant", "integration-test/policy.pdf", version
            )
            assert stored is not None
            assert repository.chunk_count(document_id, version) == 1
    finally:
        with SessionFactory.begin() as session:
            session.execute(
                text("DELETE FROM knowledge_chunks WHERE document_id = :document_id"),
                {"document_id": document_id},
            )
            session.query(KnowledgeDocumentModel).filter_by(document_id=document_id).delete()
