# AI Inference Service

**Blueprint:** Phần 03 Inference; NFR-04; Phần 05.

## Responsibility

Load champion (and shadow/canary as configured); emit calibrated P(profit &gt; threshold) + explanations; publish `signal.generated`. Monitor live calibration (ECE).

## Phase

AI Service from Phase 2 live AI; CPU baseline (XGBoost/LightGBM).

## Interfaces

- In: Feature Store realtime  
- Out: Event Bus `signal.generated` → Strategy  
- Registry for model load / rollback

## Fail-closed notes

Inference/Registry timeout → no new signals = no new orders. Latency &gt; 50% candle → alert; do not widen canary on bad calibration.
