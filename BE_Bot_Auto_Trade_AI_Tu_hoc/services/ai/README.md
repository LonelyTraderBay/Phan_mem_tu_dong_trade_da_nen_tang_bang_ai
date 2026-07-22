# AI Service

**Ownership:** AI / ML

Phase-1 container for Training Pipeline, Inference, and Model Registry. Skeleton only — no model I/O or training jobs yet.

## Docs & contracts

- Architecture: [`Kien-truc-Bot-Auto-Trade-AI-v2-Enterprise.md`](../../Kien-truc-Bot-Auto-Trade-AI-v2-Enterprise.md)
- Shared contracts: [`packages/contracts`](../../packages/contracts)

## Run (local)

```bash
pip install -e ".[dev]"
uvicorn ai_service.app:app --reload
pytest
```
