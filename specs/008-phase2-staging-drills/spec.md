# Feature Specification: Phase-2 Staging Drills

**Feature Branch**: `008-phase2-staging-drills`

**Created**: 2026-07-23

**Status**: Implemented

**Input**: Owner — tiếp tục Phase-2 hướng hoàn thiện. Scope AI: **staging/paper drill automation + evidence registry + sign-off templates**. Không live capital; không tự tick Pass cổng người (pen-test, Risk Officer, on-call thật, capital NAV thật).

## User Stories

### US1 - Automated paper drills for chaos + L3 (P1)

As SRE, I can run pytest staging drills that exercise fail-closed risk, kill-switch confirm/SoD-style reject, L3 cancel timing ≤30s (paper), credentials fail-closed, and related paper behaviors — producing machine evidence in a registry.

### US2 - Human sign-off templates ready (P1)

As Owner/Risk/Security, I have fillable templates for 03D limits, capital sizing, on-call, restore, and pen-test disposition so remaining Pass ticks can be recorded without inventing approvals.

## Requirements

- **FR-001**: pytest suite `test_phase2_staging_drills.py` covering paper-mappable C/G rows.
- **FR-002**: `docs/shared/phase2-evidence-registry.md` records tooling results vs human-pending.
- **FR-003**: Sign-off templates under `docs/shared/phase2-signoff/`.
- **FR-004**: release-gates notes updated; Pass checkboxes remain for human evidence.
- **FR-005**: MUST NOT enable live keys, fake signatures, or Deferred SaaS.

## Success Criteria

- Drills green on paper Gateway; registry honest about % tooling vs % gate Pass; assignment closed.
