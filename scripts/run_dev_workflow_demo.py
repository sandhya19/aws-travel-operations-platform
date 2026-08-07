"""Exercise the deployed dev request, approval, and completion workflow."""

import argparse
import json
import os
import time
from datetime import UTC, datetime, timedelta
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import jwt


def make_token(subject: str, roles: list[str], secret: str) -> str:
    """Create a short-lived token accepted by the dev API."""
    return jwt.encode(
        {"sub": subject, "roles": roles, "exp": datetime.now(UTC) + timedelta(minutes=10)},
        secret,
        algorithm="HS256",
    )


def request_json(
    url: str, token: str, method: str, body: dict[str, Any] | None = None
) -> tuple[int, dict[str, Any]]:
    """Call the API without logging the bearer token or response headers."""
    payload = json.dumps(body).encode() if body is not None else None
    request = Request(
        url,
        data=payload,
        method=method,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    try:
        with urlopen(request, timeout=15) as response:  # noqa: S310
            return response.status, json.loads(response.read())
    except HTTPError as error:
        return error.code, json.loads(error.read())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-url", required=True)
    parser.add_argument("--timeout-seconds", type=int, default=120)
    arguments = parser.parse_args()
    secret = os.environ["JWT_SECRET"]
    employee_token = make_token("demo.employee", [], secret)
    approver_token = make_token("demo.approver", ["travel:approve"], secret)
    status, created = request_json(
        f"{arguments.api_url.rstrip('/')}/travel-request",
        employee_token,
        "POST",
        {
            "destination_country": "GB",
            "departure_date": "2026-10-01",
            "return_date": "2026-10-03",
            "purpose": "Hackathon workflow demonstration",
        },
    )
    if status != 201:
        raise RuntimeError(f"Request creation failed with HTTP {status}: {created}")
    request_id = str(created["id"])
    deadline = time.monotonic() + arguments.timeout_seconds
    approval_url = f"{arguments.api_url.rstrip('/')}/travel-request/{request_id}/approval"
    while time.monotonic() < deadline:
        status, _ = request_json(approval_url, approver_token, "POST")
        if status == 202:
            break
        if status != 404:
            raise RuntimeError(f"Approval failed with HTTP {status}")
        time.sleep(2)
    else:
        raise TimeoutError("Workflow did not create an approval task before the deadline")
    request_url = f"{arguments.api_url.rstrip('/')}/travel-request/{request_id}"
    while time.monotonic() < deadline:
        status, result = request_json(request_url, employee_token, "GET")
        if status == 200 and result["status"] == "COMPLETED":
            print(json.dumps({"request_id": request_id, "status": "COMPLETED"}))
            return
        if status != 200:
            raise RuntimeError(f"Request lookup failed with HTTP {status}")
        time.sleep(2)
    raise TimeoutError("Workflow did not reach COMPLETED before the deadline")


if __name__ == "__main__":
    main()
