"""Compare baseline and assisted workflow benchmark JSON results."""

import argparse
import json
from pathlib import Path
from typing import Any, cast


def load_benchmark(path: Path) -> dict[str, Any]:
    """Load one successful benchmark result and reject incomplete evidence."""
    result = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(result, dict):
        raise ValueError(f"{path} is not a benchmark object")
    required = {"label", "success_rate", "requests_per_second", "latency_ms"}
    if not required.issubset(result) or result["latency_ms"] is None:
        raise ValueError(f"{path} is not a complete benchmark result")
    if result["success_rate"] != 1:
        raise ValueError(f"{path} contains failed workflow samples")
    return cast(dict[str, Any], result)


def compare(baseline: dict[str, Any], assisted: dict[str, Any]) -> dict[str, Any]:
    """Calculate explicit deltas without treating a slower assisted flow as a success."""
    baseline_p95 = float(baseline["latency_ms"]["p95"])
    assisted_p95 = float(assisted["latency_ms"]["p95"])
    baseline_rps = float(baseline["requests_per_second"])
    assisted_rps = float(assisted["requests_per_second"])
    return {
        "baseline_label": baseline["label"],
        "assisted_label": assisted["label"],
        "baseline_p95_ms": baseline_p95,
        "assisted_p95_ms": assisted_p95,
        "p95_delta_ms": round(assisted_p95 - baseline_p95, 3),
        "baseline_requests_per_second": baseline_rps,
        "assisted_requests_per_second": assisted_rps,
        "throughput_delta_per_second": round(assisted_rps - baseline_rps, 3),
        "both_runs_completed": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", required=True, type=Path)
    parser.add_argument("--assisted", required=True, type=Path)
    arguments = parser.parse_args()
    comparison = compare(load_benchmark(arguments.baseline), load_benchmark(arguments.assisted))
    print(json.dumps(comparison))


if __name__ == "__main__":
    main()
