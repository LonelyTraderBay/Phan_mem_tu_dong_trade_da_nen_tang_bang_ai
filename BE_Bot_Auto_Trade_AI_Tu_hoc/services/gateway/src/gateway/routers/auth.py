"""Paper-dev auth stubs: postAuthLogin / postAuthRefresh / postAuthLogout."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Header
from pydantic import BaseModel, Field

from gateway import auth_store
from gateway.deps import parse_bearer
from gateway.errors import ErrorDetail, error_response

router = APIRouter(prefix="/auth", tags=["Auth"])


class LoginRequest(BaseModel):
    email: str
    password: str = Field(min_length=8)


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(min_length=1)


class LogoutRequest(BaseModel):
    refresh_token: str | None = Field(default=None, min_length=1)


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int


class ActionResult(BaseModel):
    success: bool


@router.post("/login")
def login(body: LoginRequest):
    # Never log password or raw tokens.
    if not auth_store.credentials_ok(body.email, body.password):
        return error_response(
            401,
            code="unauthorized",
            message="Invalid email or password",
            details=[ErrorDetail(field="credentials", reason="authentication_failed")],
        )
    return TokenPair(**auth_store.issue_pair(body.email))


@router.post("/refresh")
def refresh(body: RefreshTokenRequest):
    pair = auth_store.refresh_pair(body.refresh_token)
    if pair is None:
        return error_response(
            401,
            code="unauthorized",
            message="Invalid or expired refresh token",
            details=[ErrorDetail(field="refresh_token", reason="invalid_token")],
        )
    return TokenPair(**pair)


@router.post("/logout")
def logout(
    body: LogoutRequest | None = None,
    authorization: Annotated[str | None, Header()] = None,
):
    access = parse_bearer(authorization)
    refresh_token = body.refresh_token if body else None
    if not access and not refresh_token:
        return error_response(
            401,
            code="unauthorized",
            message="Authentication is required",
            details=[ErrorDetail(field="authorization", reason="missing_credentials")],
        )
    revoked = auth_store.revoke(access_token=access, refresh_token=refresh_token)
    if not revoked:
        return error_response(
            401,
            code="unauthorized",
            message="Invalid or expired session",
            details=[ErrorDetail(field="session", reason="invalid_token")],
        )
    return ActionResult(success=True)
