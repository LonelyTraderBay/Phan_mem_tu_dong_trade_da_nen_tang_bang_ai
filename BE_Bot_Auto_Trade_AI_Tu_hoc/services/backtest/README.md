# Backtest Service

**Ownership:** BE

Standalone Backtesting Engine container (offline jobs, off the live hot path). Skeleton only — no simulation or metrics yet.

## Docs & contracts

- Architecture: [`Kien-truc-Bot-Auto-Trade-AI-v2-Enterprise.md`](../../Kien-truc-Bot-Auto-Trade-AI-v2-Enterprise.md)
- Shared contracts: [`packages/contracts`](../../packages/contracts)

## Run (local)

```bash
pip install -e ".[dev]"
uvicorn backtest_service.app:app --reload
pytest
```
