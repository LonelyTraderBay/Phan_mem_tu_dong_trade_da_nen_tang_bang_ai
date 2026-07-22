# Contracts touchpoints — Paper Trading E2E

This feature **consumes** existing MVP OpenAPI in `packages/contracts/openapi/openapi.yaml`.

## Required operationIds (already present, `x-mvp: true`)

| Area | operationIds |
|---|---|
| Auth | `postAuthLogin`, `postAuthRefresh`, `postAuthLogout` |
| Accounts | `postAccounts`, `postAccountApiKeys` |
| Strategies | `getStrategies`, `postStrategies`, `patchStrategy` |
| Market | `getMarketSymbols`, `getMarketCandles` |
| Portfolio | `getPositions`, `getPnlSummary`, `getReportsTrades` |
| Safety | `getKillSwitchStatus`, `postKillSwitch`, `getAlerts` |
| System | `getHealth`, `getReady` |

## T003 Decision (2026-07-22) — LOCKED

**Choice: Internal paper order path (no public REST order create for US1 acceptance).**

| Question | Answer |
|---|---|
| Does OpenAPI define `POST /v1/orders` / `postOrders` today? | **No** — matrix MVP ops do not include a public create-order operationId |
| Gateway `POST /v1/orders` 501 stub? | **Non-contract** scaffold leftover — **FE MUST NOT call it**; treat as deprecated until removed or RFC’d |
| How does US1 prove paper E2E? | Strategy runner → Risk (`risk_check_id`) → OMS → paper adapter **internally**; operator verifies via `getPositions`, `getPnlSummary`, `getReportsTrades` (+ alerts). Events may use existing `order.lifecycle` schema (bus), not a new FE REST invent |
| When is a public order API allowed? | Only after **RFC + OpenAPI** lands `operationId` (e.g. `postOrders`) with `x-mvp: true`, then BE implement / FE bind (see T004) |

### Implications for implement

1. **Do not** invent FE-facing order request/response fields.
2. **T004**: Prefer **remove or quarantine** undocumented `POST /v1/orders` from Gateway public router (or leave 501 with explicit “non-contract” comment) — **no OpenAPI add required for US1**.
3. If Owner later wants manual “Place paper order” UI → open RFC (T004 variant) before coding.

## Deferred (do not implement)

- `postModelPromote` (`x-mvp: false`)
- Public discretionary order entry UI (until RFC)
