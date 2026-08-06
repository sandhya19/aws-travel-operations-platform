"""JWT authentication dependencies."""

import os
from dataclasses import dataclass

import jwt
from fastapi import Depends, HTTPException, Request, status


@dataclass(frozen=True)
class AuthenticatedUser:
    subject: str
    roles: frozenset[str]


def require_user(request: Request) -> AuthenticatedUser:
    authorization = request.headers.get("Authorization", "")
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Bearer token required"
        )
    try:
        claims = jwt.decode(
            authorization.removeprefix("Bearer "), os.environ["JWT_SECRET"], algorithms=["HS256"]
        )
        roles = claims.get("roles", [])
        if not isinstance(roles, list) or not all(isinstance(role, str) for role in roles):
            raise KeyError("roles")
        return AuthenticatedUser(subject=str(claims["sub"]), roles=frozenset(roles))
    except (KeyError, jwt.InvalidTokenError) as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token"
        ) from error


def require_approver(user: AuthenticatedUser = Depends(require_user)) -> AuthenticatedUser:
    """Require the explicit role permitted to resolve human approvals."""
    if "travel:approve" not in user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Approver role required")
    return user
