# HANDOFF — Frontend AI

## Allowed write paths

- `FE_Bot_Auto_Trade_AI_Tu_Hoc/` (toàn bộ: `web/`, `docs/`)

## Forbidden

- `BE_Bot_Auto_Trade_AI_Tu_Hoc/`
- Đoán field REST/WS không có trong `packages/contracts`
- P&L / risk math phía client làm nguồn sự thật
- Nối Kafka/Event Bus hoặc DB trực tiếp

## Source of truth

| Concern | Location |
|---|---|
| REST client | Generate từ `packages/contracts/openapi/openapi.yaml` |
| WS | `packages/contracts/ws/` |
| Errors | `docs/shared/error-model.md` |
| Roles / SoD UX | `docs/shared/auth-rbac-sod.md` |

## Working rules

1. Mọi traffic qua Gateway (`NEXT_PUBLIC_API_URL` / `NEXT_PUBLIC_WS_URL`).  
2. Hiện **stale** khi feed/gap; không bịa nến/fill.  
3. Kill-switch L3/L4: confirm + step-up.  
4. Dual-control: proposer ≠ approver trên UI.  
5. Stub `501` từ BE là OK — UI bám schema.  
6. Validate: `scripts/validate-contracts.ps1`.

## Parallel BE

BE chỉ làm trong `BE_Bot_Auto_Trade_AI_Tu_Hoc/`. Phối hợp qua contracts + RFC.
