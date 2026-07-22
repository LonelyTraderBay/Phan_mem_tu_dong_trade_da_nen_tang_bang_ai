# Risk Management

**Blueprint:** Phần 03 Risk; **Phần 03D** (limits + kill-switch + SoD).

## Responsibility

Last defense before venue: numeric limits, calendar/margin/fee inputs, kill-switch L1–L4, dual-control for limit changes and resumes. Persist `risk_checks` (NFR-01).

## Phase

Core Trading Phase 1 — **never** optional or stubbed away in live paths.

## Interfaces

- In: Strategy sync RPC; Gateway kill-switch / limit APIs  
- Out: approve/reject; events `risk.limit_breached`, `kill_switch.*`  
- Emits SEV on auto L2+

## Fail-closed notes

Any dependency needed for check missing → reject order. FE cannot override Risk decisions. Limit change ineffective until SoD approve.
