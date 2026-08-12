"""Run a bounded concurrent benchmark of the deployed dev approval workflow."""

import argparse
import json
import os
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from scripts.run_dev_workflow_demo import run_workflow_demo


def percentile(values: list[float], percent: int) -> float:
    """Return the nearest-rank percentile for a non-empty list of durations."""
    if not values:
        raise ValueError("Cannot calculate a percentile without successful samples")
    rank = max(0, (len(values) * percent + 99) // 100 - 1)
    return sorted(values)[rank]


def run_benchmark(
    run_once: Callable[[], dict[str, str]],
    requests: int,
    concurrency: int,
    clock: Callable[[], float] = time.perf_counter,
) -> dict[str, Any]:
    """Run bounded concurrent workflow samples without retaining request payloads or tokens."""
    if requests < 1:
        raise ValueError("requests must be at least one")
    if concurrency < 1 or concurrency > requests:
        raise ValueError("concurrency must be between one and requests")

    durations: list[float] = []
    failures: dict[str, int] = {}
    started = clock()

    def timed_run() -> float:
        sample_started = clock()
        result = run_once()
        if result.get("status") != "COMPLETED":
            raise RuntimeError("Workflow sample did not complete")
        return clock() - sample_started

    with ThreadPoolExecutor(max_workers=concurrency) as executor:
        futures = [executor.submit(timed_run) for _ in range(requests)]
        for future in as_completed(futures):
            try:
                durations.append(future.result())
            except Exception as error:  # noqa: BLE001 - benchmark must report every failed sample.
                name = type(error).__name__
                failures[name] = failures.get(name, 0) + 1

    elapsed = clock() - started
    successful = len(durations)
    return {
        "requests": requests,
        "concurrency": concurrency,
        "successful_requests": successful,
        "failed_requests": requests - successful,
        "success_rate": successful / requests,
        "elapsed_seconds": round(elapsed, 3),
        "requests_per_second": round(successful / elapsed, 3) if elapsed > 0 else 0.0,
        "latency_ms": (
            {
                "p50": round(percentile(durations, 50) * 1000, 3),
                "p95": round(percentile(durations, 95) * 1000, 3),
                "max": round(max(durations) * 1000, 3),
            }
            if durations
            else None
        ),
        "failure_types": failures,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-url", required=True)
    parser.add_argument("--label", required=True, help="For example baseline or assisted.")
    parser.add_argument("--requests", type=int, default=5)
    parser.add_argument("--concurrency", type=int, default=1)
    parser.add_argument("--timeout-seconds", type=int, default=120)
    arguments = parser.parse_args()
    secret = os.environ["JWT_SECRET"]
    result = run_benchmark(
        lambda: run_workflow_demo(arguments.api_url, arguments.timeout_seconds, secret),
        arguments.requests,
        arguments.concurrency,
    )
    result["label"] = arguments.label
    print(json.dumps(result, sort_keys=True))
    if result["failed_requests"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
