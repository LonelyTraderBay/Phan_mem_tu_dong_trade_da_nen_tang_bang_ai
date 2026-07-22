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

## Likely gap (RFC before FE binds new fields)

Scaffold still has example `POST /v1/orders` 501 stub. For paper E2E:

1. Either implement paper order creation **consistent with a documented OpenAPI operation** (extend schema via RFC if current stub is insufficient), **or**
2. Keep orders internal (Strategy→OMS) without new public POST if acceptance can verify via positions/reports/events only.

**Rule**: Do not invent FE-facing fields. If public order API is needed, land RFC + OpenAPI update first, bump `packages/contracts/VERSION` if breaking.

## Deferred (do not implement)

- `postModelPromote` (`x-mvp: false`)
