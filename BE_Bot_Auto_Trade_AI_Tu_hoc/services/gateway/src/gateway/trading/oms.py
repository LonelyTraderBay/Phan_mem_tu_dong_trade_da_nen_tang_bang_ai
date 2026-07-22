"""Paper OMS — submits to adapter only when risk allow + risk_check_id present."""

from __future__ import annotations

from typing import Any

from gateway.trading import paper_adapter
from gateway.trading.risk_engine import RiskDecision


class OmsError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


def submit_paper_order(
    *,
    decision: RiskDecision,
    account_id: str,
    symbol: str,
    side: str,
    quantity: float,
    strategy_id: str | None = None,
    interval: str = "1m",
) -> dict[str, Any]:
    if not decision.allowed:
        raise OmsError("OMS refuses submit without risk allow")
    if not decision.risk_check_id:
        raise OmsError("OMS refuses submit without risk_check_id")
    return paper_adapter.submit_and_fill(
        account_id=account_id,
        symbol=symbol,
        side=side,
        quantity=quantity,
        risk_check_id=decision.risk_check_id,
        trace_id=decision.trace_id,
        strategy_id=strategy_id,
        interval=interval,
    )
