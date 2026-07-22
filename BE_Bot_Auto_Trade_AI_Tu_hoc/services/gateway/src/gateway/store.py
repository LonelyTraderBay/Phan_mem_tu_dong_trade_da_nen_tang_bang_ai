"""In-memory paper-stub state for Phase 1 gateway."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4


PAPER_EMAIL = "operator@paper.local"
PAPER_PASSWORD = "PaperStub!123"
PAPER_USER_ID = UUID("00000000-0000-4000-8000-000000000001")
ACCESS_TOKEN_TTL_SECONDS = 3600


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_now() -> str:
    return utc_now().isoformat().replace("+00:00", "Z")


@dataclass
class SessionTokens:
    access_token: str
    refresh_token: str
    user_id: UUID


@dataclass
class PaperStore:
    """Process-local stub vault / ledgers — not for production."""

    # refresh_token -> SessionTokens
    refresh_sessions: dict[str, SessionTokens] = field(default_factory=dict)
    # access_token -> user_id
    access_sessions: dict[str, UUID] = field(default_factory=dict)

    accounts: dict[str, dict[str, Any]] = field(default_factory=dict)
    # account_id -> list of masked key records (secrets never stored in response shape)
    api_keys: dict[str, list[dict[str, Any]]] = field(default_factory=dict)
    strategies: dict[str, dict[str, Any]] = field(default_factory=dict)

    kill_switch_engaged: bool = False
    kill_switch_reason: str | None = None
    kill_switch_updated_at: str = field(default_factory=iso_now)
    kill_switch_updated_by: str | None = None
    kill_switch_audit: list[dict[str, Any]] = field(default_factory=list)

    # Fail-closed hook flag (P1-BE-08). Default available for paper happy-path.
    risk_available: bool = True

    alerts: list[dict[str, Any]] = field(default_factory=list)

    def reset(self) -> None:
        self.refresh_sessions.clear()
        self.access_sessions.clear()
        self.accounts.clear()
        self.api_keys.clear()
        self.strategies.clear()
        self.kill_switch_engaged = False
        self.kill_switch_reason = None
        self.kill_switch_updated_at = iso_now()
        self.kill_switch_updated_by = None
        self.kill_switch_audit.clear()
        self.risk_available = True
        self.alerts = [
            {
                "id": str(uuid4()),
                "severity": "info",
                "code": "PAPER_STUB_READY",
                "message": "Paper stub gateway is ready",
                "acknowledged": False,
                "created_at": iso_now(),
                "account_id": None,
                "acknowledged_at": None,
            }
        ]


store = PaperStore()
store.reset()
