"""Paper stubs: postAccounts / postAccountApiKeys (masked credentials only)."""

from __future__ import annotations

from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from gateway import account_store, auth_store
from gateway.deps import require_auth
from gateway.errors import ErrorDetail, error_response

router = APIRouter(prefix="/accounts", tags=["Accounts"])


class AccountCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    exchange: str = Field(min_length=1)
    market_type: Literal["spot", "futures"]
    testnet: bool = True


class Account(BaseModel):
    id: str
    name: str
    exchange: str
    market_type: Literal["spot", "futures"]
    testnet: bool
    status: Literal["active", "disabled", "error"]
    created_at: str
    updated_at: str | None = None


class ApiKeyCreate(BaseModel):
    label: str = Field(min_length=1, max_length=100)
    api_key: str = Field(min_length=1)
    api_secret: str = Field(min_length=1)
    passphrase: str | None = Field(default=None, min_length=1)


class ApiKeyMasked(BaseModel):
    id: str
    account_id: str
    label: str
    masked_api_key: str
    created_at: str
    last_validated_at: str | None = None


@router.post("", status_code=201, response_model=Account)
def create_account(
    body: AccountCreate,
    _session: Annotated[auth_store.Session, Depends(require_auth)],
):
    # Never log request body secrets (none on this path).
    created = account_store.create_account(
        name=body.name,
        exchange=body.exchange,
        market_type=body.market_type,
        testnet=body.testnet,
    )
    return Account(**created)


@router.post("/{account_id}/api-keys", status_code=201, response_model=ApiKeyMasked)
def register_api_key(
    account_id: UUID,
    body: ApiKeyCreate,
    _session: Annotated[auth_store.Session, Depends(require_auth)],
):
    # Never log api_key / api_secret / passphrase.
    result = account_store.register_api_key(
        account_id=str(account_id),
        label=body.label,
        api_key=body.api_key,
        api_secret=body.api_secret,
        passphrase=body.passphrase,
    )
    if result is None:
        return error_response(
            404,
            code="not_found",
            message="Account not found",
            details=[ErrorDetail(field="account_id", reason="unknown_account")],
        )
    return ApiKeyMasked(**result)
