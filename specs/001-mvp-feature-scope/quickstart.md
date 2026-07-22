# Quickstart: Validate MVP Feature Scope Optimization

## Prerequisites

- Repo root checkout with `specs/001-mvp-feature-scope/` present
- PowerShell available (Windows) or equivalent for validate script
- Optional: Python + PyYAML for schema experiments

## 1. Confirm feature artifacts

From repo root:

```powershell
Test-Path specs\001-mvp-feature-scope\spec.md
Test-Path specs\001-mvp-feature-scope\plan.md
Test-Path specs\001-mvp-feature-scope\research.md
Test-Path specs\001-mvp-feature-scope\data-model.md
Test-Path specs\001-mvp-feature-scope\contracts\mvp-capability-matrix.example.yaml
```

Expected: all `True`.

## 2. Validate platform contracts still pass

```powershell
.\scripts\validate-contracts.ps1
```

Expected: `RESULT: PASS`.

## 3. Review matrix vs acceptance (manual, ~15 min)

Open:

- `specs/001-mvp-feature-scope/contracts/mvp-capability-matrix.example.yaml`
- `specs/001-mvp-feature-scope/spec.md` (FR-002, FR-005, FR-006)

Checks:

1. Every In-MVP capability has `lane` set (`backend` / `frontend` / `both` / `shared`).
2. Deferred items include `ai-auto-retrain-promote`, `no-code-builder`, `multi-user-saas`.
3. `emergency-pause` and `broker-credentials` have `safety_critical: true`.
4. No In-MVP item requires multi-user tenancy.

## 4. Lane parallel smoke (docs-level)

| Lane | Action | Expected |
|---|---|---|
| Shared | Read matrix YAML | Can list In-MVP ids |
| Backend | Open `BE_Bot_Auto_Trade_AI_Tu_Hoc/docs/HANDOFF-AI.md` | Ownership forbids `FE_...` |
| Frontend | Open `FE_Bot_Auto_Trade_AI_Tu_Hoc/docs/HANDOFF-AI.md` | Ownership forbids `BE_...` |

## 5. After publish (post-tasks)

When `docs/shared/mvp-capability-matrix.md` exists, repeat step 3 against that file
as the canonical stakeholder copy.

## Out of scope for this quickstart

- Full paper broker connect / live orders
- Docker compose full stack E2E (belongs to later implement features)
