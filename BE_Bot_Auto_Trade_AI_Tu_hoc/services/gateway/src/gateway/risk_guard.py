"""Fail-closed entry guard when risk is unavailable (P1-BE-08 / Constitution II).

Paper stub: no live risk RPC. When the unavailable flag is set, reject new
entries — never fail-open. Callers MUST check before activating a strategy
(or any future stub entry path).
"""

from __future__ import annotations

from gateway.errors import ErrorDetail, GatewayError

# Default True so paper stubs work; tests flip this to simulate risk down.
_risk_available: bool = True


def clear() -> None:
    """Reset to available (tests)."""
    global _risk_available
    _risk_available = True


def set_risk_available(available: bool) -> None:
    """Test/ops hook: mark risk dependency up or down."""
    global _risk_available
    _risk_available = available


def is_risk_available() -> bool:
    return _risk_available


def ensure_entry_allowed() -> None:
    """Allow entry only when risk is available; otherwise reject (fail-closed)."""
    if _risk_available:
        return
    raise GatewayError(
        503,
        code="risk_unavailable",
        message="Risk dependency unavailable; new entries rejected (fail-closed)",
        details=[ErrorDetail(field="risk", reason="unavailable")],
    )
