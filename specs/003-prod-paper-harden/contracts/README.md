# Contracts touch — 003-prod-paper-harden

## Required before BE/FE level code

Additive OpenAPI (see `docs/shared/rfcs/RFC-0002-kill-switch-levels.md`):

- `KillSwitchRequest.level` enum `L1|L2|L3|L4`
- `KillSwitchRequest.confirmed` boolean (required semantics for L2+ in implementation; schema may be optional with runtime enforce)
- `KillSwitchStatus.level` nullable enum

## Prefer no new public recon paths in v1 of this feature

- Reconciliation results surface via existing `getAlerts` (`RECON_MISMATCH` / `RECON_ERROR` codes).
- If FE needs a recon status panel later → new RFC + `operationId` before code.

## Out of scope

- Live order create public API
- Deferred matrix ops (`postModelPromote`, etc.)
