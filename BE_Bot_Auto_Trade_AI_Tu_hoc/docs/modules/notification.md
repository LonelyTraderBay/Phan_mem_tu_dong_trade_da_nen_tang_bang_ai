# Notification Service

**Blueprint:** Phần 03 Notification; Phần 11 SEV taxonomy.

## Responsibility

Route alerts by SEV to email / Telegram / push / page. Events: large fills, drawdown, model rollback, recon break, dual-control pending.

## Phase

Core Trading Phase 1 (basic); full paging Phase 2+.

## Interfaces

- In: domain events / alert rules  
- Out: external channels; FE alerts inbox via Gateway  
- Must not block trading path (async)

## Fail-closed notes

Notification outage ≠ open risk path. SEV1 must have escalation path tested in game-day.
