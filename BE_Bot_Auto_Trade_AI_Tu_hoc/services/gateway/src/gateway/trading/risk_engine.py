"""Paper risk engine — fail-closed allow/deny with persisted RiskCheck + trace_id."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from gateway import alerts_store, kill_switch_store, risk_guard
from gateway.trading import ledger


@dataclass(frozen=True)
class RiskDecision:
    allowed: bool
    risk_check_id: str
    trace_id: str
    reason_code: str
    message: str


def evaluate_entry(
    *,
    account_id: str,
    strategy_id: str | None = None,
    symbol: str | None = None,
    side: str | None = None,
    quantity: float | None = None,
    trace_id: str | None = None,
) -> RiskDecision:
    """Allow only when risk is available and L1 kill-switch is disengaged.

    Always persists a RiskCheck on the ledger. Emits RISK_REJECTED alert on deny.
    Unused signal fields are accepted for call-site clarity / future checks.
    """
    _ = (symbol, side, quantity)
    tid = trace_id or str(uuid4())

    if not risk_guard.is_risk_available():
        check = ledger.record_risk_check(
            decision="deny",
            reason_code="risk_unavailable",
            trace_id=tid,
            account_id=account_id,
            strategy_id=strategy_id,
        )
        _alert_risk_rejected(account_id, "Risk dependency unavailable; entry denied")
        return RiskDecision(
            allowed=False,
            risk_check_id=check["risk_check_id"],
            trace_id=tid,
            reason_code="risk_unavailable",
            message="Risk dependency unavailable; new entries rejected (fail-closed)",
        )

    ks = kill_switch_store.get_status()
    if ks.get("engaged"):
        check = ledger.record_risk_check(
            decision="deny",
            reason_code="kill_switch_engaged",
            trace_id=tid,
            account_id=account_id,
            strategy_id=strategy_id,
        )
        _alert_risk_rejected(account_id, "Kill-switch L1 engaged; entry denied")
        return RiskDecision(
            allowed=False,
            risk_check_id=check["risk_check_id"],
            trace_id=tid,
            reason_code="kill_switch_engaged",
            message="Kill-switch engaged; new entries rejected",
        )

    check = ledger.record_risk_check(
        decision="allow",
        reason_code="ok",
        trace_id=tid,
        account_id=account_id,
        strategy_id=strategy_id,
    )
    return RiskDecision(
        allowed=True,
        risk_check_id=check["risk_check_id"],
        trace_id=tid,
        reason_code="ok",
        message="Entry allowed",
    )


def _alert_risk_rejected(account_id: str, message: str) -> None:
    # Never include secrets in alert messages.
    alerts_store.seed_alert(
        account_id=account_id,
        severity="warning",
        code="RISK_REJECTED",
        message=message,
    )
