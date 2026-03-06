"""
Authentication dependency for FastAPI routes.

Extracts and validates JWT tokens from Authorization headers.
"""

from uuid import UUID

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError

from app.core.exceptions import AuthenticationError
from app.core.security import decode_token

security_scheme = HTTPBearer(auto_error=False)


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),
) -> UUID:
    """
    Extract authenticated user ID from JWT token.
    
    Usage:
        @router.get("/me")
        async def me(user_id: UUID = Depends(get_current_user_id)):
    """
    if not credentials:
        raise AuthenticationError("Missing authentication token")

    try:
        payload = decode_token(credentials.credentials)
    except JWTError:
        raise AuthenticationError("Invalid or expired token")

    if payload.get("type") != "access":
        raise AuthenticationError("Invalid token type")

    subject = payload.get("sub")
    if not subject:
        raise AuthenticationError("Invalid token payload")

    try:
        return UUID(subject)
    except ValueError:
        raise AuthenticationError("Invalid user ID in token")
