# Gateway

**Ownership:** `BE_Bot_Auto_Trade_AI_Tu_Hoc/`

Single entry point for Frontend (auth, RBAC, request validation). Skeleton only — no business logic yet.

## Docs & contracts

- Module design: [`docs/modules/gateway-auth.md`](../../docs/modules/gateway-auth.md)
- Shared contracts: [`packages/contracts`](../../../packages/contracts)

## Run (local)

```bash
pip install -e ".[dev]"
uvicorn gateway.app:app --reload
pytest
```
