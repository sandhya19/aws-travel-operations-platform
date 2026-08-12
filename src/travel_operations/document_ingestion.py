"""S3 event adapter for the secure knowledge-document ingestion use case."""

import os
from urllib.parse import unquote_plus

from travel_operations.database import SessionFactory
from travel_operations.ingestion import DocumentIngestionService


def handler(event: dict[str, object], _: object) -> dict[str, int]:
    """Ingest tenant-prefixed PDF records delivered by the private knowledge bucket."""
    bucket = os.environ["KNOWLEDGE_BUCKET"]
    records = event.get("Records", [])
    if not isinstance(records, list):
        raise ValueError("S3 event must contain Records")
    ingested = 0
    with SessionFactory.begin() as session:
        service = DocumentIngestionService(session, bucket)
        for record in records:
            if not isinstance(record, dict):
                raise ValueError("S3 event record is invalid")
            s3_record = record.get("s3")
            if not isinstance(s3_record, dict):
                raise ValueError("S3 event record has no object")
            object_record = s3_record.get("object")
            if not isinstance(object_record, dict) or not isinstance(object_record.get("key"), str):
                raise ValueError("S3 event object has no key")
            key = unquote_plus(object_record["key"])
            tenant_id = key.split("/", maxsplit=1)[0]
            service.ingest_pdf(key, tenant_id)
            ingested += 1
    return {"ingested": ingested}
