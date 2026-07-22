"""Unit tests for fail-closed risk entry guard."""

from __future__ import annotations

import pytest

from core_trading.risk import RiskUnavailableError, assert_entries_allowed


def test_fail_closed_rejects_when_risk_unavailable() -> None:
    with pytest.raises(RiskUnavailableError) as exc_info:
        assert_entries_allowed(risk_available=False)
    assert exc_info.value.code == "RISK_UNAVAILABLE"


def test_fail_closed_allows_when_risk_available() -> None:
    assert_entries_allowed(risk_available=True)
