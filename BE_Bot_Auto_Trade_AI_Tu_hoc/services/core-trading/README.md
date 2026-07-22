# Core Trading

**Ownership:** BE

Phase-1 container for the synchronous hot path (Strategy → Risk → OMS) plus Adapter, Ledger, and Notification module boundaries. Skeleton only — no business logic, DB, or broker clients.

## Modules

| Package | Boundary |
| --- | --- |
| `adapter` | Normalize exchange/broker differences behind one interface |
| `strategy` | Combine AI signals with filters/sizing; call Risk sync |
| `risk` | Limits, kill-switch, fail-closed risk-check |
| `oms` | Order state machine + idempotent submit via Adapter |
| `ledger` | Intent/history book; reconcile toward venue truth |
| `notification` | Severity-based human alerts |

## Docs & contracts

- Architecture: [`Kien-truc-Bot-Auto-Trade-AI-v2-Enterprise.md`](../../Kien-truc-Bot-Auto-Trade-AI-v2-Enterprise.md)
- Shared contracts: [`packages/contracts`](../../packages/contracts)

## Run (local)

```bash
pip install -e ".[dev]"
uvicorn core_trading.app:app --reload
pytest
```
