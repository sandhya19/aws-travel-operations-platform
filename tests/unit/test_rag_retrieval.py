"""IMP-014 retrieval, grounding, and citation regression coverage."""

from travel_operations.rag.models import RetrievedChunk
from travel_operations.rag.retriever import EmbeddingRetriever
from travel_operations.rag.service import GroundedAnswerService


class FakeSession:
    def __init__(self, rows: list[tuple[object, ...]]) -> None:
        self.rows = rows
        self.statement = ""
        self.parameters: dict[str, object] = {}

    def execute(self, statement: object, parameters: dict[str, object]) -> list[tuple[object, ...]]:
        self.statement = str(statement)
        self.parameters = parameters
        return self.rows


def test_retrieval_query_filters_by_tenant_and_document_role() -> None:
    session = FakeSession(
        [("doc", "1-0", "Policy evidence", "s3://bucket/acme/policy.pdf", 0.9, "v1", 1)]
    )

    chunks = EmbeddingRetriever(session).search("acme", frozenset({"travel:read"}), [0.1] * 1024)

    assert chunks[0].citation_id == "doc:1-0:v1"
    assert "chunk.tenant_id = :tenant_id" in session.statement
    assert "knowledge_document_access" in session.statement
    assert session.parameters["tenant_id"] == "acme"
    assert session.parameters["roles"] == ["travel:read"]


class FakeRetriever:
    def __init__(self, chunks: list[RetrievedChunk]) -> None:
        self.chunks = chunks

    def search(self, *_: object) -> list[RetrievedChunk]:
        return self.chunks


def _chunk() -> RetrievedChunk:
    return RetrievedChunk(
        "doc", "1-0", "Approved policy evidence", "s3://bucket/doc.pdf", 0.9, "v1", 1
    )


def test_grounded_answer_accepts_only_retrieved_versioned_citations() -> None:
    service = GroundedAnswerService(FakeRetriever([_chunk()]))  # type: ignore[arg-type]

    answer = service.answer(
        "What is approved?",
        "acme",
        frozenset({"travel:read"}),
        [0.1] * 1024,
        lambda _, __: "Approved policy evidence [doc:1-0:v1]",
    )

    assert answer.citations == ("doc:1-0:v1",)
    assert answer.outcome == "GROUNDED"
    assert answer.confidence == 0.9


def test_grounded_answer_falls_back_for_fabricated_citations() -> None:
    service = GroundedAnswerService(FakeRetriever([_chunk()]))  # type: ignore[arg-type]

    answer = service.answer(
        "What is approved?",
        "acme",
        frozenset(),
        [0.1] * 1024,
        lambda _, __: "Unsupported [other:1:v1]",
    )

    assert answer.outcome == "SAFE_FALLBACK"
    assert answer.citations == ()


def test_grounded_answer_returns_insufficient_evidence_for_low_confidence() -> None:
    low_confidence = RetrievedChunk(
        "doc", "1-1", "Possibly relevant", "s3://bucket/doc.pdf", 0.74, "v1", 2
    )
    service = GroundedAnswerService(FakeRetriever([low_confidence]))  # type: ignore[arg-type]

    answer = service.answer("What is approved?", "acme", frozenset(), [0.1] * 1024, lambda *_: "")

    assert answer.outcome == "INSUFFICIENT_EVIDENCE"
    assert answer.citations == ()


def test_grounded_answer_falls_back_when_generation_fails() -> None:
    service = GroundedAnswerService(FakeRetriever([_chunk()]))  # type: ignore[arg-type]

    def fail(_: str, __: str) -> str:
        raise RuntimeError("provider error")

    answer = service.answer("What is approved?", "acme", frozenset(), [0.1] * 1024, fail)

    assert answer.outcome == "SAFE_FALLBACK"
