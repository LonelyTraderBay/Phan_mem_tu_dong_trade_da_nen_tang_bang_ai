# Tasks: MVP Feature Scope Optimization

**Input**: Design documents from `/specs/001-mvp-feature-scope/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: Not requested in spec — no TDD task block unless owner asks later

**Organization**: Tasks grouped by user story for parallel BE/FE-safe delivery of the
scope matrix; US3 prepares operator paper-day alignment without implementing full
exchange trading in this feature.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no incomplete dependencies)
- **[Story]**: [US1]…[US4] for story phases only

## Path Conventions

- **Backend**: `BE_Bot_Auto_Trade_AI_Tu_Hoc/...`
- **Frontend**: `FE_Bot_Auto_Trade_AI_Tu_Hoc/...`
- **Contracts**: `packages/contracts/`
- **Shared docs**: `docs/shared/`
- **Feature**: `specs/001-mvp-feature-scope/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm feature workspace and baseline validation

- [ ] T001 Verify feature artifacts exist per `specs/001-mvp-feature-scope/quickstart.md` step 1
- [ ] T002 Run `scripts/validate-contracts.ps1` and record PASS in feature notes or PR description

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Schema + example matrix must be accepted before publishing or lane tagging

- [ ] T003 Finalize `specs/001-mvp-feature-scope/contracts/capability-matrix.schema.json` fields against `specs/001-mvp-feature-scope/data-model.md`
- [ ] T004 Complete `specs/001-mvp-feature-scope/contracts/mvp-capability-matrix.example.yaml` so every FR-002 In-MVP capability appears with lane + rationale
- [ ] T005 Ensure Deferred list in example YAML includes AI retrain/promote, no-code builder, multi-user SaaS, MT5, deep-learning primary per FR-005 / US4

**Checkpoint**: Example matrix reviewable in &lt;15 minutes (SC-001)

---

## Phase 3: User Story 1 - Must-have capability matrix (P1) 🎯 MVP

**Goal**: Publish binding In-MVP vs Deferred catalog with reasons

**Independent Test**: Reviewer can label every listed capability and confirm paper happy-path needs only In-MVP items

- [ ] T006 [US1] Create stakeholder Markdown matrix `docs/shared/mvp-capability-matrix.md` from example YAML (tables: In-MVP and Deferred)
- [ ] T007 [US1] Add canonical YAML copy `docs/shared/mvp-capability-matrix.yaml` matching the Markdown content and schema rules
- [ ] T008 [P] [US1] Link matrix from `docs/shared/README.md` and `docs/architecture/INDEX.md`
- [ ] T009 [US1] Add amendment rule section to `docs/shared/mvp-capability-matrix.md` (owner written approval to move Deferred → In-MVP)

**Checkpoint**: US1 acceptance scenarios satisfiable from docs alone

---

## Phase 4: User Story 2 - Lane ownership map (P1)

**Goal**: Every In-MVP item has Backend / Frontend / Both / Shared owner and contract-touch flag

**Independent Test**: Table shows lane + contract prerequisite for each In-MVP row

- [ ] T010 [US2] Add “Lane ownership” section to `docs/shared/mvp-capability-matrix.md` grouping In-MVP by lane
- [ ] T011 [P] [US2] Update `BE_Bot_Auto_Trade_AI_Tu_Hoc/docs/HANDOFF-AI.md` with pointer to matrix and rule: do not implement Deferred without owner expand
- [ ] T012 [P] [US2] Update `FE_Bot_Auto_Trade_AI_Tu_Hoc/docs/HANDOFF-AI.md` with pointer to matrix and stub-vs-live UI rules for Both items
- [ ] T013 [US2] Document Both-item contract prerequisites in `docs/shared/mvp-capability-matrix.md` (list `contract_refs` requiring RFC/tag before code)

**Checkpoint**: Parallel lanes can start without Deferred AI/SaaS blockers (SC-002)

---

## Phase 5: User Story 3 - Paper-day safety alignment (P2)

**Goal**: Ensure In-MVP safety/operator path is reflected in contracts tags and FE/BE docs (not full broker E2E in this feature)

**Independent Test**: Emergency pause + credentials + fail-closed called out as In-MVP safety_critical; screens/modules point to them

- [ ] T014 [P] [US3] Tag In-MVP OpenAPI operations with `x-mvp: true` in `packages/contracts/openapi/openapi.yaml` for auth, accounts, strategies, market, positions, pnl, kill-switch, alerts, reports used by matrix
- [ ] T015 [P] [US3] Mark clearly Deferred-related model promote paths with `x-mvp: false` in `packages/contracts/openapi/openapi.yaml` where present
- [ ] T016 [US3] Add paper-day operator checklist section to `docs/shared/mvp-capability-matrix.md` (connect → run → pause → review) referencing FR-002/US3
- [ ] T017 [P] [US3] Update `FE_Bot_Auto_Trade_AI_Tu_Hoc/docs/screens/kill-switch.md` to state L1 pause is In-MVP mandatory and always visible
- [ ] T018 [P] [US3] Update `FE_Bot_Auto_Trade_AI_Tu_Hoc/docs/screens/account-api-keys.md` with masked credentials + no full reveal after save
- [ ] T019 [P] [US3] Update `BE_Bot_Auto_Trade_AI_Tu_Hoc/docs/modules/risk-management.md` noting fail-closed entries are In-MVP (docs-only until implement feature)
- [ ] T020 [US3] Run `scripts/validate-contracts.ps1` after OpenAPI tag edits; fix YAML if validation fails

**Checkpoint**: Safety controls for paper day are unambiguous in shared + lane docs

---

## Phase 6: User Story 4 - Park advanced AI & SaaS (P3)

**Goal**: Deferred list acknowledged with phase_return labels

**Independent Test**: Stakeholders see AI auto-retrain, no-code, multi-user SaaS deferred with phase tags

- [ ] T021 [US4] Ensure Deferred table in `docs/shared/mvp-capability-matrix.md` includes phase_return column (phase-2/3/4)
- [ ] T022 [P] [US4] Add explicit “Out of MVP” callout to `BE_Bot_Auto_Trade_AI_Tu_Hoc/docs/modules/ai-training.md` pointing to deferred matrix ids
- [ ] T023 [P] [US4] Add explicit “Out of MVP” callout to `FE_Bot_Auto_Trade_AI_Tu_Hoc/docs/screens/ai-model-center.md` and `strategy-builder.md`
- [ ] T024 [US4] Note in `docs/shared/release-gates.md` that Phase 4 multi-user remains legally gated and is Deferred in MVP matrix

**Checkpoint**: US4 acceptance scenarios covered by published Deferred list

---

## Phase 7: Polish & Cross-Cutting

- [ ] T025 [P] Update root `README.md` “Design & architecture” table with link to `docs/shared/mvp-capability-matrix.md`
- [ ] T026 Align `specs/001-mvp-feature-scope/contracts/mvp-capability-matrix.example.yaml` with final `docs/shared/mvp-capability-matrix.yaml` (same version)
- [ ] T027 Execute remaining steps in `specs/001-mvp-feature-scope/quickstart.md` and mark checklist in `specs/001-mvp-feature-scope/checklists/requirements.md` notes that plan/tasks ready for implement
- [ ] T028 Set `specs/001-mvp-feature-scope/spec.md` Status from Draft to Planned (or Ready for implement) after owner skim

---

## Dependencies

```text
Phase 1 → Phase 2 → Phase 3 (US1) → Phase 4 (US2)
                         ↘ Phase 5 (US3) [after T006 matrix exists]
                         ↘ Phase 6 (US4) [after T006 matrix exists]
Phase 7 after US1–US4 core docs exist
```

- US2 depends on US1 matrix file existing
- US3/US4 can proceed in parallel after T006
- T014/T015 (OpenAPI) parallelizable; T020 after both

## Parallel execution examples

```text
# After T006:
T008 + T011 + T012 in parallel
T014 + T015 + T017 + T018 + T019 in parallel
T022 + T023 in parallel
```

## Implementation strategy

1. **MVP first**: Complete US1 + US2 (matrix + lanes) — unlocks parallel coding later
2. **Then** US3 safety alignment tags/docs
3. **Then** US4 deferred callouts
4. **Do not** implement live/paper broker E2E inside these tasks — spawn follow-on
   features from In-MVP rows when ready for `/speckit-implement` of trading code

## Suggested MVP scope for first implement pass

Execute **T001–T013** (Setup + Foundational + US1 + US2) before any trading code feature.
