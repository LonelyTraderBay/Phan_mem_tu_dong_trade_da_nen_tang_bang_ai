# Feature Specification: Prod-Live Capital Envelope (≤5% NAV)

**Feature Branch**: `009-prod-live-capital-envelope`

**Created**: 2026-07-23

**Status**: Implemented

**Input**: Owner `Active PROD-LIVE — scope: ≤5% NAV …` — capital envelope and fail-closed live guard. Ellipsis = NAV absolute / venue / Risk sign-off still incomplete → MUST NOT place mainnet orders in this feature.

## User Stories

### US1 - Capital cap ≤5% NAV is policy-enforced (P1)

System records Owner scope max live capital = **≤5% NAV** and refuses live (non-testnet) entry attempts unless explicit enable flags + NAV configured; still no mainnet adapter in this wave.

### US2 - Live path fail-closed without Phase-2 (P1)

If `account.testnet=false` or live mode requested, Gateway rejects with clear code unless `LIVE_TRADING_ENABLED` + `PHASE2_GATES_ACK` + NAV env present — and even then returns **not implemented** for mainnet submit (separate feature required).

## Requirements

- **FR-001**: Document capital policy ≤5% NAV under `docs/shared/`.
- **FR-002**: Implement `live_capital` guard module (env-driven).
- **FR-003**: Block non-testnet account activate/submit with fail-closed errors.
- **FR-004**: MUST NOT call Binance mainnet / live exchange APIs in this feature.
- **FR-005**: MUST NOT invent Risk Officer signature or tick Phase-2 Pass.

## Success Criteria

- pytest covers reject live without flags / reject even with flags (no mainnet adapter).
- validate_governance PASS; Owner told remaining inputs for true live.
