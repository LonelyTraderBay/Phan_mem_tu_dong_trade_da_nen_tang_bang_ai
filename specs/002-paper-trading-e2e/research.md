# Research: Paper Trading E2E

**Feature**: `002-paper-trading-e2e` · **Date**: 2026-07-22

## Decisions

### D1 — Paper venue strategy

**Decision**: Prefer exchange **testnet/paper API** when credentials present; otherwise use an **internal paper matcher** in the adapter module for CI/local demos.

**Rationale**: CI cannot depend on external secrets; constitution allows stubs until gates pass, but E2E must still exercise Risk→OMS.

**Alternatives rejected**: Live mainnet (out of scope); delaying E2E until only external testnet (blocks CI).

### D2 — Signal source for simple strategy

**Decision**: Rule/baseline signal inside Strategy module (e.g. scheduled/demo tick or simple threshold on paper candles) — **not** deep-learning-primary (Deferred).

**Rationale**: Matrix In-MVP is simple strategy run; DL-primary is Deferred phase-3.

### D3 — Persistence

**Decision**: Start with durable-enough paper ledger for the demo process (SQLite or existing service store if already present); in-memory only acceptable for unit tests, not for the acceptance E2E happy path if process restart is required mid-demo.

**Rationale**: Operator review (US3) needs stable trade history during a paper day.

### D4 — Contracts (locked by T003)

**Decision**: Reuse MVP OpenAPI operations already tagged `x-mvp: true`. Paper entry path is **internal** (Strategy→Risk→OMS→adapter). Acceptance via portfolio/report APIs. Gateway `POST /v1/orders` is **not** in OpenAPI → non-contract; FE must not call; remove/quarantine under T004. Public `postOrders` only after future RFC.

**Rationale**: OpenAPI has no create-order operationId today; inventing FE order API would violate constitution I.

### D5 — Parallel lanes

**Decision**: Keep BE/FE split; shared work only on `packages/contracts` + docs via assignment; activate `TRADING-E2E` with task IDs in `tasks.md`.

**Rationale**: Existing governance + path policy.

## Open points resolved by assumption

| Topic | Assumption |
|---|---|
| Venue | Crypto paper/testnet first |
| Operator | Solo |
| L2–L4 | Not required for P1 acceptance beyond L1 block; keep UI disabled/confirm stubs |
| WS | Optional enhancement; REST sufficient for acceptance if positions/reports update on refresh |

## References

- `docs/shared/mvp-capability-matrix.md`
- `docs/shared/parallel-dispatch-phase1.md` (stub baseline)
- `.specify/memory/constitution.md`
- `packages/contracts/openapi/openapi.yaml`
