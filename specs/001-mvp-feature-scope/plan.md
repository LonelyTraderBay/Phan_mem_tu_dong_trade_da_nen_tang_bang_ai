# Implementation Plan: MVP Feature Scope Optimization

**Branch**: `001-mvp-feature-scope` | **Date**: 2026-07-22 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/001-mvp-feature-scope/spec.md`

**Note**: This plan is filled by `/speckit-plan`.

## Summary

Publish a binding **MVP capability matrix** (In-MVP vs Deferred) with **lane ownership**
(Backend / Frontend / Both) so two AIs can build Phase 1 paper trading in parallel
without implementing the full enterprise surface. Technical approach: versioned
Markdown + YAML matrix under shared docs/contracts, tag existing OpenAPI paths with
MVP markers, and gate deferred work (AI retrain, SaaS, MT5) out of the current phase.
Operator paper-day capabilities remain In-MVP targets; this feature delivers the
scope control artifacts and alignment hooks that unlock parallel implementation.

## Technical Context

**Language/Version**: Python 3.11+ (BE skeleton), TypeScript 5.x / Node 20 (FE skeleton)

**Primary Dependencies**: Existing monorepo — FastAPI gateway stubs, Next.js app shell,
`packages/contracts` OpenAPI 3.0.3 + event JSON Schema; PyYAML for matrix validation
scripts (optional)

**Storage**: N/A for matrix itself (files in git). Paper-trading persistence remains
PostgreSQL when operator stories are implemented later from this matrix.

**Testing**: `scripts/validate-contracts.ps1`; new check that every In-MVP capability
maps to a contract path or explicit "docs-only" flag; pytest only if matrix schema
parser is added

**Target Platform**: Local monorepo (Windows/Linux); paper trading via Gateway + Web

**Project Type**: Web application (split BE/FE monorepo) + governance artifacts

**Performance Goals**: Matrix reviewable in &lt;15 minutes (SC-001); no runtime SLO
change in this feature

**Constraints**: Constitution v1.0.0 — contract-first, fail-closed entries, no
Phase 4 SaaS, ownership folders fixed; single operator paper/demo; crypto paper first

**Scale/Scope**: One MVP matrix covering major blueprint capabilities; one primary
market family; Deferred list covers Phase 2–4 items

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify against `.specify/memory/constitution.md` (v1.0.0+):

- [x] **I. Contract-First**: Matrix marks which OpenAPI/WS items are In-MVP; no new
      public shapes without `packages/contracts` (+ RFC if breaking)
- [x] **II. Capital Safety**: Emergency pause + fail-closed entries remain In-MVP;
      live capital and risky promote stay Deferred
- [x] **III. Traceability**: Matrix and any contract tags stay in git; no secrets
- [x] **IV. Test & Gates**: validate-contracts remains required; add matrix↔contract
      consistency check in quickstart
- [x] **V. Phase Discipline**: Explicit Deferred for AI auto-retrain, no-code builder,
      multi-user SaaS, MT5/equities (unless owner expands)
- [x] **Ownership**: Docs/matrix in `docs/shared` + feature `specs/`; BE/FE only
      touched for alignment notes/HANDOFF pointers — no cross-lane code in this plan

Post-design re-check: **PASS** (no unjustified violations).

## Project Structure

### Documentation (this feature)

```text
specs/001-mvp-feature-scope/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── capability-matrix.schema.json
│   └── mvp-capability-matrix.example.yaml
└── tasks.md             # /speckit-tasks
```

### Source Code (repository root)

```text
BE_Bot_Auto_Trade_AI_Tu_Hoc/
├── services/
├── infra/
└── docs/

FE_Bot_Auto_Trade_AI_Tu_Hoc/
├── web/
└── docs/

packages/contracts/
docs/{architecture,shared,superpowers}/
scripts/
```

**Structure Decision**: Governance artifacts live in `specs/001-mvp-feature-scope/`
and `docs/shared/` (published matrix). Runtime code stays in existing BE/FE trees;
this feature does not add new top-level services.

## Complexity Tracking

> No constitution violations requiring justification.
