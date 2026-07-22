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
  - 2026-07-22: gateway **51 passed**; `tsc --noEmit` **PASS**

---

## Phase 2: Foundational (blocking)

- [x] T003 Decide paper order public surface: implement existing `/v1/orders` stub per OpenAPI **or** RFC additive paper-order ops — document choice in `contracts/README.md`
  - **LOCKED**: Internal Strategy→Risk→OMS→adapter path; no public create-order in OpenAPI today; Gateway `POST /v1/orders` is non-contract (FE must not call). See `contracts/README.md` § T003.
- [ ] T004 Quarantine/remove undocumented Gateway `POST /v1/orders` (or RFC `postOrders` only if Owner later wants public manual orders) — **no OpenAPI add required for US1**
- [ ] T005 [P] BE: wire Gateway → core-trading strategy/risk/oms module boundaries (no FE)
- [ ] T006 [P] BE: paper adapter interface (testnet **or** internal matcher per research D1)
- [ ] T007 BE: ensure every entry path calls fail-closed risk guard + persists `risk_check_id`
- [ ] T008 BE: propagate `trace_id` on risk/order logs/events (no secrets)

**Checkpoint**: Contract choice locked; risk guard on entry path

---

## Phase 3: User Story 1 — Paper order path (P1) 🎯

**Goal**: Connect → activate simple strategy → paper risk/order outcome → server positions/P&L

- [ ] T009 [US1] BE: paper credential validation hook (fail closed on invalid; never log secrets)
- [ ] T010 [US1] BE: simple strategy runner produces baseline signal (non-DL) when active
- [ ] T011 [US1] BE: Risk allow/deny with stored RiskCheck; deny returns Error model
- [ ] T012 [US1] BE: OMS + paper adapter submit/fill simulation or testnet; update ledger
- [ ] T013 [US1] BE: `getPositions` / `getPnlSummary` / `getReportsTrades` read from ledger (not empty fixtures only)
- [ ] T014 [P] [US1] FE: accounts/strategy flows already present — bind live errors; show risk-reject clearly
- [ ] T015 [P] [US1] FE: dashboard positions/P&L/activity refresh server truth after activate (no client PnL math)
- [ ] T016 [US1] Tests: allow path creates paper order/fill; risk-down path zero entries
- [ ] T017 [US1] Extend `wave9_smoke.py` (or successor) to assert paper order/risk outcome

**Checkpoint**: SC-001–SC-003 demonstrable on paper env

---

## Phase 4: User Story 2 — L1 pause (P1)

- [ ] T018 [US2] BE: L1 engaged blocks new entries in strategy/OMS path (not only status flag)
- [ ] T019 [P] [US2] FE: KillSwitchBar remains always visible; confirm before mutate; show engaged state
- [ ] T020 [US2] Tests: engage L1 → entry attempts rejected

**Checkpoint**: SC-004

---

## Phase 5: User Story 3 — Review loop (P2)

- [ ] T021 [P] [US3] BE: alerts for risk reject / kill-switch engage (no secrets in message)
- [ ] T022 [P] [US3] FE: reports filter + copy/export; alerts inbox shows new codes
- [ ] T023 [US3] Manual quickstart §4 checklist recorded PASS in PR description

---

## Phase 6: Polish & gates

- [ ] T024 [P] Mark Deferred still out of MVP in FE `/models` and strategy UI (no promote/no-code)
- [ ] T025 Run full gateway pytest + FE tsc + `validate_governance.py` PASS
- [ ] T026 Update `docs/shared/agent-assignment.yaml` notes when feature demo-complete (Owner)
- [ ] T027 Set `specs/002-paper-trading-e2e/spec.md` Status → Implemented (after Owner accept)

---

## Dependencies

```text
Phase1 → Phase2 → Phase3 (US1) → Phase4 (US2) → Phase5 (US3) → Phase6
T003/T004 before FE binds any new order fields
T007 before T010–T012
```

## Parallel examples

```text
After T008:
  T009–T013 (BE) with T014–T015 (FE) in parallel where contracts stable
  T018 (BE) ∥ T019 (FE)
  T021 (BE) ∥ T022 (FE)
```

## Implementation strategy

1. Lock contracts (T003–T004)
2. Deliver US1 paper path first (value + safety)
3. Harden L1 block (US2)
4. Review/alerts polish (US3)
5. Do **not** open Deferred or live capital
