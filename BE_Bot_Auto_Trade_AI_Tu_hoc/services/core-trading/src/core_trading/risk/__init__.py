"""Risk Management: last line of defense — limits, kill-switch, and calendar/margin/fee checks before any order leaves the system."""

from core_trading.risk.fail_closed import (
    RiskUnavailableError,
    assert_entries_allowed,
)

__all__ = [
    "RiskUnavailableError",
    "assert_entries_allowed",
]
