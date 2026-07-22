"""Phase-1 paper trading engine (Strategy → Risk → OMS → adapter → ledger).

Internal path only — no public create-order REST. See specs/002-paper-trading-e2e.
"""

from gateway.trading import strategy_runner

__all__ = ["strategy_runner"]
