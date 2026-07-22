"""Ledger vs paper-adapter view reconciliation (read-only; alerts on mismatch)."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from gateway import alerts_store
from gateway.trading import ledger

_runs: list[dict[str, Any]] = []


def clear() -> None:
    _runs.clear()


def _adapter_position_qty(account_id: str, symbol: str) -> float:
    """Derive adapter view from fills (buy +, sell −) as absolute net size."""
    qty = 0.0
    for fill in ledger.list_fills(account_id=account_id):
        if fill["symbol"] != symbol:
            continue
        signed = float(fill["quantity"])
        if fill["side"] == "sell":
            signed = -signed
        qty += signed
    return abs(qty)


def run_reconciliation(*, account_id: str | None = None) -> dict[str, Any]:
    """Compare open ledger positions to fill-derived adapter qty."""
    trace_id = str(uuid4())
    positions = ledger.list_positions(account_id=account_id, open_only=True)

    diffs: list[dict[str, Any]] = []
    for pos in positions:
        acct = pos["account_id"]
        symbol = pos["symbol"]
        ledger_qty = float(pos["quantity"])
        adapter_qty = _adapter_position_qty(acct, symbol)
        if abs(ledger_qty - adapter_qty) > 1e-9:
            diffs.append(
                {
                    "account_id": acct,
                    "symbol": symbol,
                    "field": "quantity",
                    "ledger_value": ledger_qty,
                    "adapter_value": adapter_qty,
                }
            )

    status = "ok" if not diffs else "mismatch"
    run = {
        "id": str(uuid4()),
        "trace_id": trace_id,
        "status": status,
        "positions_compared": len(positions),
        "diffs_count": len(diffs),
        "diffs": diffs,
    }
    _runs.append(run)

    if status == "mismatch":
        sample = diffs[0]
        alerts_store.seed_alert(
            account_id=sample.get("account_id"),
            severity="critical",
            code="RECON_MISMATCH",
            message=(
                f"Reconciliation mismatch on {sample['symbol']}: "
                f"ledger={sample['ledger_value']} adapter={sample['adapter_value']} "
                f"(trace_id={trace_id})"
            ),
        )
    return dict(run)


def list_runs() -> list[dict[str, Any]]:
    return [dict(r) for r in _runs]
