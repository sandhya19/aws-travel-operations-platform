"""Authorization tests for travel-request actions."""

import pytest
from fastapi import HTTPException

from travel_operations.auth import AuthenticatedUser, require_approver


def test_approver_role_is_required() -> None:
    with pytest.raises(HTTPException, match="Approver role required") as error:
        require_approver(AuthenticatedUser(subject="employee", roles=frozenset()))

    assert error.value.status_code == 403


def test_approver_role_is_accepted() -> None:
    approver = AuthenticatedUser(subject="travel.manager", roles=frozenset({"travel:approve"}))

    assert require_approver(approver) == approver
