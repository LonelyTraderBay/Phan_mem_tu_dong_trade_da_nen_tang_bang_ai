# Data Service

**Ownership:** BE

Phase-1 container for Market Data + Feature Engineering. Skeleton only — no ingestion, DB, or Feature Store wiring yet.

## Docs & contracts

- Architecture: [`Kien-truc-Bot-Auto-Trade-AI-v2-Enterprise.md`](../../Kien-truc-Bot-Auto-Trade-AI-v2-Enterprise.md)
- Shared contracts: [`packages/contracts`](../../packages/contracts)

## Run (local)

```bash
pip install -e ".[dev]"
uvicorn data_service.app:app --reload
pytest
```
