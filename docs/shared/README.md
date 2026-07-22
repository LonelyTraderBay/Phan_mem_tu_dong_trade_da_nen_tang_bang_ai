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
| [parallel-dispatch-phase1.md](./parallel-dispatch-phase1.md) | Bảng giao BE∥FE phase đầu (In-MVP stubs) |
| [parallel-dispatch-phase1.yaml](./parallel-dispatch-phase1.yaml) | Dispatch máy cho Cursor/subagent |
| [api-overview.md](./api-overview.md) | REST / WS / events split |
| [auth-rbac-sod.md](./auth-rbac-sod.md) | Roles + dual-control |
| [error-model.md](./error-model.md) | Error JSON schema |
| [websocket-protocol.md](./websocket-protocol.md) | WS summary → contracts |
| [environments.md](./environments.md) | dev → prod-live |
| [release-gates.md](./release-gates.md) | Phase checklists |
| [glossary.md](./glossary.md) | Key terms |
| [rfcs/RFC-0001-template.md](./rfcs/RFC-0001-template.md) | RFC template |
