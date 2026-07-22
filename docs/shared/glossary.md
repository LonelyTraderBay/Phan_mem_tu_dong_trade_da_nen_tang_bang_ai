# Glossary

| Term | Meaning |
|---|---|
| Champion / Challenger | Production model vs candidate under evaluation |
| Shadow trading | Challenger runs on live data without placing real orders |
| Canary | Small real capital allocation, ramped if stable |
| Drift (PSI / KS) | Distribution shift vs training data |
| Sharpe / Sortino / PSR / DSR | Risk-adjusted return metrics; DSR adjusts for multiple testing |
| Idempotency | Retries produce one effect (`Idempotency-Key` / `client_order_id`) |
| Kill-switch L1–L4 | Pause → halt orders → flatten → full lockdown |
| Reconciliation break | Ledger vs broker mismatch; **broker wins** |
| Walk-forward | Time-ordered train/test with purge + embargo |
| Slippage | Expected vs fill price gap |
| SLO / SLI / Error budget | Ops targets; exhausted budget freezes risky change |
| SoD / Dual-control | Proposer ≠ approver for dangerous actions |
| Schema Registry | Blocks incompatible event payloads |
| WORM | Append-only audit retention |
| MRM | Model Risk Management (card, owner, review, calibration) |
| Fail-closed | If risk path unavailable → no new orders |
| Gateway | Sole FE entrypoint (REST + WS) |
