"""Validated, tenant-owned PDF ingestion for approved knowledge sources."""

import hashlib
import json
import re
from collections.abc import Iterable
from io import BytesIO
from typing import Any

import boto3
from sqlalchemy.orm import Session

from travel_operations.repositories.knowledge_documents import KnowledgeDocumentRepository
from travel_operations.security import reject_prompt_injection

_ALLOWED_CONTENT_TYPES = frozenset({"application/pdf", "application/x-pdf"})
_SAFE_KEY = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._/-]*\.pdf$")
_EMBEDDING_DIMENSIONS = 1024

try:
    from pypdf import PdfReader
except ImportError:  # pragma: no cover - exercised only in incomplete local environments
    PdfReader: Any = None


class DocumentIngestionError(ValueError):
    """Raised when a knowledge document fails the ingestion security contract."""


class DocumentIngestionService:
    """Coordinates object validation, extraction, embedding, and durable version storage."""

    def __init__(
        self,
        session: Session,
        bucket: str,
        *,
        s3_client: Any | None = None,
        bedrock_client: Any | None = None,
        max_document_bytes: int = 10 * 1024 * 1024,
    ) -> None:
        self._repository = KnowledgeDocumentRepository(session)
        self._bucket = bucket
        self._s3 = s3_client or boto3.client("s3")
        self._bedrock = bedrock_client or boto3.client("bedrock-runtime")
        self._max_document_bytes = max_document_bytes

    def ingest_pdf(self, key: str, tenant_id: str) -> dict[str, object]:
        """Persist an idempotent, validated PDF version and its Titan embeddings."""
        self._validate_key(key, tenant_id)
        head = self._s3.head_object(Bucket=self._bucket, Key=key)
        content_type = str(head.get("ContentType", "")).lower()
        allowed_roles = self._allowed_roles(head.get("Metadata", {}))
        content_length = head.get("ContentLength")
        if content_type not in _ALLOWED_CONTENT_TYPES:
            raise DocumentIngestionError("Knowledge source must declare application/pdf")
        if (
            not isinstance(content_length, int)
            or not 0 < content_length <= self._max_document_bytes
        ):
            raise DocumentIngestionError("Knowledge source exceeds the permitted size")

        payload = self._s3.get_object(Bucket=self._bucket, Key=key)["Body"].read()
        if len(payload) != content_length or not payload.startswith(b"%PDF-"):
            raise DocumentIngestionError("Knowledge source is not a valid PDF payload")
        version = hashlib.sha256(payload).hexdigest()
        existing = self._repository.find_version(tenant_id, key, version)
        if existing is not None:
            return {
                "document_id": existing.document_id,
                "version": existing.version,
                "chunks": self._repository.chunk_count(existing.document_id, existing.version),
                "created": False,
            }

        if PdfReader is None:
            raise RuntimeError("pypdf must be installed to ingest knowledge documents")
        reader = PdfReader(BytesIO(payload))
        if reader.is_encrypted:
            raise DocumentIngestionError("Encrypted PDFs are not accepted")
        pages = [(number, page.extract_text() or "") for number, page in enumerate(reader.pages, 1)]
        chunks = list(self._chunks(pages))
        if not chunks:
            raise DocumentIngestionError("Knowledge source contains no extractable text")

        document_id = hashlib.sha256(f"{tenant_id}:{key}:{version}".encode()).hexdigest()
        document = self._repository.add_document(
            document_id, tenant_id, key, version, content_type, len(pages), allowed_roles
        )
        embedded_chunks = [
            (chunk_id, page_number, content, self._embed(content))
            for chunk_id, page_number, content in chunks
        ]
        self._repository.add_chunks(document, embedded_chunks, f"s3://{self._bucket}/{key}")
        return {
            "document_id": document.document_id,
            "version": document.version,
            "chunks": len(embedded_chunks),
            "created": True,
        }

    def _embed(self, content: str) -> list[float]:
        response = self._bedrock.invoke_model(
            modelId="amazon.titan-embed-text-v2:0",
            body=json.dumps({"inputText": content, "dimensions": _EMBEDDING_DIMENSIONS}),
        )
        embedding = json.loads(response["body"].read()).get("embedding")
        if (
            not isinstance(embedding, list)
            or len(embedding) != _EMBEDDING_DIMENSIONS
            or not all(isinstance(value, int | float) for value in embedding)
        ):
            raise DocumentIngestionError(
                "Embedding response did not match the configured dimensions"
            )
        return [float(value) for value in embedding]

    @staticmethod
    def _validate_key(key: str, tenant_id: str) -> None:
        if (
            not tenant_id
            or not _SAFE_KEY.fullmatch(key)
            or ".." in key.split("/")
            or not key.startswith(f"{tenant_id}/")
        ):
            raise DocumentIngestionError("Knowledge source key is outside the tenant PDF namespace")

    @staticmethod
    def _allowed_roles(metadata: object) -> tuple[str, ...]:
        if not isinstance(metadata, dict):
            raise DocumentIngestionError("Knowledge source metadata is invalid")
        raw_roles = metadata.get("access-roles", "")
        if not isinstance(raw_roles, str):
            raise DocumentIngestionError("Knowledge source access roles are invalid")
        roles = tuple(role.strip() for role in raw_roles.split(",") if role.strip())
        if any(len(role) > 255 or not re.fullmatch(r"[A-Za-z0-9:_-]+", role) for role in roles):
            raise DocumentIngestionError("Knowledge source access roles are invalid")
        return tuple(dict.fromkeys(roles))

    @staticmethod
    def _chunks(pages: Iterable[tuple[int, str]]) -> Iterable[tuple[str, int, str]]:
        for page_number, page_text in pages:
            content = page_text.strip()
            if not content:
                continue
            try:
                reject_prompt_injection(content)
            except ValueError as error:
                raise DocumentIngestionError(
                    "Knowledge source contains unsafe instructions"
                ) from error
            for offset in range(0, len(content), 1000):
                chunk = content[offset : offset + 1200].strip()
                if chunk:
                    yield f"{page_number}-{offset}", page_number, chunk
