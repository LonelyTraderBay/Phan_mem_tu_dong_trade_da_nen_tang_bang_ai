"""In-memory paper stub for accounts + broker credentials. Not for production.

Secrets are stored server-side only and must never be logged or returned.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def mask_api_key(api_key: str) -> str:
    """Return a masked form only — never the full key."""
    if len(api_key) >= 4:
        return f"****{api_key[-4:]}"
    return "****MASKED"


@dataclass
class StoredCredential:
    id: str
    account_id: str
    label: str
    api_key: str  # server-side only
    api_secret: str  # server-side only
    passphrase: str | None  # server-side only
    created_at: str
    last_validated_at: str | None = None


@dataclass
class StoredAccount:
    id: str
    name: str
    exchange: str
    market_type: str
    testnet: bool
    status: str
    created_at: str
    updated_at: str | None = None
    credentials: list[StoredCredential] = field(default_factory=list)


_accounts: dict[str, StoredAccount] = {}


def clear() -> None:
    """Reset store (tests)."""
    _accounts.clear()


def create_account(
    *,
    name: str,
    exchange: str,
    market_type: str,
    testnet: bool = True,
) -> dict[str, object]:
    now = _utcnow_iso()
    account_id = str(uuid4())
    account = StoredAccount(
        id=account_id,
        name=name,
        exchange=exchange,
        market_type=market_type,
        testnet=testnet,
        status="active",
        created_at=now,
        updated_at=now,
    )
    _accounts[account_id] = account
    return {
        "id": account.id,
        "name": account.name,
        "exchange": account.exchange,
        "market_type": account.market_type,
        "testnet": account.testnet,
        "status": account.status,
        "created_at": account.created_at,
        "updated_at": account.updated_at,
    }


def get_account(account_id: str) -> StoredAccount | None:
    return _accounts.get(account_id)


def register_api_key(
    *,
    account_id: str,
    label: str,
    api_key: str,
    api_secret: str,
    passphrase: str | None = None,
) -> dict[str, object] | None:
    account = _accounts.get(account_id)
    if account is None:
        return None
    now = _utcnow_iso()
    cred = StoredCredential(
        id=str(uuid4()),
        account_id=account_id,
        label=label,
        api_key=api_key,
        api_secret=api_secret,
        passphrase=passphrase,
        created_at=now,
        last_validated_at=None,
    )
    account.credentials.append(cred)
    account.updated_at = now
    # Response: ApiKeyMasked only — never full secrets.
    return {
        "id": cred.id,
        "account_id": cred.account_id,
        "label": cred.label,
        "masked_api_key": mask_api_key(api_key),
        "created_at": cred.created_at,
        "last_validated_at": cred.last_validated_at,
    }
