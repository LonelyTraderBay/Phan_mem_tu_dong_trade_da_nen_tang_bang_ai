# Gateway

**Ownership:** `BE_Bot_Auto_Trade_AI_Tu_Hoc/`

Single entry point for Frontend (auth, RBAC, request validation). Phase 1 paper stubs are in-memory only — not for live capital.

## Docs & contracts

- Module design: [`docs/modules/gateway-auth.md`](../../docs/modules/gateway-auth.md)
- Shared contracts: [`packages/contracts`](../../../packages/contracts)

## Paper stub credentials (local only)

| Field | Value |
|---|---|
| Email | `operator@paper.local` |
| Password | `PaperStub!123` |

Do **not** log the password or put real broker secrets in this README / commits.

## Run (local)

```bash
pip install -e ".[dev]"
uvicorn gateway.app:app --reload
python -m pytest
```

Protected `/v1/*` routes require `Authorization: Bearer <access_token>` from `POST /v1/auth/login`.
Market responses may include header `X-Data-Stale: true` (paper feed, not live).
