"""Shared FastAPI dependencies (auth bearer validation)."""

from __future__ import annotations

from typing import Annotated

from fastapi import Header

from gateway import auth_store
from gateway.errors import ErrorDetail, GatewayError


def parse_bearer(authorization: str | None) -> str | None:
    if not authorization:
        return None
    scheme, _, value = authorization.partition(" ")
    if scheme.lower() != "bearer" or not value:
        return None
    return value


def require_auth(
    authorization: Annotated[str | None, Header()] = None,
) -> auth_store.Session:
    """Require a valid Bearer access token (shared with auth routes)."""
    token = parse_bearer(authorization)
    session = auth_store.resolve_access(token)
    if session is None:
        raise GatewayError(
            401,
            code="unauthorized",
            message="Authentication is required",
            details=[ErrorDetail(field="authorization", reason="missing_or_invalid_token")],
        )
    return session
