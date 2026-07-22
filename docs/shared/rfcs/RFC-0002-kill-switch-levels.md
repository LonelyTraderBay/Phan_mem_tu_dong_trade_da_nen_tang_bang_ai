# RFC-0002: Kill-switch levels L1–L4 (additive)

| | |
|---|---|
| **Status** | Approved (Owner auto-open priority 2026-07-22) |
| **Author** | AI (Owner-directed) |
| **Date** | 2026-07-22 |
| **Approver (Owner)** | Owner — authorize open next priority |

## Summary

Extend kill-switch OpenAPI schemas with additive `level` (L1–L4) and `confirmed` so Phase 1 → `prod-paper` can demonstrate L1–L4 on paper/staging without breaking existing boolean `engaged` clients.

## Motivation

`docs/shared/release-gates.md` requires kill-switch L1–L4 on staging. Current `KillSwitchRequest`/`KillSwitchStatus` only expose `engaged` boolean. Constitution II requires L1–L4 respect for dangerous actions.

## Contract diff

- `packages/contracts/VERSION`: minor bump (0.1.0 → 0.2.0) when schemas land
- OpenAPI schemas: `KillSwitchRequest`, `KillSwitchStatus`
- Events/WS/RBAC: none in this RFC
- SoD: documented runtime rules for L2+; full dual-control IdP deferred to later phase

## Phase

Phase 1 paper/staging (`prod-paper` gate). Not prod-live.

## Change class

- [x] **Additive public** (field mới)
- [ ] **Breaking**
- [ ] **Docs-only**

## Breaking?

- [x] No (additive, same major 0.x; minor VERSION bump)

## Security / safety

- L2+ require `confirmed: true` or reject
- L4 paper flatten is internal matcher only — must not claim live exchange
- No secrets in reason/logs

## Rollout

1. Land OpenAPI + VERSION + validate_governance PASS  
2. BE implement levels + tests  
3. FE show level + confirm UX for L2+  
4. Mark release-gates kill-switch item progress

## Alternatives

Separate URLs per level — rejected (surface churn).
