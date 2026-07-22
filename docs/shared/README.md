# Shared docs

Ownership: **Shared (RFC)**. Both BE and FE consume this layer; neither owns unilateral contract changes.

## Rules

1. **Contracts first** — mọi REST path / WS channel / event subject / role / error code **công khai** phải có trong `packages/contracts` *trước* khi BE implement hoặc FE bind.
2. **RFC policy (thống nhất):**
   - **Thiếu path/field công khai (kể cả additive):** dừng coding → RFC ngắn (hoặc PR contracts có Owner approve) → cập nhật contracts → rồi mới code.
   - **Breaking:** major bump `packages/contracts/VERSION` + RFC + migration/dual-publish + Owner (+ Risk/Security nếu safety/auth).
3. FE talks **only** to Gateway (REST + WS). FE never subscribes to the Event Bus.
4. Do not copy blueprint text here — link to [architecture INDEX](../architecture/INDEX.md).
5. AI assignment: [agent-assignment.yaml](./agent-assignment.yaml) — chỉ làm id `status: active` được Owner gọi tên.

## Contents

| Doc | Purpose |
|---|---|
| [mvp-capability-matrix.md](./mvp-capability-matrix.md) | **Phạm vi Phase 1** In-MVP vs Deferred + lane ownership |
| [mvp-capability-matrix.yaml](./mvp-capability-matrix.yaml) | Bản máy của matrix (canonical) |
| [agent-assignment.yaml](./agent-assignment.yaml) | Task/lane được phép cho AI (machine-readable) |
| [parallel-dispatch-phase1.md](./parallel-dispatch-phase1.md) | Bảng giao BE∥FE stubs (baseline, đã done) |
| [parallel-dispatch-phase1.yaml](./parallel-dispatch-phase1.yaml) | Dispatch máy stubs |
| [chaos-checklist.md](./chaos-checklist.md) | Phase-2 chaos minimum table (docs) |
| [phase2-remaining-gates.md](./phase2-remaining-gates.md) | Phase-2 remaining gates pack G-01…G-06 (docs) |
| [prod-live-capital-policy.md](./prod-live-capital-policy.md) | PROD-LIVE ≤5% NAV envelope (fail-closed; no mainnet yet) |
| [phase2-evidence-registry.md](./phase2-evidence-registry.md) | Tooling vs human Pass registry (honest %) |
| [phase2-staging-runbook.md](./phase2-staging-runbook.md) | SRE runbook C-01…C-06 + G-01 + evidence export |
| [phase2-owner-auto-check.md](./phase2-owner-auto-check.md) | Owner 2026-07-23 Phase-2 auto-check / self-attest record |
| [phase2-signoff/](./phase2-signoff/) | Human sign-off templates (G-02…G-06) |
| [../../specs/010-enterprise-staging-evidence/](../../specs/010-enterprise-staging-evidence/) | Evidence export pack — **done** |
| [../../specs/011-enterprise-ci-evidence/](../../specs/011-enterprise-ci-evidence/) | CI evidence job + artifacts — **done** |
| [../../specs/008-phase2-staging-drills/](../../specs/008-phase2-staging-drills/) | Paper staging drills automation — **done** |
| [../../specs/007-phase2-remaining-gates-docs/](../../specs/007-phase2-remaining-gates-docs/) | Remaining gates docs — **done** |
| [../../specs/006-prod-live-chaos-docs/](../../specs/006-prod-live-chaos-docs/) | Prod-live prep — chaos checklist docs — **done (docs scope)** |
| [../../specs/005-paper-ws-realtime/](../../specs/005-paper-ws-realtime/) | Paper WS realtime (ticket + locked channels) — **done** |
| [../../specs/004-binance-testnet-adapter/](../../specs/004-binance-testnet-adapter/) | Binance Spot Testnet adapter — **done** |
| [rfcs/RFC-0003-paper-ws-realtime.md](./rfcs/RFC-0003-paper-ws-realtime.md) | WS ticket + paper channel lock |
| [../../specs/003-prod-paper-harden/](../../specs/003-prod-paper-harden/) | Prod-paper harden (kill-switch L1–L4, recon, ops tracker) — **done** |
| [../../specs/002-paper-trading-e2e/](../../specs/002-paper-trading-e2e/) | Paper trading E2E Speckit feature (**done**) |
| [paper-ops-tracker.md](./paper-ops-tracker.md) | Optional paper ops log (Owner waived ≥30-day Pass gate 2026-07-23) |
| [rfcs/RFC-0002-kill-switch-levels.md](./rfcs/RFC-0002-kill-switch-levels.md) | Additive kill-switch L1–L4 contract |
| [api-overview.md](./api-overview.md) | REST / WS / events split |
| [auth-rbac-sod.md](./auth-rbac-sod.md) | Roles + dual-control |
| [error-model.md](./error-model.md) | Error JSON schema |
| [websocket-protocol.md](./websocket-protocol.md) | WS summary → contracts |
| [environments.md](./environments.md) | dev → prod-live |
| [release-gates.md](./release-gates.md) | Phase checklists |
| [glossary.md](./glossary.md) | Key terms |
| [rfcs/RFC-0001-template.md](./rfcs/RFC-0001-template.md) | RFC template |
