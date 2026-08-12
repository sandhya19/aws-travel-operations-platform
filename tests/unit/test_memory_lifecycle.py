"""Contracts for scheduled memory-retention expiry."""

from travel_operations import memory_lifecycle


class FakeSession:
    def __enter__(self) -> "FakeSession":
        return self

    def __exit__(self, *_: object) -> None:
        return None


class FakeRepository:
    def expire_due_agent_sessions(self, _: object) -> list[object]:
        return [object(), object()]


class FakeSessionFactory:
    @staticmethod
    def begin() -> FakeSession:
        return FakeSession()


def test_lifecycle_handler_reports_expired_terminal_sessions(monkeypatch: object) -> None:
    monkeypatch.setattr(memory_lifecycle, "SessionFactory", FakeSessionFactory)  # type: ignore[union-attr]
    monkeypatch.setattr(memory_lifecycle, "TravelRequestRepository", lambda _: FakeRepository())  # type: ignore[union-attr]

    assert memory_lifecycle.handler({}, object()) == {"expired": 2}
