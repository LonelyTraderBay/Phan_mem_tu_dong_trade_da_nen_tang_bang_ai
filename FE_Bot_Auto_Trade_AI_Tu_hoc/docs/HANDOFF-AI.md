# HANDOFF — Frontend AI

## Allowed write paths

- `FE_Bot_Auto_Trade_AI_Tu_Hoc/` (toàn bộ: `web/`, `docs/`)

## Forbidden

- `BE_Bot_Auto_Trade_AI_Tu_Hoc/`
- Đoán field REST/WS không có trong `packages/contracts`
- P&L / risk math phía client làm nguồn sự thật
- Nối Kafka/Event Bus hoặc DB trực tiếp
- Implement / quảng cáo UI cho mục **Deferred** (no-code builder, AI Model Center promote, multi-user SaaS, …) như đã live nếu Owner chưa mở scope — xem [MVP matrix](../../docs/shared/mvp-capability-matrix.md)
- Tự làm task ngoài danh sách được assign
- Bỏ qua CI governance (`scripts/validate_governance.py` phải PASS)

## Source of truth

| Concern | Location |
|---|---|
| Phạm vi Phase 1 | [docs/shared/mvp-capability-matrix.md](../../docs/shared/mvp-capability-matrix.md) |
| Assignment | [docs/shared/agent-assignment.yaml](../../docs/shared/agent-assignment.yaml) |
| Agent laws | [AGENTS.md](../../AGENTS.md) · constitution · `.cursor/rules/60-ai-execution.mdc` |
| REST client | Generate từ `packages/contracts/openapi/openapi.yaml` |
| WS | `packages/contracts/ws/` |
| Errors | `docs/shared/error-model.md` |
| Roles / SoD UX | `docs/shared/auth-rbac-sod.md` |
| Việc được giao | `specs/**/tasks.md` — chỉ task ID được assign |

## Working rules

1. Mọi traffic qua Gateway (`NEXT_PUBLIC_API_URL` / `NEXT_PUBLIC_WS_URL`).  
2. Hiện **stale** khi feed/gap; không bịa nến/fill.  
3. Kill-switch: L1 pause In-MVP luôn hiện diện; L3/L4 confirm + step-up.  
4. Dual-control: proposer ≠ approver trên UI.  
5. Stub `501` từ BE là OK — UI bám schema; **không** hiện “đã khớp” khi Backend chưa xác nhận.  
6. Validate: `scripts/validate-contracts.ps1` → phải **PASS**.  
7. Both-items: chờ/đồng bộ `contract_refs` trong matrix trước khi bind cứng UI.  
8. Xong task được giao → **dừng** và báo cáo.

## Parallel BE

BE chỉ làm trong `BE_Bot_Auto_Trade_AI_Tu_Hoc/`. Phối hợp qua contracts + RFC + matrix.
