# HANDOFF — Backend AI

## Allowed write paths

- `BE_Bot_Auto_Trade_AI_Tu_Hoc/` (toàn bộ: `services/`, `infra/`, `docs/`)

## Forbidden

- `FE_Bot_Auto_Trade_AI_Tu_Hoc/`
- Commit secrets (`.env` có key thật, token, private key)
- Implement REST/WS/event **chưa** có trong `packages/contracts` (mở RFC trước)
- Implement mục **Deferred** trong [MVP matrix](../../docs/shared/mvp-capability-matrix.md) nếu Owner chưa mở scope bằng văn bản
- Tự làm task ngoài danh sách được assign; tiện tay làm trading E2E khi chỉ được giao docs/matrix

## Source of truth

| Concern | Location |
|---|---|
| Phạm vi Phase 1 | [docs/shared/mvp-capability-matrix.md](../../docs/shared/mvp-capability-matrix.md) |
| Agent laws | [AGENTS.md](../../AGENTS.md) · constitution |
| REST | `packages/contracts/openapi/openapi.yaml` |
| Events | `packages/contracts/events/*.schema.json` |
| RBAC / SoD | `packages/contracts/rbac/` + `docs/shared/auth-rbac-sod.md` |
| WS (Gateway) | `packages/contracts/ws/` |
| Architecture | `docs/architecture/` (chỉ khi task trỏ section) |
| Việc được giao | `specs/**/tasks.md` — chỉ task ID được assign |

## Working rules

1. Contract-first: RFC → update contracts → rồi mới code.  
2. Hot path Strategy → Risk → OMS: sync, timeout, **fail-closed** (`fail-closed-entries` là In-MVP).  
3. Modular-monolith Phase 1 (ADR-02): giữ ranh giới module.  
4. Không đưa credential sàn thật vào skeleton.  
5. `/health` + `/ready` trước business logic.  
6. Validate: `scripts/validate-contracts.ps1` (hoặc `.sh`).  
7. Both-items: xem bảng contract prerequisites trong MVP matrix trước khi code.  
8. Xong task được giao → **dừng** và báo cáo.

## Parallel FE

FE chỉ làm trong `FE_Bot_Auto_Trade_AI_Tu_Hoc/`. Phối hợp qua contracts + Owner merge RFC + matrix.
