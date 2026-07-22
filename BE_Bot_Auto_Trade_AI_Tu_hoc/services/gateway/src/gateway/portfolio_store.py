"""Portfolio / trade-report read models — backed by paper ledger (T013)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from gateway.trading import ledger


def clear() -> None:
    ledger.clear()


def seed_position(**kwargs: Any) -> dict[str, Any]:
    return ledger.seed_position(**kwargs)


def seed_trade(**kwargs: Any) -> dict[str, Any]:
    return ledger.seed_trade(**kwargs)


def list_positions(
    *,
    account_id: str,
    symbol: str | None = None,
    open_only: bool = True,
) -> list[dict[str, Any]]:
    return ledger.list_positions(
        account_id=account_id,
        symbol=symbol,
        open_only=open_only,
    )


def get_pnl_summary(
    *,
    account_id: str,
    from_time: datetime | None = None,
    to_time: datetime | None = None,
) -> dict[str, Any]:
    """Server-side PnL from ledger — FE must not invent these numbers."""
    realized = 0.0
    unrealized = 0.0
    for pos in list_positions(account_id=account_id, open_only=False):
        unrealized += float(pos.get("unrealized_pnl") or 0.0)
    for trade in list_trades(account_id=account_id):
        realized += float(trade.get("realized_pnl") or 0.0)
    trade_count = len(list_trades(account_id=account_id, from_time=from_time, to_time=to_time))
    total = realized + unrealized
    return {
        "account_id": account_id,
        "currency": "USDT",
        "realized_pnl": realized,
        "unrealized_pnl": unrealized,
        "total_pnl": total,
        "gross_profit": max(total, 0.0),
        "gross_loss": min(total, 0.0),
        "trade_count": trade_count,
        "calculated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def list_trades(
    *,
    account_id: str,
    strategy_id: str | None = None,
    from_time: datetime | None = None,
    to_time: datetime | None = None,
    limit: int = 100,
) -> list[dict[str, Any]]:
    return ledger.list_trades(
        account_id=account_id,
        strategy_id=strategy_id,
        from_time=from_time,
        to_time=to_time,
        limit=limit,
    )
