# Feature Specification: Prod-Live Chaos Docs

**Feature Branch**: `006-prod-live-chaos-docs`

**Created**: 2026-07-22

**Status**: Implemented

**Input**: Owner `Active PROD-LIVE-PREP — scope: chaos checklist docs only` — expand Phase-2 chaos checklist documentation only; no live capital code; no Deferred.

## User Scenarios & Testing

### User Story 1 - Operator/SRE has a fillable chaos table (Priority: P1)

As Owner/SRE preparing for Phase 2, I can open a shared chaos checklist that expands the release-gates minimums into inject → expect → evidence → sign-off rows.

**Independent Test**: Doc exists, linked from release-gates and shared README; six minimum scenarios present; scope callout says docs-only.

**Acceptance Scenarios**:

1. **Given** release-gates Phase 2 chaos item, **When** reader follows the link, **Then** they reach `docs/shared/chaos-checklist.md` with the six minimums.
2. **Given** this assignment scope, **When** reviewing the PR/diff, **Then** there is no live-trading product code / no Deferred matrix implement.

## Requirements

- **FR-001**: MUST publish `docs/shared/chaos-checklist.md` covering C-01…C-06 from release-gates chaos minimums.
- **FR-002**: MUST link checklist from `release-gates.md` and `docs/shared/README.md`.
- **FR-003**: MUST state Owner scope docs-only and that Pass ticks require human evidence.
- **FR-004**: MUST NOT implement live capital, chaos automation, or Deferred features in this feature.

## Success Criteria

- **SC-001**: Checklist + links landed; assignment closed as docs-complete for this scope.
- **SC-002**: `PROD-LIVE-PREP` notes record remaining Phase-2 gates still open.
