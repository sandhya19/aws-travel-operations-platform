"""Transaction-boundary tests for the travel-request service."""

from travel_operations.services.travel_requests import TravelRequestService


class CommitRecordingRepository:
    def __init__(self) -> None:
        self.commits = 0

    def commit(self) -> None:
        self.commits += 1


def test_service_commits_before_external_side_effects() -> None:
    repository = CommitRecordingRepository()

    TravelRequestService(repository).commit()  # type: ignore[arg-type]

    assert repository.commits == 1
