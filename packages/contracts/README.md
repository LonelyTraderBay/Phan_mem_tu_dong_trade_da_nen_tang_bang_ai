# packages/contracts

**Source of truth** for API, events, RBAC, and WebSocket protocol.

| Consumer | Role |
|---|---|
| **Frontend (`FE_Bot_Auto_Trade_AI_Tu_Hoc/`)** | Chỉ consume — REST OpenAPI, realtime `ws/`, permissions `rbac/` |
| **Backend (`BE_Bot_Auto_Trade_AI_Tu_Hoc/`)** | Implement — không invent shape khác cho public surface |

## Layout

| Path | Purpose |
|---|---|
| `VERSION` | Semver (hiện `0.3.0` — phải khớp `openapi.info.version`) |
| `openapi/openapi.yaml` | HTTP API (OpenAPI 3.0.3) — MVP ops có `x-mvp: true` |
| `events/` | Event-bus JSON Schema |
| `rbac/roles.yaml` | Roles, permissions, dual-control (SoD) |
| `ws/` | WebSocket protocol |

## Validation

```powershell
.\scripts\validate-contracts.ps1
```

Phải in `RESULT: PASS`. Script kiểm matrix `contract_refs` → `operationId`, VERSION sync, rules, CODEOWNERS, assignment manifest.

## RFC process

Mọi thay đổi **public contract** (kể cả additive path/field):

1. Dừng coding BE/FE.  
2. RFC (hoặc PR contracts được Owner approve) tại [`docs/shared/rfcs/`](../../docs/shared/rfcs/).  
3. Land `packages/contracts` trước.  
4. Breaking → major `VERSION` + dual-publish / deprecation.  
5. Safety/auth/kill-switch → thêm Risk/Security sign-off trên RFC.

Không merge code BE/FE lệch contracts. `postModelPromote` là stub Deferred (`x-mvp: false`) — không implement Phase 1.
