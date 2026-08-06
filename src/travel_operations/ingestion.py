"""S3 PDF ingestion into versioned CockroachDB vectors."""

import hashlib
import json
from io import BytesIO

import boto3
from pypdf import PdfReader
from sqlalchemy import text
from sqlalchemy.orm import Session


class DocumentIngestionService:
    def __init__(self, session: Session, bucket: str) -> None:
        self._session, self._bucket = session, bucket
        self._s3, self._bedrock = boto3.client("s3"), boto3.client("bedrock-runtime")

    def ingest_pdf(self, key: str) -> dict[str, object]:
        payload = self._s3.get_object(Bucket=self._bucket, Key=key)["Body"].read()
        version, document_id = (
            hashlib.sha256(payload).hexdigest(),
            hashlib.sha256(key.encode()).hexdigest(),
        )
        reader = PdfReader(BytesIO(payload))
        chunks = [
            "\n".join(page.extract_text() or "" for page in reader.pages)[i : i + 1200]
            for i in range(
                0, len("\n".join(page.extract_text() or "" for page in reader.pages)), 1000
            )
        ]
        for index, chunk in enumerate(item for item in chunks if item.strip()):
            response = self._bedrock.invoke_model(
                modelId="amazon.titan-embed-text-v2:0", body=json.dumps({"inputText": chunk})
            )
            embedding = json.loads(response["body"].read())["embedding"]
            self._session.execute(
                text(
                    "INSERT INTO knowledge_chunks (document_id, chunk_id, content, source_uri, version, page_count, embedding) VALUES (:d,:c,:t,:u,:v,:p,CAST(:e AS VECTOR))"
                ),
                {
                    "d": document_id,
                    "c": str(index),
                    "t": chunk,
                    "u": f"s3://{self._bucket}/{key}",
                    "v": version,
                    "p": len(reader.pages),
                    "e": str(embedding),
                },
            )
        return {"document_id": document_id, "version": version, "chunks": len(chunks)}
