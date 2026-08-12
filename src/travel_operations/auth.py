"""JWT authentication dependencies."""

import os
from dataclasses import dataclass
from functools import lru_cache

import boto3
import jwt
from fastapi import Depends, HTTPException, Request, status


@dataclass(frozen=True)
class AuthenticatedUser:
    subject: str
    roles: frozenset[str]
    tenant_id: str = "default"


@lru_cache
def load_jwt_secret() -> str:
    """Resolve the local secret or Lambda runtime Secrets Manager reference."""
    if secret := os.getenv("JWT_SECRET"):
        return secret
    if secret_arn := os.getenv("JWT_SECRET_SECRET_ARN"):
        response = boto3.client("secretsmanager").get_secret_value(SecretId=secret_arn)
        return str(response["SecretString"])
    raise KeyError("JWT_SECRET")


def require_user(request: Request) -> AuthenticatedUser:
    authorization = request.headers.get("Authorization", "")
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Bearer token required"
        )
    try:
        claims = jwt.decode(
            authorization.removeprefix("Bearer "), load_jwt_secret(), algorithms=["HS256"]
        )
        roles = claims.get("roles", [])
        if not isinstance(roles, list) or not all(isinstance(role, str) for role in roles):
            raise KeyError("roles")
        tenant_id = claims.get("tenant_id", "default")
        if not isinstance(tenant_id, str) or not tenant_id:
            raise KeyError("tenant_id")
        return AuthenticatedUser(
            subject=str(claims["sub"]), roles=frozenset(roles), tenant_id=tenant_id
        )
    except (KeyError, jwt.InvalidTokenError) as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token"
        ) from error


def require_approver(
    user: AuthenticatedUser = Depends(require_user),  # noqa: B008
) -> AuthenticatedUser:
    """Require the explicit role permitted to resolve human approvals."""
    if "travel:approve" not in user.roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Approver role required")
    return user
