"""Portfolio & Ledger boundary.

Phase-1 paper ledger lives in Gateway: `gateway.trading.ledger`
(portfolio reads via `gateway.portfolio_store`).
This package documents the module boundary for later extraction.
"""

PHASE1_IMPL = "gateway.trading.ledger"
