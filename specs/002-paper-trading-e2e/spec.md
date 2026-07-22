# Feature Specification: Paper Trading E2E

**Feature Branch**: `002-paper-trading-e2e`

**Created**: 2026-07-22

**Status**: Implemented

**Input**: User description: "đi tiếp Speckit feature + bật TRADING-E2E" — implement end-to-end paper trading on In-MVP capabilities after Phase-1 stubs, without Deferred scope (no live capital, no multi-user SaaS, no AI auto-promote, no no-code builder, no MT5-first).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Connect paper venue and place a guarded paper order path (Priority: P1)

As a solo paper operator, I connect a crypto paper/testnet venue with masked credentials, start a simple strategy, and the system can generate a signal that passes Risk (with `risk_check_id`) into OMS and a paper adapter so I see a real paper fill/position update — not only empty stubs.

**Why this priority**: Without a real paper order path, Wave 1–8 stubs cannot prove capital-safety wiring or operator value.

**Independent Test**: With paper credentials and risk available, activate a simple strategy and observe at least one paper order lifecycle event (accepted/filled or explicitly risk-rejected) with positions/P&L updated from server truth.

**Acceptance Scenarios**:

1. **Given** a logged-in operator with a paper account and masked API key saved, **When** they create and activate a simple strategy for an allowed symbol, **Then** the backend runs Strategy→Risk→OMS (sync) and does not place an order without a recorded risk check.
2. **Given** risk dependency is unavailable, **When** the strategy would enter, **Then** new entries are rejected fail-closed and the UI shows a clear non-success state (no invented fill).
3. **Given** a successful paper fill path, **When** the operator opens positions/P&L and activity, **Then** values come from server/ledger APIs (not client-calculated truth).

---

### User Story 2 - Emergency pause stops new paper entries (Priority: P1)

As the operator, I can always trigger L1 emergency pause so no new paper entries are accepted while paused, and I can see paused state clearly.

**Why this priority**: Mandatory safety for any paper-day that can send orders.

**Independent Test**: Engage L1 during an active strategy; subsequent entry attempts are blocked; status APIs/UI show engaged.

**Acceptance Scenarios**:

1. **Given** an active strategy capable of entries, **When** the operator engages L1 kill-switch, **Then** new entries are not accepted until disengaged (per product rules).
2. **Given** L1 is engaged, **When** the operator views any monitoring surface, **Then** the pause control/state remains visible (not buried).

---

### User Story 3 - Operator completes a paper-day review loop (Priority: P2)

As the operator, after paper activity I can review trade/activity history, alerts, and export/copy a summary for personal records.

**Why this priority**: Completes the paper happy path after connect→run→pause.

**Independent Test**: With prior paper activity (or seeded paper events), reports/alerts screens show server data; export/copy works without revealing secrets.

**Acceptance Scenarios**:

1. **Given** paper trades/events exist, **When** the operator filters today’s history, **Then** they see server-provided rows and can copy/export a summary.
2. **Given** an alert was raised (e.g. risk reject / kill-switch), **When** the operator opens alerts, **Then** they see non-secret, actionable messages.

---

### Edge Cases

- Paper venue/API credentials invalid or withdraw-capable warning ignored → connection/test fails closed; no silent “connected live”.
- Market data stale/gap → UI shows stale; system does not invent candles/fills.
- Duplicate client order / retry → no double paper order (idempotency / UNKNOWN handling per constitution intent).
- Operator logs out → tokens cleared; subsequent API calls unauthorized.
- Attempt to use Deferred capabilities (no-code, AI promote, MT5-first, multi-user) → not offered as live MVP paths.

## Requirements *(mandatory)*

### Constitution Constraints *(trading platform)*

Specs that touch orders, risk, credentials, or model promote MUST NOT contradict
`.specify/memory/constitution.md`: contract-first (`packages/contracts`),
fail-closed risk, no secrets in artifacts, and lane ownership
(`BE_Bot_Auto_Trade_AI_Tu_Hoc` vs `FE_Bot_Auto_Trade_AI_Tu_Hoc`).
This feature is **paper/testnet only** — not live capital Phase 2+.

### Functional Requirements

- **FR-001**: System MUST authenticate the solo paper operator before account or trading actions.
- **FR-002**: System MUST accept paper venue credentials, store them securely, and return only masked key material to the client after save.
- **FR-003**: System MUST support configure/start/stop (status transitions) for a simple form-based strategy (not a no-code builder).
- **FR-004**: System MUST provide paper market visibility (symbols/candles or feed status) and surface stale/unavailable states honestly.
- **FR-005**: System MUST execute the paper entry path as Strategy → Risk → OMS → paper adapter with synchronous risk check and a recorded `risk_check_id` before any venue submit.
- **FR-006**: System MUST fail closed on new entries when Risk (or required dependency for the check) is unavailable.
- **FR-007**: System MUST expose L1 emergency pause that blocks new entries and remains operator-visible.
- **FR-008**: System MUST expose server-truth positions, P&L summary, and trade/activity reports for the paper account.
- **FR-009**: System MUST emit/retain correlatable `trace_id` (and order client ids where applicable) on trading/risk decisions; MUST NOT log secrets.
- **FR-010**: Frontend MUST consume only Gateway REST/WS contracts; MUST NOT treat client-side P&L/risk math as authoritative; MUST NOT connect to Kafka/DB.
- **FR-011**: System MUST NOT implement Deferred MVP-matrix items in this feature: AI auto-retrain/promote, no-code builder, multi-user SaaS, MT5-first adapter, deep-learning-primary signal.
- **FR-012**: Public API/event shapes used by this feature MUST exist in `packages/contracts` before BE/FE implementation of new fields; additive gaps require RFC/Owner approve.

### Key Entities

- **PaperAccount**: Operator’s paper venue account linkage (exchange, market type, testnet flag, masked credentials metadata).
- **SimpleStrategy**: Form-configured strategy bound to an account/symbol/timeframe with status draft|active|paused|stopped.
- **RiskCheck**: Recorded allow/deny decision with id referenced by downstream order attempt.
- **PaperOrder / Fill**: Paper venue order lifecycle outcome used to update positions and reports.
- **KillSwitchState**: L1 engaged flag + reason/audit metadata.
- **Alert**: Operator-visible operational/safety notification without secrets.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A trained operator can complete connect → activate simple strategy → observe paper order/risk outcome → engage L1 pause in under 15 minutes on a prepared paper environment.
- **SC-002**: 100% of paper entry attempts while risk is marked unavailable are rejected (zero silent entries).
- **SC-003**: 100% of successful paper fills shown in UI match server positions/P&L/report APIs (no client-invented fills).
- **SC-004**: L1 pause is reachable from the primary monitoring layout without navigating more than one secondary screen.
- **SC-005**: Reviewer can confirm no Deferred matrix ids were delivered as “live MVP” in this feature’s acceptance demo.
- **SC-006**: `scripts/validate-contracts` / governance validation PASS on the integration branch before claiming API readiness for the feature.

## Assumptions

- Primary market remains crypto paper/testnet (matrix `crypto_paper`); solo operator profile.
- Phase-1 stub Gateway/FE from assignment `P1-*-PAPER-STUB` are the starting codebase; this feature replaces stub gaps with paper-real behavior where In-MVP requires it.
- Paper adapter may use exchange testnet or an internal paper matching simulator if external keys are unavailable in CI — behavior must still exercise Risk→OMS gates.
- Live capital, production withdraw-enabled keys, and Phase 4 multi-user are out of scope.
- Existing OpenAPI MVP operations (`x-mvp: true`) are the default contract surface; only additive RFC’d fields are allowed when gaps appear.
