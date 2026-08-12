"""Unit tests for Milestone 4 operational evidence tooling."""

import importlib.util
import sys
from pathlib import Path
from typing import Any

import pytest


def _load_script(name: str) -> Any:
    scripts_directory = Path(__file__).parents[2] / "scripts"
    if str(scripts_directory) not in sys.path:
        sys.path.insert(0, str(scripts_directory))
    path = scripts_directory / name
    spec = importlib.util.spec_from_file_location(name.removesuffix(".py"), path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_workflow_benchmark_reports_success_latency_and_throughput() -> None:
    benchmark = _load_script("benchmark_workflow.py")
    timestamps = iter([0.0, 0.0, 0.1, 0.2, 0.4, 0.5, 0.9, 1.0])

    result = benchmark.run_benchmark(
        lambda: {"status": "COMPLETED"}, requests=3, concurrency=1, clock=lambda: next(timestamps)
    )

    assert result["successful_requests"] == 3
    assert result["failed_requests"] == 0
    assert result["success_rate"] == 1
    assert result["latency_ms"]["p95"] == 400.0


def test_workflow_benchmark_reports_failure_types_without_response_content() -> None:
    benchmark = _load_script("benchmark_workflow.py")

    result = benchmark.run_benchmark(
        lambda: (_ for _ in ()).throw(RuntimeError("sensitive response")),
        requests=1,
        concurrency=1,
        clock=lambda: 1.0,
    )

    assert result["failure_types"] == {"RuntimeError": 1}
    assert "sensitive" not in str(result)


def test_kpi_comparison_requires_completed_runs() -> None:
    comparison = _load_script("compare_kpi_benchmarks.py")
    baseline = {
        "label": "baseline",
        "success_rate": 1,
        "requests_per_second": 2,
        "latency_ms": {"p95": 100},
    }
    assisted = {
        "label": "assisted",
        "success_rate": 1,
        "requests_per_second": 3,
        "latency_ms": {"p95": 125},
    }

    result = comparison.compare(baseline, assisted)

    assert result["p95_delta_ms"] == 25.0
    assert result["throughput_delta_per_second"] == 1.0


def test_dr_evidence_rejects_mismatched_restore_counts() -> None:
    validation = _load_script("validate_dr_evidence.py")
    source_counts = {table: 1 for table in validation.REQUIRED_TABLES}
    restored_counts = {table: 1 for table in validation.REQUIRED_TABLES}
    evidence = {
        "drill_id": "dev-2026-08-12",
        "environment": "dev",
        "result": "PASSED",
        "backup_timestamp": "2026-08-12T10:00:00Z",
        "started_at": "2026-08-12T10:30:00Z",
        "completed_at": "2026-08-12T10:45:00Z",
        "source_row_counts": source_counts,
        "restored_row_counts": restored_counts,
    }
    validation.validate_evidence(evidence, max_rpo_minutes=60, max_rto_minutes=60)
    restored_counts["agent_memory_events"] = 0

    with pytest.raises(ValueError, match="row counts"):
        validation.validate_evidence(evidence, max_rpo_minutes=60, max_rto_minutes=60)
