"""Accounts + masked API keys paper stubs."""

from __future__ import annotations

from typing import Literal
from uuid import uuid4

from fastapi import APIRouter
from pydantic import BaseModel, Field

from gateway.auth_deps import BearerUser
from gateway.errors import error_response
from gateway.store import iso_now, store

router = APIRouter(prefix="/v1", tags=["Accounts"])


class AccountCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    exchange: str = Field(min_length=1)
    market_type: Literal["spot", "futures"]
    testnet: bool = True


class ApiKeyCreate(BaseModel):
    label: str = Field(min_length=1, max_length=100)
    api_key: str = Field(min_length=1)
    api_secret: str = Field(min_length=1)
    passphrase: str | None = Field(default=None, min_length=1)


def mask_api_key(api_key: str) -> str:
    """Return masked key showing only last 4 characters."""
    last4 = api_key[-4:] if len(api_key) >= 4 else api_key
    return f"****{last4}"


@router.post("/accounts", status_code=201, operation_id="postAccounts")
def post_accounts(_user: BearerUser, body: AccountCreate) -> dict:
    now = iso_now()
    account_id = str(uuid4())
    account = {
        "id": account_id,
        "name": body.name,
        "exchange": body.exchange,
        "market_type": body.market_type,
        "testnet": body.testnet,
        "status": "active",
        "created_at": now,
        "updated_at": now,
    }
    store.accounts[account_id] = account
    store.api_keys.setdefault(account_id, [])
    return account


@router.post(
    "/accounts/{account_id}/api-keys",
    status_code=201,
    operation_id="postAccountApiKeys",
)
def post_account_api_keys(
    account_id: str,
    _user: BearerUser,
    body: ApiKeyCreate,
):
    if account_id not in store.accounts:
        return error_response(
            404,
            "NOT_FOUND",
            "Account not found",
            details=[{"field": "account_id", "reason": "unknown"}],
        )
    # Never put full api_key/secret in response or logs.
    key_id = str(uuid4())
    record = {
        "id": key_id,
        "account_id": account_id,
        "label": body.label,
        "masked_api_key": mask_api_key(body.api_key),
        "created_at": iso_now(),
        "last_validated_at": None,
    }
    store.api_keys.setdefault(account_id, []).append(record)
    return record
