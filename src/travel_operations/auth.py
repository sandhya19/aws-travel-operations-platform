"""JWT authentication dependencies."""
import os
from dataclasses import dataclass

import jwt
from fastapi import HTTPException, Request, status


@dataclass(frozen=True)
class AuthenticatedUser:
    subject: str


def require_user(request: Request) -> AuthenticatedUser:
    authorization = request.headers.get("Authorization", "")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bearer token required")
    try:
        claims = jwt.decode(authorization.removeprefix("Bearer "), os.environ["JWT_SECRET"], algorithms=["HS256"])
        return AuthenticatedUser(subject=str(claims["sub"]))
    except (KeyError, jwt.InvalidTokenError) as error:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token") from error
