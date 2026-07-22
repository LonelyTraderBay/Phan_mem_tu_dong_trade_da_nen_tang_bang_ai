# Portfolio & Ledger

**Blueprint:** Phần 03 Portfolio & Ledger; ADR-08; Phần 03C recon.

## Responsibility

Double-entry intent/history ledger; FX to reporting currency (default USD); separate fee legs; realtime P&L for FE. On mismatch, **broker wins** — adjust ledger + audit.

## Phase

Core Trading Phase 1.

## Interfaces

- In: fills, fees, recon jobs  
- Out: positions/P&L APIs + WS; events `position.updated`, `fee.posted`, `reconciliation.break_detected`

## Fail-closed notes

Recon break → auto L2 on account/symbol. Never delete history to “fix” breaks.
