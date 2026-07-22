<!--
Sync Impact Report
- Version change: (none / template placeholders) → 1.0.0
- Modified principles: [PRINCIPLE_1..5 placeholders] → I–V concrete trading-platform principles
- Added sections: Repository & Ownership Constraints; Development Workflow & Quality Gates
- Removed sections: none (template slots replaced)
- Templates:
  - .specify/templates/plan-template.md ✅ Constitution Check + project structure paths updated
  - .specify/templates/tasks-template.md ✅ Path conventions updated to BE_/FE_ folders
  - .specify/templates/spec-template.md ✅ Safety/contract constraints note added
  - README.md ✅ already aligned with ownership (no further change required this pass)
- Follow-up TODOs: none deferred; project compliance audit summarized in agent reply (prep-phase vs live-trading)
-->

# Bot Auto-Trade AI Constitution

## Core Principles

### I. Contract-First Boundary (NON-NEGOTIABLE)

All public REST, WebSocket, event, and RBAC shapes MUST exist in
`packages/contracts` before implementation in either lane.
Breaking changes MUST bump `packages/contracts/VERSION` (semver) and land an
RFC under `docs/shared/rfcs/` before code merge.
Frontend MUST consume contracts only; Backend MUST implement them — neither MAY
invent alternate public shapes.
Rationale: Two AIs work in parallel; contracts are the only join point that
keeps integrations correct.

### II. Capital Safety & Fail-Closed Risk (NON-NEGOTIABLE)

No order MAY reach an exchange/broker without a recorded risk-check
(`risk_check_id`). Risk and credential dependencies MUST fail closed
(no new orders when Risk, Vault, calendar, or inference required for the
decision path is unavailable).
Strategy → Risk → OMS MUST remain synchronous with explicit timeout.
Kill-switch L1–L4 and dual-control (SoD) rules from the enterprise blueprint
MUST be respected for dangerous actions (limit changes, L2+ resume, L4, promote
above capital thresholds).
Rationale: The system touches real capital; safety beats availability of entries.

### III. Traceability & Audit Integrity

Every trading decision and dual-control action MUST be reconstructible via
`trace_id` / `client_order_id` linkage in logs, events, and audit storage.
Audit streams for trading/risk/approvals MUST be append-only (WORM or
equivalent retention policy) for the retention window in NFR-02/09.
Secrets MUST NEVER appear in logs, commits, or client bundles.
Rationale: Incident response, compliance, and rollback require immutable history.

### IV. Test Discipline & Release Gates

Contract validation (`scripts/validate-contracts.*`) MUST pass before claiming
API readiness. Health endpoints MUST exist for every service skeleton.
Business features that touch orders, risk, or promote MUST include tests
appropriate to their layer (unit for limits/FSM; contract tests for adapters;
chaos/game-day before live capital per blueprint Phần 15).
No user story MAY skip foundational gates defined in the implementation plan
Constitution Check.
Rationale: Undetected regressions in trading systems are capital events.

### V. Observability, Simplicity & Phase Discipline

Services MUST expose `/health` and `/ready`. Production paths MUST support
structured logs and correlation IDs; Phase 3+ MUST meet OpenTelemetry coverage
targets in the blueprint.
Prefer modular-monolith Phase 1 (ADR-02) over premature microservice split.
Do not implement Phase 4 multi-user/SaaS behaviors without legal sign-off
(blueprint hồ sơ pháp lý).
YAGNI for business logic during scaffold: stubs (e.g. HTTP 501) are allowed
until a feature plan passes Constitution Check.
Rationale: Operability and controlled scope prevent enterprise theater.

## Repository & Ownership Constraints

Root MUST keep two primary product folders:

- `BE_Bot_Auto_Trade_AI_Tu_Hoc/` — ALL backend code, infra, and backend docs
- `FE_Bot_Auto_Trade_AI_Tu_Hoc/` — ALL frontend code and frontend docs

Shared (not owned by a single lane):

- `packages/contracts/`
- `docs/architecture/`, `docs/shared/`, `docs/superpowers/`
- `scripts/`

Backend AI MUST NOT edit `FE_Bot_Auto_Trade_AI_Tu_Hoc/`.
Frontend AI MUST NOT edit `BE_Bot_Auto_Trade_AI_Tu_Hoc/`.
Frontend MUST NOT connect to Kafka/DB directly; all traffic via Gateway.
Guidance: `BE_Bot_Auto_Trade_AI_Tu_Hoc/docs/HANDOFF-AI.md`,
`FE_Bot_Auto_Trade_AI_Tu_Hoc/docs/HANDOFF-AI.md`, root `README.md`,
and blueprint `docs/architecture/Kien-truc-Bot-Auto-Trade-AI-v2-Enterprise.md`.

## Development Workflow & Quality Gates

1. Spec → Plan (Constitution Check) → Tasks → Implement.
2. Contract RFC approve → update `packages/contracts` → then BE/FE code.
3. Prep-phase DoD before business logic: validate-contracts PASS; handoffs
   present; compose file present; no secrets in git.
4. Live-capital DoD (Phase 2+): chaos UNKNOWN/retry, game-day L3 ≤30s,
   security review, Risk Officer sign-off on limits — per blueprint Phần 15.
5. PRs MUST verify: ownership paths, contract sync, no plaintext secrets,
   fail-closed behavior for risk-touching changes.

## Governance

This constitution supersedes informal practice when conflicts arise.
Amendments MUST: document motivation, update this file with semver bump,
update dependent Speckit templates if gates change, and record
`Last Amended` date (ISO YYYY-MM-DD).
- MAJOR: remove/redefine non-negotiable principles
- MINOR: add principle/section or materially expand gates
- PATCH: clarifications and non-semantic wording

Compliance review: every `/speckit-plan` run MUST complete Constitution Check;
owners MAY block merge on failed gates.
Runtime guidance: root `README.md` and lane HANDOFF files.

**Version**: 1.0.0 | **Ratified**: 2026-07-22 | **Last Amended**: 2026-07-22
