# Feature Specification: Phase-2 Remaining Gates Docs Pack

**Feature Branch**: `007-phase2-remaining-gates-docs`

**Created**: 2026-07-22

**Status**: Implemented

**Input**: Owner — mở pack docs cho toàn bộ mục Phase-2 còn lại (game-day L3, restore, pen-test, capital sizing, on-call). Docs only; no live capital code.

## User Scenarios

### US1 - Owner/SRE có pack checklist điền được (P1)

As Owner/SRE, I open one shared pack covering G-01…G-06 with steps, evidence, and sign-off columns, linked from release-gates.

**Acceptance**:

1. `docs/shared/phase2-remaining-gates.md` exists with G-01…G-06.
2. `release-gates.md` Phase-2 rows link to the pack (and chaos checklist remains separate).
3. Diff contains no live-trading product code.

## Requirements

- **FR-001**: Publish remaining-gates pack for game-day L3, restore T1, pen-test, 03D limits, capital sizing, on-call.
- **FR-002**: Link from release-gates + shared README; cross-link chaos checklist.
- **FR-003**: State docs-only; Pass requires human evidence.
- **FR-004**: MUST NOT implement live capital or Deferred features.

## Success Criteria

- Pack + links landed; assignment notes updated; governance PASS.
