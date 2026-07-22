"""In-memory kill-switch state L1–L4 (paper/staging; L4 = internal flatten)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal
from uuid import uuid4

KillLevel = Literal["L1", "L2", "L3", "L4"]
_LEVEL_RANK = {"L1": 1, "L2": 2, "L3": 3, "L4": 4}

_state: dict[str, Any] = {
    "engaged": False,
    "level": None,
    "reason": None,
    "updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "updated_by": None,
    "trace_id": None,
}
_audit: list[dict[str, Any]] = []


def clear() -> None:
    """Reset store (tests)."""
    _state.clear()
    _state.update(
        {
            "engaged": False,
            "level": None,
            "reason": None,
            "updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "updated_by": None,
            "trace_id": None,
        }
    )
    _audit.clear()


def get_status() -> dict[str, Any]:
    return dict(_state)


def level_rank(level: str | None) -> int:
    if level is None:
        return 0
    return _LEVEL_RANK.get(level, 0)


def set_state(
    *,
    engaged: bool,
    reason: str,
    level: KillLevel | None = None,
    updated_by: str | None = None,
    trace_id: str | None = None,
) -> dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    tid = trace_id or str(uuid4())
    if not engaged:
        _state["engaged"] = False
        _state["level"] = None
    else:
        _state["engaged"] = True
        _state["level"] = level or "L1"
    _state["reason"] = reason
    _state["updated_at"] = now
    _state["updated_by"] = updated_by
    _state["trace_id"] = tid
    _audit.append(
        {
            "engaged": _state["engaged"],
            "level": _state["level"],
            "reason": reason,
            "updated_at": now,
            "updated_by": updated_by,
            "trace_id": tid,
        }
    )
    return dict(_state)


def set_engaged(
    *,
    engaged: bool,
    reason: str,
    updated_by: str | None = None,
) -> dict[str, Any]:
    """Backward-compatible L1 helper used by older tests/call sites."""
    return set_state(
        engaged=engaged,
        reason=reason,
        level="L1" if engaged else None,
        updated_by=updated_by,
    )


def list_audit() -> list[dict[str, Any]]:
    return [dict(row) for row in _audit]
