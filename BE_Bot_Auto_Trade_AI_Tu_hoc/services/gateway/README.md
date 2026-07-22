# Gateway

**Ownership:** `BE_Bot_Auto_Trade_AI_Tu_Hoc/`

Single entry point for Frontend (auth, RBAC, request validation).

## Docs & contracts

- Module design: [`docs/modules/gateway-auth.md`](../../docs/modules/gateway-auth.md)
- Shared contracts: [`packages/contracts`](../../../packages/contracts)

## Run (local)

```bash
pip install -e ".[dev]"
uvicorn gateway.app:app --reload
pytest
```

## Paper-dev auth stub (P1-BE-02)

Local-only demo operator credentials (override via env; **do not commit real secrets**):

| Env var | Default (local only) |
|---|---|
| `PAPER_AUTH_EMAIL` | `operator@example.com` |
| `PAPER_AUTH_PASSWORD` | `paper-dev-password` |

Endpoints (OpenAPI):

- `POST /v1/auth/login` — body `{email, password}` → `TokenPair` or `401` Error
- `POST /v1/auth/refresh` — body `{refresh_token}` → new `TokenPair` or `401`
- `POST /v1/auth/logout` — `Authorization: Bearer <access>` and/or body `{refresh_token}` → `{success: true}`

Tokens are held in an **in-memory** store (process-local; lost on restart). Passwords and raw tokens are never logged.
