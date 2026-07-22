"""Fail-closed entry guard: reject new entries when risk is unavailable."""

from __future__ import annotations


class RiskUnavailableError(Exception):
    """Raised when risk cannot evaluate an entry — never fail-open."""

    code = "RISK_UNAVAILABLE"

    def __init__(self, message: str = "Risk service unavailable; new entries rejected") -> None:
        self.message = message
        super().__init__(message)


def assert_entries_allowed(*, risk_available: bool) -> None:
    """Allow new entries only when risk is available.

    Fail-closed: if risk is unavailable, raise RiskUnavailableError.
    Callers MUST treat this as a hard reject (never proceed to OMS).
    """
    if not risk_available:
        raise RiskUnavailableError()
