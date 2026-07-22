# Tasks: Prod-Paper Harden

**Input**: Design documents from `/specs/003-prod-paper-harden/`  
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/README.md, RFC-0002  
**Assignment**: `PROD-PAPER-HARDEN`

## Phase 1 — Setup

- [x] T001 Verify feature artifacts + link from `docs/shared/README.md` / release-gates
- [x] T002 [P] Confirm Gateway pytest + FE `tsc` baseline still green on branch

## Phase 2 — Foundational (contracts)

- [x] T003 Land RFC-0002 OpenAPI additive `level` + `confirmed` on KillSwitch schemas; bump `packages/contracts/VERSION` minor
- [x] T004 Run `.\scripts\validate-contracts.ps1` → PASS after T003
- [x] T005 [P] Add `docs/shared/paper-ops-tracker.md` and link from `release-gates.md`

## Phase 3 — US1 Kill-switch L1–L4

- [x] T006 [US1] BE: extend `kill_switch_store` + router for levels; L1 preserves entry block
- [x] T007 [US1] BE: L2+ require `confirmed`; reject + audit when missing
- [x] T008 [US1] BE: L3 cancel open paper orders; L4 paper-internal flatten (no live claim)
- [x] T009 [P] [US1] FE: KillSwitchBar shows level; confirm UX for L2+
- [x] T010 [US1] Tests: L1 block; L2 without confirm rejected; L4 paper flatten stub

## Phase 4 — US2 Reconciliation

- [x] T011 [US2] BE: `reconciliation` module compare ledger vs paper adapter
- [x] T012 [US2] BE: mismatch → alert `RECON_MISMATCH` (existing getAlerts)
- [x] T013 [P] [US2] FE: alerts page surfaces recon codes clearly
- [x] T014 [US2] Tests: matched OK; forced mismatch creates alert

## Phase 5 — US3 Secrets + paper-ops + gates

- [x] T015 [US3] Confirm gitleaks/governance secrets rules still PASS; note on release-gates
- [x] T016 [US3] Update `release-gates.md` Phase 1 checkboxes with status notes (tooling vs calendar)
- [x] T017 [US3] Quickstart §2–4 recorded PASS

## Phase 6 — Polish / close

- [x] T018 gateway pytest **61 passed** + FE tsc PASS + validate_governance PASS (2026-07-22)
- [x] T019 `agent-assignment.yaml`: `PROD-PAPER-HARDEN` → done; next stays blocked until Owner names venue
- [x] T020 `spec.md` Status → Implemented

## Stop rule

Do not invent exchange for `PAPER-TESTNET-ADAPTER` without Owner naming venue.
