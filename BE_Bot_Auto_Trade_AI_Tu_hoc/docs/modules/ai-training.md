# AI Training Pipeline

**Blueprint:** Phần 03 Training; Phần 05 loop.

## Responsibility

Offline retrain jobs (schedule or drift). Walk-forward with purge/embargo; Optuna budget (FinOps); push challenger + Model Card to Registry. Isolated from live trading process.

## Phase

AI Service Phase 1 skeleton; full auto-retrain Phase 3.

## Interfaces

- In: Feature Store snapshots, labels with `label_available_at`  
- Out: Model Registry challenger artifacts  
- Triggers: cron, drift, manual (ml_lead)

## Fail-closed notes

Over budget → reject job. Never auto-promote to 100% capital. Training failure must not degrade live Inference/OMS.
