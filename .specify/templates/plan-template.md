# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]

**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command; its definition describes the execution workflow.

## Summary

[Extract from feature spec: primary requirement + technical approach from research]

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: [e.g., Python 3.11, Swift 5.9, Rust 1.75 or NEEDS CLARIFICATION]

**Primary Dependencies**: [e.g., FastAPI, UIKit, LLVM or NEEDS CLARIFICATION]

**Storage**: [if applicable, e.g., PostgreSQL, CoreData, files or N/A]

**Testing**: [e.g., pytest, XCTest, cargo test or NEEDS CLARIFICATION]

**Target Platform**: [e.g., Linux server, iOS 15+, WASM or NEEDS CLARIFICATION]

**Project Type**: [e.g., library/cli/web-service/mobile-app/compiler/desktop-app or NEEDS CLARIFICATION]

**Performance Goals**: [domain-specific, e.g., 1000 req/s, 10k lines/sec, 60 fps or NEEDS CLARIFICATION]

**Constraints**: [domain-specific, e.g., <200ms p95, <100MB memory, offline-capable or NEEDS CLARIFICATION]

**Scale/Scope**: [domain-specific, e.g., 10k users, 1M LOC, 50 screens or NEEDS CLARIFICATION]

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Verify against `.specify/memory/constitution.md` (v1.0.0+):

- [ ] **I. Contract-First**: New/changed public REST/WS/events/RBAC are drafted in
      `packages/contracts` (RFC if breaking); FE will only consume; BE will only implement
- [ ] **II. Capital Safety**: Order/risk paths remain fail-closed; Strategy→Risk→OMS sync;
      no bypass of risk_check / kill-switch / SoD for dangerous actions
- [ ] **III. Traceability**: `trace_id` / `client_order_id` plan present; no secrets in logs/git
- [ ] **IV. Test & Gates**: validate-contracts considered; health/ready for touched services;
      tests named for risk/order/adapter changes when in scope
- [ ] **V. Phase Discipline**: Fits current phase (no Phase 4 multi-user without legal gate);
      no unjustified new top-level service beyond approved tree
- [ ] **Ownership**: Changes confined to `BE_Bot_Auto_Trade_AI_Tu_Hoc/` **or**
      `FE_Bot_Auto_Trade_AI_Tu_Hoc/` (plus shared contracts/docs via RFC as needed)

If any gate fails, resolve or record under Complexity Tracking below.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
BE_Bot_Auto_Trade_AI_Tu_Hoc/
├── services/
│   ├── gateway/
│   ├── core-trading/
│   ├── data/
│   ├── ai/
│   └── backtest/
├── infra/
└── docs/

FE_Bot_Auto_Trade_AI_Tu_Hoc/
├── web/
└── docs/

packages/contracts/
docs/{architecture,shared,superpowers}/
scripts/
```

**Structure Decision**: Monorepo contract-first. Backend work ONLY under
`BE_Bot_Auto_Trade_AI_Tu_Hoc/`; frontend ONLY under `FE_Bot_Auto_Trade_AI_Tu_Hoc/`.
Shared API truth: `packages/contracts`. Delete unused option trees from plans;
do not invent parallel `backend/` / `frontend/` / `apps/` roots.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
