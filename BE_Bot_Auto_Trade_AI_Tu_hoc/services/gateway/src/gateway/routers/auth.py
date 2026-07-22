"""Auth paper stubs: login / refresh / logout."""

from __future__ import annotations

from secrets import token_urlsafe

from fastapi import APIRouter
from pydantic import BaseModel, Field

from gateway.auth_deps import BearerUser
from gateway.errors import error_response
from gateway.store import (
    ACCESS_TOKEN_TTL_SECONDS,
    PAPER_EMAIL,
    PAPER_PASSWORD,
    PAPER_USER_ID,
    SessionTokens,
    store,
)

router = APIRouter(prefix="/v1/auth", tags=["Auth"])


class LoginRequest(BaseModel):
    email: str = Field(min_length=3)
    password: str = Field(min_length=8)


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(min_length=1)


class LogoutRequest(BaseModel):
    refresh_token: str | None = Field(default=None, min_length=1)


def _issue_tokens(user_id=PAPER_USER_ID) -> dict:
    access = token_urlsafe(32)
    refresh = token_urlsafe(32)
    session = SessionTokens(
        access_token=access,
        refresh_token=refresh,
        user_id=user_id,
    )
    store.access_sessions[access] = user_id
    store.refresh_sessions[refresh] = session
    return {
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "Bearer",
        "expires_in": ACCESS_TOKEN_TTL_SECONDS,
    }


@router.post("/login", operation_id="postAuthLogin")
def post_auth_login(body: LoginRequest):
    # Never log password / tokens.
    if body.email.lower() != PAPER_EMAIL or body.password != PAPER_PASSWORD:
        return error_response(
            401,
            "UNAUTHORIZED",
            "Invalid email or password",
        )
    return _issue_tokens()


@router.post("/refresh", operation_id="postAuthRefresh")
def post_auth_refresh(body: RefreshTokenRequest):
    session = store.refresh_sessions.pop(body.refresh_token, None)
    if session is None:
        return error_response(
            401,
            "UNAUTHORIZED",
            "Invalid refresh token",
        )
    # Invalidate previous access token for this session.
    store.access_sessions.pop(session.access_token, None)
    return _issue_tokens(user_id=session.user_id)


@router.post("/logout", operation_id="postAuthLogout")
def post_auth_logout(
    _user: BearerUser,
    body: LogoutRequest | None = None,
):
    if body and body.refresh_token:
        session = store.refresh_sessions.pop(body.refresh_token, None)
        if session is not None:
            store.access_sessions.pop(session.access_token, None)
    return {"success": True}
