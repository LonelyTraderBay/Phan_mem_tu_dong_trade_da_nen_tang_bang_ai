"""Bearer access-token dependency for protected /v1 routes."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, Request
from fastapi.responses import JSONResponse

from gateway.errors import error_response
from gateway.store import store


class AuthError(Exception):
    def __init__(self, response: JSONResponse) -> None:
        self.response = response
        super().__init__("unauthorized")


def require_bearer(
    authorization: Annotated[str | None, Header()] = None,
) -> UUID:
    if not authorization or not authorization.startswith("Bearer "):
        raise AuthError(
            error_response(
                401,
                "UNAUTHORIZED",
                "Missing or invalid Bearer token",
            )
        )
    token = authorization.removeprefix("Bearer ").strip()
    user_id = store.access_sessions.get(token)
    if user_id is None:
        raise AuthError(
            error_response(
                401,
                "UNAUTHORIZED",
                "Invalid or expired access token",
            )
        )
    return user_id


async def auth_error_handler(_request: Request, exc: AuthError) -> JSONResponse:
    return exc.response


BearerUser = Annotated[UUID, Depends(require_bearer)]
