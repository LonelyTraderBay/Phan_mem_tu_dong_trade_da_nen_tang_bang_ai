# Tasks: Paper Trading E2E

**Input**: Design documents from `/specs/002-paper-trading-e2e/`

**Prerequisites**: plan.md (Constitution Check PASS), spec.md, research.md, data-model.md, contracts/README.md, quickstart.md

**Assignment**: `TRADING-E2E` (active) — see `docs/shared/agent-assignment.yaml`

**Organization**: Parallel BE/FE where marked [P]; contract RFC before inventing public fields.

## Format: `[ID] [P?] [Story] Description`

---

## Phase 1: Setup

- [x] T001 Verify `specs/002-paper-trading-e2e/` artifacts + `.\scripts\validate-contracts.ps1` PASS
  - 2026-07-22: all feature artifacts present; `validate_governance.py` → **RESULT: PASS**
- [x] T002 [P] Confirm Gateway pytest baseline still green; FE `tsc` green on current branch
  - 2026-07-22: gateway pytest green; `tsc --noEmit` **PASS**

---

## Phase 2: Foundational (blocking)

- [x] T003 Decide paper order public surface — **LOCKED** internal path (see `contracts/README.md`)
- [x] T004 Quarantine/remove undocumented Gateway `POST /v1/orders` — **removed**
- [x] T005 [P] BE: wire Gateway → core-trading module boundaries (`core_trading/*/PHASE1_IMPL` + `gateway/trading/`)
- [x] T006 [P] BE: paper adapter internal matcher (`gateway/trading/paper_adapter.py`)
- [x] T007 BE: entry path fail-closed + `risk_check_id` (`risk_engine` + `risk_guard`)
- [x] T008 BE: `trace_id` on risk/order path (no secrets)

**Checkpoint**: PASS

---

## Phase 3: User Story 1 — Paper order path (P1) 🎯

- [x] T009 [US1] BE: credential required before activate (fail closed; no secret logs)
- [x] T010 [US1] BE: baseline signal on activate (`strategy_runner`)
- [x] T011 [US1] BE: Risk allow/deny + stored RiskCheck
- [x] T012 [US1] BE: OMS + paper adapter fill → ledger
- [x] T013 [US1] BE: positions/pnl/trades from ledger
- [x] T014 [P] [US1] FE: honest risk/kill-switch/not_found errors on strategies
- [x] T015 [P] [US1] FE: dashboard server-truth + Refresh
- [x] T016 [US1] Tests: allow path fill; risk-down zero entries (`test_paper_trading_e2e.py`)
- [x] T017 [US1] `wave9_smoke.py` asserts positions/trades after activate

**Checkpoint**: PASS (smoke + 55 pytest)

---

## Phase 4: User Story 2 — L1 pause (P1)

- [x] T018 [US2] BE: L1 engaged blocks entries in `risk_engine`
- [x] T019 [P] [US2] FE: KillSwitchBar always visible + confirm + engaged state
- [x] T020 [US2] Tests: L1 → entry rejected

**Checkpoint**: PASS

---

## Phase 5: User Story 3 — Review loop (P2)

- [x] T021 [P] [US3] BE: alerts `RISK_REJECTED` / `KILL_SWITCH_ACTIVE`
- [x] T022 [P] [US3] FE: reports + alerts code/message UX
- [x] T023 [US3] Quickstart §4 / wave9 smoke recorded **PASS** 2026-07-22

---

## Phase 6: Polish & gates

- [x] T024 [P] FE `/models` Deferred callout; strategies form-only
- [x] T025 gateway pytest **55 passed** + FE tsc PASS + `validate_governance` PASS (2026-07-22)
- [x] T026 `agent-assignment.yaml` notes updated (demo-complete)
- [x] T027 `spec.md` Status → **Implemented**

---

## Dependencies

```text
Phase1 → Phase2 → Phase3 (US1) → Phase4 (US2) → Phase5 (US3) → Phase6
```

## Implementation strategy

Completed 2026-07-22 on branch `cursor/cloud-agent-1784715111455-vg2c7`.
Paper/testnet internal path only — no live capital, no Deferred.
