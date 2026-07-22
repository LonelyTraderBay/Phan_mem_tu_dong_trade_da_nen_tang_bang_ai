# Research: MVP Feature Scope Optimization

## Decision: Feature intent = scope governance, not ML tuning

**Rationale**: User request followed scaffold + constitution; “tối ưu hóa tính năng”
maps to cutting Phase 1 surface for parallel BE/FE delivery (spec assumptions).

**Alternatives considered**:
- Optimize strategy/ML hyperparameters — rejected for this feature id; would need a
  new spec focused on model performance.
- Implement full paper trading stack inside this feature alone — too large; matrix
  unlocks incremental implement features/tasks.

## Decision: Publish matrix as Markdown (human) + YAML (machine)

**Rationale**: Stakeholders need readable table (SC-001); lanes/CI need parseable
status/owner fields. YAML example validated against JSON Schema in feature
`contracts/`.

**Alternatives considered**:
- Markdown only — hard to validate lane coverage automatically.
- Database UI for scope — overkill for Phase 1, violates YAGNI.

## Decision: Canonical published copy under `docs/shared/`

**Rationale**: Both HANDOFF lanes already read `docs/shared`; feature `specs/`
keeps working copy + schema. After approval, matrix is copied/linked to
`docs/shared/mvp-capability-matrix.md` (+ yaml).

**Alternatives considered**:
- Only inside `specs/` — FE/BE AIs may miss it.
- Duplicate full matrix in BE and FE docs — drift risk.

## Decision: Tag OpenAPI operations with `x-mvp: true|false` (additive)

**Rationale**: Contract-first constitution; existing OpenAPI already has `x-phase`.
Additive extension avoids breaking consumers; validate-contracts can later assert
In-MVP paths exist.

**Alternatives considered**:
- Separate MVP OpenAPI file — duplicate maintenance.
- Remove Deferred paths from OpenAPI — breaks forward planning and FE stubs.

## Decision: Default first market = crypto paper; MT5/equities Deferred

**Rationale**: Spec FR-008; crypto adapters are simplest for Linux-friendly paper
paths; MT5 has ADR-03 infrastructure cost.

**Alternatives considered**:
- MT5-first — higher infra coupling for MVP.
- Multi-venue MVP — expands adapter surface beyond parallel-lane capacity.

## Decision: No new microservice for “scope service”

**Rationale**: Constitution phase discipline / YAGNI; matrix is git-managed
governance, not a runtime dependency of order path.

**Alternatives considered**:
- Runtime feature-flag service — unnecessary until multi-env promote needs it.
