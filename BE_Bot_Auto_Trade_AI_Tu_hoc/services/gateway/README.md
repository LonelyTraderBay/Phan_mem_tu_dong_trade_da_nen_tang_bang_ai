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

## Paper market visibility stub (P1-BE-05)

Fixture/mock market data (not a live exchange feed). Requires `Authorization: Bearer <access>`.

| Method | Path | OpenAPI |
|---|---|---|
| `GET` | `/v1/market/symbols` | `getMarketSymbols` — optional `exchange`, `market_type` |
| `GET` | `/v1/market/candles` | `getMarketCandles` — required `symbol`, `interval`; optional `start_time`, `end_time`, `limit` |

### Stale marker

OpenAPI `MarketSymbol` / `Candle` have **no** stale body field. Paper fixtures always advertise non-live data via response header:

```http
X-Market-Stale: true
```

Clients MUST treat fixture responses as stale. Unknown `symbol` on candles returns an empty array with the same header (empty/error path — no invented body field).
