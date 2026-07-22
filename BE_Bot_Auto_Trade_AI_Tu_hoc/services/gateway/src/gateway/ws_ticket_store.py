"""Short-lived Gateway WS tickets bound to auth sessions (paper)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from secrets import token_urlsafe
from typing import Any

WS_PATH = "/ws"
DEFAULT_TTL_SECONDS = 120

_tickets: dict[str, "WsTicket"] = {}


@dataclass
class WsTicket:
    ticket: str
    subject: str
    expires_at: datetime
    consumed: bool = False


def clear() -> None:
    _tickets.clear()


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def issue(*, subject: str, ttl_seconds: int = DEFAULT_TTL_SECONDS) -> dict[str, Any]:
    ticket = token_urlsafe(24)
    expires = _utcnow() + timedelta(seconds=ttl_seconds)
    _tickets[ticket] = WsTicket(ticket=ticket, subject=subject, expires_at=expires)
    return {
        "ticket": ticket,
        "expires_at": expires.isoformat().replace("+00:00", "Z"),
        "ws_path": WS_PATH,
    }


def consume(ticket: str) -> WsTicket | None:
    """Validate and consume ticket (single-use)."""
    row = _tickets.get(ticket)
    if row is None:
        return None
    if row.consumed:
        return None
    if row.expires_at < _utcnow():
        _tickets.pop(ticket, None)
        return None
    row.consumed = True
    return row
