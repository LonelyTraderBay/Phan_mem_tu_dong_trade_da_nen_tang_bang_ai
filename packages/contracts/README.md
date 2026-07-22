# packages/contracts

**Source of truth** for API, events, RBAC, and WebSocket protocol.

| Consumer | Role |
|---|---|
| **Frontend (`FE_Bot_Auto_Trade_AI_Tu_Hoc/`)** | Chỉ consume — REST OpenAPI, realtime `ws/`, permissions `rbac/` |
| **Backend (`BE_Bot_Auto_Trade_AI_Tu_Hoc/`)** | Implement — không invent shape khác cho public surface |

## Layout

| Path | Purpose |
|---|---|
| `VERSION` | Semver (hiện `0.1.0`) |
| `openapi/openapi.yaml` | HTTP API (OpenAPI 3.0.3) |
| `events/` | Event-bus JSON Schema |
| `rbac/roles.yaml` | Roles, permissions, dual-control (SoD) |
| `ws/` | WebSocket protocol |

## RFC process

Đổi contract công khai → RFC tại [`docs/shared/rfcs/`](../../docs/shared/rfcs/).

1. Viết RFC (motivation, before/after, migration).  
2. Review với FE + BE.  
3. Land contract trước, rồi mới code.  
4. Breaking event → major `VERSION` + dual-publish nếu cần.

Không merge code BE/FE lệch contracts khi chưa có RFC được duyệt.
