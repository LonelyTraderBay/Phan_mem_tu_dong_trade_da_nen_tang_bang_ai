# Feature Specification: Prod-Paper Harden

**Feature Branch**: `003-prod-paper-harden`

**Created**: 2026-07-22

**Status**: Implemented

**Input**: Owner authorize auto-open next priority after TRADING-E2E done — close Phase 1 → `prod-paper` gates from `docs/shared/release-gates.md` (kill-switch L1–L4 staging-ready, reconciliation + alerts, secrets hygiene, paper-ops criteria tracking). Paper only; no live capital; no Deferred matrix items.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Kill-switch L1–L4 staging-ready (Priority: P1)

As a solo paper operator (and staging reviewer), I can engage kill-switch levels L1–L4 with clear semantics: L1 pauses new entries; higher levels escalate protection (confirm/SoD rules as documented); status is always visible; dangerous resumes require explicit confirmation. Staging can exercise L1–L4 without live capital.

**Why this priority**: First unchecked item on Phase 1 → `prod-paper` gate; constitution requires L1–L4 respect for dangerous actions.

**Independent Test**: Contract + Gateway + FE show level; L1 still blocks entries; L2+ engage/disengage paths are tested in staging/dev with confirm rules; no flatten against a real exchange required in this feature (paper/internal matcher OK).

**Acceptance Scenarios**:

1. **Given** contracts expose kill-switch level (additive), **When** operator engages L1, **Then** new paper entries are blocked and status shows level L1 engaged.
2. **Given** operator requests L2+ engage, **When** confirm/SoD rules are not satisfied, **Then** the action is rejected and audited (no silent escalate).
3. **Given** L1–L4 states in staging/dev, **When** reviewer runs the feature quickstart kill-switch section, **Then** each level’s engage path is demonstrable without live capital.

---

### User Story 2 - Reconciliation job + mismatch alerts (Priority: P1)

As the operator, the system periodically (or on-demand in paper) reconciles internal ledger fills/positions against the paper adapter view and raises alerts when they diverge — so paper books stay trustworthy before claiming `prod-paper`.

**Why this priority**: Second `prod-paper` gate item; prevents silent ledger drift after E2E demo.

**Independent Test**: Seed a deliberate ledger/adapter mismatch; reconciliation emits an alert with code/message (no secrets); matched books produce no critical mismatch alert.

**Acceptance Scenarios**:

1. **Given** ledger and paper adapter agree, **When** reconciliation runs, **Then** result is OK (or info-only) and no critical mismatch alert.
2. **Given** a forced mismatch (test hook or fixture), **When** reconciliation runs, **Then** an alert is created with a stable code (e.g. `RECON_MISMATCH`) and non-secret detail.
3. **Given** an alert exists, **When** operator opens alerts UI, **Then** they see the reconciliation alert via existing `getAlerts` contract.

---

### User Story 3 - Secrets hygiene + paper-ops criteria tracking (Priority: P2)

As Owner/operator, I have a machine-checkable secrets hygiene gate (no secrets in repo paths that CI already covers) and a paper-ops checklist/tracker for ≥30-day paper criteria (documentation + counters/runbook — not a calendar wait inside CI).

**Why this priority**: Completes remaining `prod-paper` checklist items without pretending CI can “wait 30 days”.

**Independent Test**: `validate_governance` / gitleaks config still PASS; paper-ops tracker doc + optional metrics endpoint or docs checklist exist and are linked from release-gates.

**Acceptance Scenarios**:

1. **Given** repo governance scripts, **When** secrets validators run, **Then** RESULT PASS (or fail on intentional secret fixture only in tests).
2. **Given** paper-ops criteria (Phần 08 condensed), **When** operator opens the tracker, **Then** they see required days/criteria and current recorded progress fields (manual or stubbed counters).

---

### Edge Cases

- L4/flatten requested while only internal paper matcher exists → safe paper cancel/flatten stub; MUST NOT claim live exchange flatten.
- Reconciliation while risk/kill-switch engaged → still runs read-only; does not place orders.
- Resume from L2+ without confirm → reject fail-closed.
- Missing additive contract fields → stop → RFC → update OpenAPI before BE/FE code.
- Attempt to open live capital / Deferred → out of scope for this feature.

## Requirements *(mandatory)*

### Constitution Constraints *(trading platform)*

MUST follow `.specify/memory/constitution.md`: contract-first, fail-closed risk, no secrets, BE/FE lane ownership. **Paper/staging only** — not Phase 2 `prod-live`.

### Functional Requirements

- **FR-001**: System MUST represent kill-switch levels L1–L4 in public contracts (additive OpenAPI) before BE/FE implement level semantics.
- **FR-002**: L1 MUST continue to block new paper entries when engaged (preserve 002 behavior).
- **FR-003**: L2+ engage/resume MUST enforce confirm and documented SoD rules; reject when unmet; audit with `trace_id`.
- **FR-004**: Staging/dev MUST be able to demonstrate L1–L4 engage paths without live capital (paper/internal matcher acceptable for flatten semantics).
- **FR-005**: System MUST provide a reconciliation path (job and/or authenticated trigger) comparing ledger vs paper adapter positions/fills.
- **FR-006**: Reconciliation mismatches MUST create operator-visible alerts via existing alerts contract (additive alert codes OK if schema allows; new fields → RFC).
- **FR-007**: Reconciliation and kill-switch paths MUST NOT log secrets.
- **FR-008**: Secrets hygiene MUST remain enforced by existing governance/gitleaks tooling; this feature documents the `prod-paper` checkbox linkage.
- **FR-009**: Paper-ops ≥30-day criteria MUST be tracked via runbook/checklist (and optional counters) linked from `docs/shared/release-gates.md` — CI MUST NOT fake calendar completion.
- **FR-010**: Frontend MUST consume only Gateway contracts; display kill-switch level and recon alerts; MUST NOT invent client risk truth.
- **FR-011**: MUST NOT implement Deferred matrix items, live capital, or Phase 2 chaos/pen-test full suite (queued separately).

### Key Entities

- **KillSwitchState**: level (L1–L4), engaged, reason, updated_at, updated_by, audit metadata.
- **ReconciliationRun**: id, started_at, finished_at, status (ok|mismatch|error), summary counts, `trace_id`.
- **ReconciliationDiff**: symbol/position/fill discrepancy fields (non-secret).
- **Alert**: existing entity; codes include recon/kill-switch related codes.
- **PaperOpsTracker**: checklist progress toward ≥30-day paper criteria (docs ± lightweight store).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Quickstart demonstrates L1–L4 engage paths on staging/dev paper without live capital.
- **SC-002**: Forced mismatch produces a visible `RECON_*` alert within one reconciliation run.
- **SC-003**: `validate_governance` PASS after any contract changes; Gateway tests cover L1 block + L2+ reject-without-confirm + recon mismatch alert.
- **SC-004**: `docs/shared/release-gates.md` Phase 1 checklist items for kill-switch L1–L4, reconciliation, secrets, and paper-ops tracker are updated to reflect implementable/done vs operator calendar remaining.
- **SC-005**: No Deferred / live-capital scope lands in this feature’s tasks.
