# AI Training Pipeline

> **Out of MVP:** Automatic retrain / canary promote is **Deferred** — matrix ids
> `ai-auto-retrain-promote`, `deep-learning-primary` (phase-3). Do not implement as
> Phase 1 product path. OpenAPI `postModelPromote` has `x-mvp: false`.

**Blueprint:** Phần 03 Training; Phần 05 loop.

## Responsibility

Offline retrain jobs (schedule or drift). Walk-forward with purge/embargo; Optuna budget (FinOps); push challenger + Model Card to Registry. Isolated from live trading process.

## Phase

AI Service Phase 1 skeleton only; full auto-retrain Phase 3.

## Interfaces

- In: Feature Store snapshots, labels with `label_available_at`
- Out: Model Registry challenger artifacts
- Triggers: cron, drift, manual (ml_lead)

## Fail-closed notes

Over budget → reject job. Never auto-promote to 100% capital. Training failure must not degrade live Inference/OMS.
