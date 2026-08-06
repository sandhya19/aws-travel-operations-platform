"""Transaction lifecycle tests."""

import pytest

import travel_operations.database as database


class FakeSession:
    def __init__(self) -> None:
        self.committed = self.rolled_back = self.closed = False

    def commit(self) -> None:
        self.committed = True

    def rollback(self) -> None:
        self.rolled_back = True

    def close(self) -> None:
        self.closed = True


def test_session_scope_commits_and_closes(monkeypatch: pytest.MonkeyPatch) -> None:
    session = FakeSession()
    monkeypatch.setattr(database, "SessionFactory", lambda: session)
    scope = database.session_scope()
    next(scope)
    with pytest.raises(StopIteration):
        next(scope)
    assert session.committed and session.closed and not session.rolled_back


def test_session_scope_rolls_back_and_closes(monkeypatch: pytest.MonkeyPatch) -> None:
    session = FakeSession()
    monkeypatch.setattr(database, "SessionFactory", lambda: session)
    scope = database.session_scope()
    next(scope)
    with pytest.raises(RuntimeError):
        scope.throw(RuntimeError("write failed"))
    assert session.rolled_back and session.closed and not session.committed
