"""Baseline paper strategy runner — activate path: credentials → signal → risk → OMS."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from gateway import account_store
from gateway.errors import ErrorDetail
from gateway.strategy_store import StoredStrategy
from gateway.trading import oms, risk_engine
from gateway.trading.live_capital import LiveCapitalError, assert_live_entry_allowed
from gateway.trading.paper_adapter import VenueAdapterError

BASELINE_QTY = 0.001


@dataclass(frozen=True)
class ActivateResult:
    ok: bool
    status_code: int = 200
    code: str = "ok"
    message: str = ""
    details: tuple[ErrorDetail, ...] = ()
    trace_id: str = ""


def account_has_credential(account_id: str) -> bool:
    """Fail-closed credential presence check — never logs secret material."""
    account = account_store.get_account(account_id)
    if account is None:
        return False
    return len(account.credentials) >= 1


def run_on_activate(strategy: StoredStrategy) -> ActivateResult:
    """Emit one baseline paper buy when strategy becomes active."""
    trace_id = str(uuid4())
    account_id = strategy.account_id

    if not account_has_credential(account_id):
        return ActivateResult(
            ok=False,
            status_code=403,
            code="credentials_required",
            message="Account has no API credentials; paper entry denied (fail-closed)",
            details=(ErrorDetail(field="account_id", reason="no_credentials"),),
            trace_id=trace_id,
        )

    account = account_store.get_account(account_id)
    if account is not None and not account.testnet:
        try:
            assert_live_entry_allowed(
                testnet=False,
                exchange=account.exchange,
            )
        except LiveCapitalError as exc:
            return ActivateResult(
                ok=False,
                status_code=403,
                code=exc.code,
                message=exc.message,
                details=(ErrorDetail(field="account", reason=exc.code),),
                trace_id=trace_id,
            )

    qty = BASELINE_QTY
    if strategy.max_position_size is not None and strategy.max_position_size > 0:
        qty = min(qty, float(strategy.max_position_size))

    decision = risk_engine.evaluate_entry(
        account_id=account_id,
        strategy_id=strategy.id,
        symbol=strategy.symbol,
        side="buy",
        quantity=qty,
        trace_id=trace_id,
    )
    if not decision.allowed:
        status = 503 if decision.reason_code == "risk_unavailable" else 403
        return ActivateResult(
            ok=False,
            status_code=status,
            code=decision.reason_code,
            message=decision.message,
            details=(ErrorDetail(field="risk", reason=decision.reason_code),),
            trace_id=decision.trace_id,
        )

    try:
        oms.submit_paper_order(
            decision=decision,
            account_id=account_id,
            symbol=strategy.symbol,
            side="buy",
            quantity=qty,
            strategy_id=strategy.id,
            interval=strategy.timeframe if strategy.timeframe else "1m",
        )
    except VenueAdapterError as exc:
        return ActivateResult(
            ok=False,
            status_code=502,
            code=exc.code,
            message=exc.message,
            details=(ErrorDetail(field="venue", reason=exc.code),),
            trace_id=decision.trace_id,
        )
    return ActivateResult(ok=True, trace_id=decision.trace_id)
