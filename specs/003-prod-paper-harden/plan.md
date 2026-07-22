# Implementation Plan: Prod-Paper Harden

**Branch**: `003-prod-paper-harden` (spec) / implement on current working branch unless Owner cuts a dedicated branch | **Date**: 2026-07-22 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/003-prod-paper-harden/spec.md`

## Summary

Close Phase 1 → `prod-paper` release-gate gaps after paper E2E demo: **additive kill-switch L1–L4** (contract-first), **ledger↔paper-adapter reconciliation + alerts**, **secrets hygiene linkage**, and a **paper-ops criteria tracker** (docs/counters — not a 30-day CI wait). Remains paper/staging only.

## Technical Context

**Language/Version**: Python 3.12 (Gateway), TypeScript (Next.js FE)

**Primary Dependencies**: FastAPI Gateway + existing `gateway/trading/*`, kill-switch store, alerts store; Next.js FE KillSwitchBar / alerts pages

**Storage**: In-memory/dev-durable OK for paper staging; reconciliation runs append-only list; no new top-level DB service required for this feature

**Testing**: pytest (kill-switch levels, recon mismatch→alert); FE `tsc`; `scripts/validate_governance.py` PASS; extend smoke optionally

**Target Platform**: Local/dev + staging paper (internal matcher); not prod-live

**Project Type**: Monorepo BE/FE + `packages/contracts`

**Performance Goals**: Recon run completes for solo paper book in seconds; kill-switch mutate remains sync + audited

**Constraints**: Contract-first additive for levels; fail-closed; no secrets; no Deferred; no live flatten claims

**Scale/Scope**: Solo operator, one paper account, staging demonstration of L1–L4 + recon

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **I. Contract-First**: RFC + OpenAPI additive `level` (and related) before BE/FE; no invent paths
- [x] **II. Capital Safety**: L1 blocks entries; L2+ confirm/SoD; recon read-only (no orders); fail-closed
- [x] **III. Traceability**: `trace_id` on kill-switch escalate + recon runs; no secrets in logs
- [x] **IV. Test & Gates**: validate_governance; unit/integration for L1, L2+ reject, recon alert
- [x] **V. Phase Discipline**: Phase 1 `prod-paper` only; no multi-user / AI promote / MT5 / live
- [x] **Ownership**: BE `BE_*`, FE `FE_*`, contracts/docs shared via RFC

**Post-design re-check**: PASS — extend Gateway modules + FE surfaces; optional docs-only tracker under `docs/shared/`.

## Project Structure

### Documentation (this feature)

```text
specs/003-prod-paper-harden/
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
BE_Bot_Auto_Trade_AI_Tu_Hoc/services/gateway/
FE_Bot_Auto_Trade_AI_Tu_Hoc/web/
packages/contracts/
docs/shared/ (release-gates, RFC, paper-ops tracker)
```

**Structure Decision**: Extend Gateway kill-switch + trading ledger/adapter; no new service root.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|---|---|---|
| None | — | — |
