# Research: Prod-Paper Harden

**Date**: 2026-07-22

## Decisions

### D1 — Kill-switch levels via additive OpenAPI (not boolean-only)

- **Decision**: Add optional/required `level` enum `L1|L2|L3|L4` on `KillSwitchRequest` / `KillSwitchStatus`. Keep `engaged` for backward compatibility (L1 engage ≡ engaged true at level L1).
- **Rationale**: Current contract is boolean-only; constitution requires L1–L4; additive avoids breaking FE/BE stubs from 002.
- **Alternatives rejected**: Separate endpoints per level (more surface); breaking replace of `engaged` (unnecessary churn).

### D2 — L2+ confirm in Gateway paper staging

- **Decision**: For paper staging, require explicit confirm flag in request body (additive `confirmed: boolean`) for L2+ engage/disengage/resume; SoD dual-control remains documented for prod-live and may stub-reject if second approver absent.
- **Rationale**: Demonstrates gate without full identity SoD infra.
- **Alternatives rejected**: Full dual-control IdP (Phase 2+ scope).

### D3 — L4 flatten = paper-internal cancel/flat stub

- **Decision**: L4 triggers internal paper position flatten/cancel-all against ledger/adapter matcher; response MUST NOT claim external exchange flatten.
- **Rationale**: No testnet venue in this feature (queued next).
- **Alternatives rejected**: Block L4 until external testnet (delays prod-paper gate demo).

### D4 — Reconciliation as Gateway-internal job + optional POST trigger

- **Decision**: Implement `reconciliation` module in Gateway; scheduled/on-interval in-process for paper + authenticated internal/dev trigger if contract allows. Prefer extending alerts only; if a public recon GET/POST is needed, RFC additive ops first.
- **Rationale**: Gate needs job + alerts; public UI can rely on alerts first; avoid inventing paths.
- **Alternatives rejected**: Kafka-based recon service (premature microservice).

### D5 — ≥30-day paper is ops tracker, not CI clock

- **Decision**: Add `docs/shared/paper-ops-tracker.md` (+ optional YAML progress); release-gates links to it; AI marks tooling done, Owner records calendar days.
- **Rationale**: Cannot honestly auto-complete 30 days in one implement session.
- **Alternatives rejected**: Fake “30 days passed” checkbox in CI.

### D6 — Priority queue after this feature

1. Done/active: `PROD-PAPER-HARDEN` (this)
2. Next blocked: `PAPER-TESTNET-ADAPTER` — external crypto testnet adapter
3. Then blocked: `PAPER-WS-REALTIME` — only if WS channels already in contracts / RFC
4. Then blocked: `PROD-LIVE-PREP` — Phase 2 gates (chaos, pen-test, capital) — Owner amend when ready

## Open questions resolved

| Topic | Resolution |
|---|---|
| Public recon API? | Prefer alerts-only for MVP of this feature; add GET recon status only if FE needs it → RFC |
| Live capital? | Out of scope |
| MT5? | Deferred matrix — out of scope |
