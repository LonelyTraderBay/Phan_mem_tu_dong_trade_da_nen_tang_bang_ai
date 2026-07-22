"""In-memory paper-dev token store. Not for production."""

from __future__ import annotations

import os
import secrets
from dataclasses import dataclass

ACCESS_TOKEN_TTL_SECONDS = 3600

# Local-only defaults — override via env; never commit real secrets.
PAPER_AUTH_EMAIL = os.getenv("PAPER_AUTH_EMAIL", "operator@example.com")
PAPER_AUTH_PASSWORD = os.getenv("PAPER_AUTH_PASSWORD", "paper-dev-password")


@dataclass
class Session:
    email: str
    access_token: str
    refresh_token: str


_by_refresh: dict[str, Session] = {}
_by_access: dict[str, Session] = {}


def clear() -> None:
    """Reset store (tests)."""
    _by_refresh.clear()
    _by_access.clear()


def credentials_ok(email: str, password: str) -> bool:
    return email == PAPER_AUTH_EMAIL and password == PAPER_AUTH_PASSWORD


def issue_pair(email: str) -> dict[str, object]:
    access = f"access_{secrets.token_urlsafe(24)}"
    refresh = f"refresh_{secrets.token_urlsafe(24)}"
    session = Session(email=email, access_token=access, refresh_token=refresh)
    _by_refresh[refresh] = session
    _by_access[access] = session
    return {
        "access_token": access,
        "refresh_token": refresh,
        "token_type": "Bearer",
        "expires_in": ACCESS_TOKEN_TTL_SECONDS,
    }


def refresh_pair(refresh_token: str) -> dict[str, object] | None:
    session = _by_refresh.pop(refresh_token, None)
    if session is None:
        return None
    _by_access.pop(session.access_token, None)
    return issue_pair(session.email)


def revoke(*, access_token: str | None = None, refresh_token: str | None = None) -> bool:
    session: Session | None = None
    if refresh_token:
        session = _by_refresh.pop(refresh_token, None)
        if session is not None:
            _by_access.pop(session.access_token, None)
            return True
    if access_token:
        session = _by_access.pop(access_token, None)
        if session is not None:
            _by_refresh.pop(session.refresh_token, None)
            return True
    return False
