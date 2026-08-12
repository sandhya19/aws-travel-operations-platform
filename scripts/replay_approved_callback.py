"""Resume one approval workflow after its approved callback was not delivered."""

import argparse
from uuid import UUID

import boto3

from travel_operations.database import SessionFactory
from travel_operations.repositories.travel_requests import TravelRequestRepository
from travel_operations.services.travel_requests import TravelRequestService


def replay(request_id: UUID) -> None:
    """Send the success callback only when the durable checkpoint permits it."""
    with SessionFactory() as session:
        token = TravelRequestService(
            TravelRequestRepository(session)
        ).approved_callback_token_for_replay(request_id)
    boto3.client("stepfunctions").send_task_success(
        taskToken=token, output='{"approved":true,"replayed":true}'
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request_id", type=UUID)
    request_id = parser.parse_args().request_id
    replay(request_id)
    print(f"Replayed approved callback for travel request {request_id}")


if __name__ == "__main__":
    main()
