# Implementation Plan: Paper Trading E2E

**Branch**: `002-paper-trading-e2e` (spec) / implement on current working branch unless Owner cuts a dedicated branch | **Date**: 2026-07-22 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-paper-trading-e2e/spec.md`

## Summary

Upgrade Phase-1 paper stubs into a **paper/testnet E2E loop**: authenticated operator connects masked credentials, runs a simple strategy through **Strategy → Risk → OMS → paper adapter** with fail-closed risk and L1 pause, and reviews server-truth positions/P&L/activity. Contract-first on existing MVP OpenAPI (`x-mvp: true`); Deferred matrix items remain out of scope.

## Technical Context

**Language/Version**: Python 3.12 (Gateway / core-trading), TypeScript (Next.js FE web)

**Primary Dependencies**: FastAPI (Gateway), existing modular-monolith core-trading modules (strategy/risk/oms/adapter/ledger), Next.js FE client already bound to OpenAPI ops

**Storage**: In-process / lightweight persistence acceptable for paper Phase-1 E2E; prefer durable store only where needed for restart-safe paper ledger (document choice in research.md)

**Testing**: pytest (Gateway + risk/OMS unit), FE `tsc`; Wave-9 style API smoke extended to paper order path; `scripts/validate_governance.py` PASS

**Target Platform**: Local/dev compose + paper/testnet venue (or internal paper matcher for CI)

**Project Type**: Monorepo BE/FE services with shared `packages/contracts`

**Performance Goals**: Operator paper-day UX (SC-001 ≤15 min); sync risk path with explicit timeout (constitution)

**Constraints**: Paper only; no live capital; no secrets in git/logs; FE Gateway-only; fail-closed entries; no Deferred features

**Scale/Scope**: Solo operator, single paper account, one simple strategy path for acceptance demo

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify against `.specify/memory/constitution.md` (v1.0.0+):

- [x] **I. Contract-First**: Use existing MVP OpenAPI ops; additive gaps → RFC before code; FE consumes only; BE implements
- [x] **II. Capital Safety**: Paper entries require risk_check_id; fail-closed; Strategy→Risk→OMS sync; L1 kill-switch respected; no SoD bypass for dangerous actions (L2+ remain confirm/SoD as already documented)
- [x] **III. Traceability**: Propagate `trace_id`; never log credentials/tokens/secrets
- [x] **IV. Test & Gates**: validate_governance PASS; health/ready remain; tests for risk reject, fail-closed, L1 block, paper fill→ledger
- [x] **V. Phase Discipline**: Paper Phase-1 only; no multi-user SaaS / AI promote / MT5-first / no-code
- [x] **Ownership**: BE only `BE_Bot_Auto_Trade_AI_Tu_Hoc/`; FE only `FE_Bot_Auto_Trade_AI_Tu_Hoc/`; contracts via shared RFC if needed

**Post-design re-check**: PASS — design stays within Gateway + core-trading + FE web; no new top-level service roots.

## Project Structure

### Documentation (this feature)

```text
specs/002-paper-trading-e2e/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
├── checklists/requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
BE_Bot_Auto_Trade_AI_Tu_Hoc/services/{gateway,core-trading,data}/
FE_Bot_Auto_Trade_AI_Tu_Hoc/web/
packages/contracts/
```

**Structure Decision**: Extend existing Gateway + core-trading modules; do not invent parallel app roots.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| None | — | — |
