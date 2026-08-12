"""Validate a completed CockroachDB restore-drill evidence record."""

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

REQUIRED_TABLES = {"travel_requests", "agent_sessions", "agent_memory_events", "tool_executions"}


def _timestamp(value: object, name: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError(f"{name} must be an ISO-8601 timestamp")
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def validate_evidence(evidence: dict[str, Any], max_rpo_minutes: int, max_rto_minutes: int) -> None:
    """Reject unrecorded, failed, stale, or incomplete recovery evidence."""
    for field in ("drill_id", "environment", "backup_timestamp", "started_at", "completed_at"):
        if not evidence.get(field):
            raise ValueError(f"Missing required field: {field}")
    if evidence.get("result") != "PASSED":
        raise ValueError("Restore drill result must be PASSED")

    backup_time = _timestamp(evidence["backup_timestamp"], "backup_timestamp")
    started_at = _timestamp(evidence["started_at"], "started_at")
    completed_at = _timestamp(evidence["completed_at"], "completed_at")
    if backup_time > started_at or completed_at < started_at:
        raise ValueError("Restore timestamps are not ordered")
    rpo_minutes = (started_at - backup_time).total_seconds() / 60
    rto_minutes = (completed_at - started_at).total_seconds() / 60
    if rpo_minutes > max_rpo_minutes:
        raise ValueError(f"RPO {rpo_minutes:.1f} minutes exceeds {max_rpo_minutes} minutes")
    if rto_minutes > max_rto_minutes:
        raise ValueError(f"RTO {rto_minutes:.1f} minutes exceeds {max_rto_minutes} minutes")

    source_counts = evidence.get("source_row_counts")
    restored_counts = evidence.get("restored_row_counts")
    if not isinstance(source_counts, dict) or not isinstance(restored_counts, dict):
        raise ValueError("Source and restored row counts must be objects")
    if not REQUIRED_TABLES.issubset(source_counts) or not REQUIRED_TABLES.issubset(restored_counts):
        raise ValueError("Evidence must include every durable travel-case table")
    if source_counts != restored_counts:
        raise ValueError("Restored row counts do not match the source backup")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence_file", type=Path)
    parser.add_argument("--max-rpo-minutes", type=int, default=60)
    parser.add_argument("--max-rto-minutes", type=int, default=120)
    arguments = parser.parse_args()
    evidence = json.loads(arguments.evidence_file.read_text(encoding="utf-8"))
    validate_evidence(evidence, arguments.max_rpo_minutes, arguments.max_rto_minutes)
    print(f"Validated restore drill evidence: {evidence['drill_id']}")


if __name__ == "__main__":
    main()
