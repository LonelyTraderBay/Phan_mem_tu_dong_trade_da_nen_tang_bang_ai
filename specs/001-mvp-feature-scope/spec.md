# Feature Specification: MVP Feature Scope Optimization

**Feature Branch**: `001-mvp-feature-scope`

**Created**: 2026-07-22

**Status**: Planned

**Input**: User description: "sử dụng skill này để tối ưu hóa tính năng"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - See only must-have capabilities for first paper run (Priority: P1)

As the product owner / operator, I need a clear, prioritized list of
capabilities that belong in the first paper-trading release so the team (and
two parallel AI lanes) does not build the entire enterprise surface at once.

**Why this priority**: Without a cut scope, Backend and Frontend will diverge,
duplicate work, or stall on Phase 3–4 features before paper trading works.

**Independent Test**: A reviewer can mark each blueprint capability as
In-MVP / Deferred and confirm that executing only In-MVP still yields a
demonstrable paper-trading loop (configure → monitor → emergency stop →
history).

**Acceptance Scenarios**:

1. **Given** the full enterprise capability catalog, **When** the MVP scope
   list is published, **Then** every capability is labeled In-MVP or Deferred
   with a one-line reason.
2. **Given** only In-MVP capabilities, **When** an operator walks the happy
   path on paper trading, **Then** they can connect a demo account, run one
   simple strategy, see positions/P&L, and trigger an emergency pause without
   needing AI retrain, multi-user SaaS, or advanced builders.
3. **Given** a Deferred capability, **When** either lane proposes to implement
   it in the current phase, **Then** the proposal is rejected unless the owner
   explicitly expands MVP scope in writing.

---

### User Story 2 - Parallel lanes know who builds what first (Priority: P1)

As Backend and Frontend contributors working in parallel, I need each In-MVP
capability assigned to a lane (Backend-only, Frontend-only, or Both with a
shared contract touch) so work does not block or collide.

**Why this priority**: The monorepo is already split; feature optimization must
preserve parallel delivery.

**Independent Test**: For every In-MVP item, a table shows lane ownership and
whether a shared contract change is required before coding.

**Acceptance Scenarios**:

1. **Given** the In-MVP list, **When** lanes start work, **Then** no In-MVP
   item is left without a lane owner.
2. **Given** an item marked Both, **When** work starts, **Then** the shared
   contract touch is listed as a prerequisite before UI or server coding.
3. **Given** Frontend work, **When** Backend has not finished a Both item,
   **Then** Frontend can still progress against agreed stubs/placeholders
   without inventing new public behaviors outside the shared contracts.

---

### User Story 3 - Operator can complete a paper-trading day safely (Priority: P2)

As a solo operator (own capital / paper account), I need the MVP feature set to
cover a full safe day: sign in, attach account credentials safely, start/stop a
bot, watch live status, pause new entries in an emergency, and review what
happened.

**Why this priority**: Scope cut must still deliver operator value; safety
controls cannot be deferred out of MVP.

**Independent Test**: In a scripted paper session, the operator completes the
day without missing a mandatory safety control (emergency pause visible;
credentials never shown in full after save).

**Acceptance Scenarios**:

1. **Given** a paper account is connected, **When** the operator starts a
   simple strategy, **Then** they see running status and recent activity within
   one minute of starting.
2. **Given** open or pending activity, **When** the operator triggers emergency
   pause of new entries, **Then** no new entries are allowed and the UI shows
   the paused state clearly.
3. **Given** a completed paper session, **When** the operator opens history,
   **Then** they can filter today’s trades/events and export or copy a summary
   for personal records.

---

### User Story 4 - Explicitly park advanced AI & SaaS until later (Priority: P3)

As the product owner, I need advanced self-learning, canary promote, no-code
strategy builder, and third-party multi-user SaaS marked Deferred so legal and
model-risk gates are not skipped.

**Why this priority**: Prevents “scope creep” that violates phase discipline and
legal gates.

**Independent Test**: Deferred list includes AI auto-retrain/promote, no-code
builder, and multi-user SaaS with references to later phase criteria.

**Acceptance Scenarios**:

1. **Given** the Deferred list, **When** stakeholders review Phase 1 goals,
   **Then** they acknowledge AI auto-retrain and multi-user SaaS are out of
   MVP.
2. **Given** a request to add multi-user management of others’ capital,
   **When** MVP scope is checked, **Then** the request is blocked pending
   legal sign-off for a later phase.

### Edge Cases

- What if the operator wants MT5/forex in MVP instead of the default first
  market? Scope must be re-approved before expanding adapters.
- What if a “nice-to-have” UI screen is built with no Backend counterpart?
  It must remain clearly stubbed and not claim live success states.
- What if paper broker APIs are unavailable? Operator must see a clear
  failure/paused state, not silent fake fills.
- What if emergency pause is triggered during a partial fill? MVP must still
  stop new entries; existing positions remain manageable under stated rules.

## Requirements *(mandatory)*

### Constitution Constraints *(trading platform)*

Specs that touch orders, risk, credentials, or model promote MUST NOT contradict
`.specify/memory/constitution.md`: contract-first (`packages/contracts`),
fail-closed risk, no secrets in artifacts, and lane ownership
(`BE_Bot_Auto_Trade_AI_Tu_Hoc` vs `FE_Bot_Auto_Trade_AI_Tu_Hoc`).
Mark unresolved safety/legal items as NEEDS CLARIFICATION — do not assume live
capital or multi-user SaaS without explicit scope.

### Functional Requirements

- **FR-001**: Product MUST publish an MVP capability matrix classifying each
  major capability as In-MVP or Deferred with a short rationale.
- **FR-002**: In-MVP MUST include: operator authentication; secure broker
  credential entry (masked after save); simple strategy configure/start/stop;
  paper market data visibility; position and P&L visibility; order/activity
  list; emergency pause of new entries; basic alerts; trade/history review.
- **FR-003**: In-MVP MUST enforce that no new paper entry proceeds when risk
  checks are unavailable (fail-closed for entries).
- **FR-004**: In-MVP MUST keep emergency pause control reachable from the main
  monitoring experience without hunting through nested menus.
- **FR-005**: Deferred MUST include at least: automatic model retrain & promote
  canary; no-code drag-drop strategy builder; multi-user / third-party capital
  management SaaS; deep learning models as primary signal source.
- **FR-006**: Each In-MVP capability MUST be assigned lane ownership
  (Backend, Frontend, or Both) and note whether a shared-contract update is
  required first.
- **FR-007**: MVP MUST target a single operator using paper/demo trading only
  (own capital profile); live capital rollout remains a later gated phase.
- **FR-008**: MVP MUST target one primary market venue family first (default:
  crypto demo/paper via a supported exchange adapter path); additional venue
  families (MT5/forex, equities) are Deferred unless the owner expands scope.
- **FR-009**: Frontend MUST NOT present invented fill/P&L as live truth when
  Backend data is missing or stale; stale/unavailable MUST be visible.
- **FR-010**: Credential values MUST NEVER be displayed in full after initial
  save; withdraw-capable permissions MUST be discouraged in operator guidance.
- **FR-011**: Out of scope for this feature: changing the enterprise blueprint
  risk limit numbers themselves; rewriting folder ownership; implementing the
  full multi-phase AI loop.

### Key Entities

- **Capability**: A named product ability (e.g., Emergency Pause, Paper
  Strategy Run) with status In-MVP/Deferred, lane owner, and rationale.
- **Operator**: Single human user of the MVP paper system.
- **Paper Account**: Demo/paper brokerage connection used for MVP validation.
- **Simple Strategy**: Minimal configurable bot definition sufficient to run
  paper entries under risk rules (not a no-code builder).
- **Emergency Pause**: Operator action that blocks new entries while leaving
  existing risk controls for open exposure intact per stated MVP rules.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A new contributor can identify In-MVP vs Deferred for 100% of
  listed major capabilities in under 15 minutes using only the published
  matrix.
- **SC-002**: Two parallel lanes can start the first In-MVP slice the same day
  without blocking on Deferred AI/SaaS work.
- **SC-003**: In a scripted paper session, an operator completes
  connect → run → pause → review in under 30 minutes on the first attempt
  (excluding external broker signup time).
- **SC-004**: Zero In-MVP acceptance scenarios require multi-user tenancy or
  automatic model promote to pass.
- **SC-005**: At least 90% of Deferred items map to a later phase label
  (Phase 2/3/4) so stakeholders see when they return.

## Assumptions

- “Tối ưu hóa tính năng” in this request means **optimize and cut scope for
  Phase 1 paper-trading MVP**, not ML hyperparameter tuning or production
  performance tuning.
- Legal profile for MVP is self-operated paper/demo (hồ sơ tự doanh / tool for
  self), not managing third-party capital.
- Primary first market is crypto paper/demo; MT5 and equities follow after MVP
  proof.
- Skeleton monorepo, shared contracts, and constitution v1.0.0 already exist and
  remain authoritative for ownership and safety.
- Simple rule-based or baseline signal strategy is enough for MVP; champion/
  challenger auto-retrain is Deferred.
- Success is measured on paper trading quality and delivery clarity, not live
  PnL.
