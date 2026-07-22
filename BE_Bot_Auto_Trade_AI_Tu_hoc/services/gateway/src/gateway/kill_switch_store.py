"""In-memory L1 kill-switch state + optional audit list (paper stub; no L4)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

_state: dict[str, Any] = {
    "engaged": False,
    "reason": None,
    "updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "updated_by": None,
}
_audit: list[dict[str, Any]] = []


def clear() -> None:
    """Reset store (tests)."""
    _state.clear()
    _state.update(
        {
            "engaged": False,
            "reason": None,
            "updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "updated_by": None,
        }
    )
    _audit.clear()


def get_status() -> dict[str, Any]:
    return dict(_state)


def set_engaged(
    *,
    engaged: bool,
    reason: str,
    updated_by: str | None = None,
) -> dict[str, Any]:
    """L1 engage/disengage only — no flatten / L4."""
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    _state["engaged"] = engaged
    _state["reason"] = reason
    _state["updated_at"] = now
    _state["updated_by"] = updated_by
    _audit.append(
        {
            "engaged": engaged,
            "reason": reason,
            "updated_at": now,
            "updated_by": updated_by,
        }
    )
    return dict(_state)


def list_audit() -> list[dict[str, Any]]:
    """Optional in-memory audit trail for stub inspection/tests."""
    return [dict(row) for row in _audit]
