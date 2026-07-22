# AGENTS.md — Luật thực thi cho mọi AI trong repo

Bạn là agent coding trong monorepo Bot Auto-Trade AI. **Không đoán. Không tiện tay. Không nhảy cóc phase.**

## Thứ tự đọc bắt buộc (trước khi sửa code)

1. `.specify/memory/constitution.md`
2. File này (`AGENTS.md`)
3. `docs/shared/mvp-capability-matrix.md` (+ YAML)
4. Chỉ các **task ID được giao** trong `specs/<feature>/tasks.md` (hiện tại: `specs/001-mvp-feature-scope/tasks.md`)
5. `packages/contracts/` (OpenAPI / events / RBAC / WS)
6. HANDOFF của lane:
   - Backend → `BE_Bot_Auto_Trade_AI_Tu_Hoc/docs/HANDOFF-AI.md`
   - Frontend → `FE_Bot_Auto_Trade_AI_Tu_Hoc/docs/HANDOFF-AI.md`
7. Blueprint `docs/architecture/...` **chỉ khi** task trỏ rõ section

## Cấm tuyệt đối

- Invent path/field REST/WS/event không có trong `packages/contracts` (thiếu → dừng → RFC)
- Sửa folder lane kia (`BE_*` ↔ `FE_*`)
- Implement mục **Deferred** trong matrix (AI retrain/canary, no-code builder, multi-user SaaS, MT5-first, DL primary) nếu Owner chưa mở scope
- Commit secret (`.env` thật, key, token, private key)
- FE: P&L/risk math client làm nguồn sự thật; nối Kafka/DB trực tiếp
- Tự làm task ngoài danh sách được assign; “tiện tay” làm T014+ khi chỉ được T001–T013
- Đọc blueprint rồi tự build cả Phase 1–4

## Bắt buộc

- Contract-first: RFC (nếu breaking) → cập nhật contracts → rồi mới code
- Fail-closed cho entry khi risk không sẵn sàng (constitution II)
- Chỉ làm **In-MVP** trừ khi Owner amend matrix
- Validate: `scripts/validate-contracts.ps1` (hoặc `.sh`) trước khi tuyên bố API sẵn sàng
- Xong task được giao → **dừng** và báo cáo; không tự mở feature mới

## Ownership thư mục

| Lane | Được sửa | Không được sửa |
|---|---|---|
| Backend AI | `BE_Bot_Auto_Trade_AI_Tu_Hoc/` | `FE_Bot_Auto_Trade_AI_Tu_Hoc/` |
| Frontend AI | `FE_Bot_Auto_Trade_AI_Tu_Hoc/` | `BE_Bot_Auto_Trade_AI_Tu_Hoc/` |
| Shared (RFC) | `packages/contracts`, `docs/shared` | Implement trước khi RFC duyệt |

## Ưu tiên hiện tại (001-mvp-feature-scope)

1. Tôn trọng matrix đã publish (`docs/shared/mvp-capability-matrix.md`) — T001–T013 **done**
2. Chỉ làm tiếp khi Owner giao rõ (T014+ hoặc feature mới) — không tự implement trading E2E
3. Speckit: specify → plan → tasks → implement → converge — không nhảy cóc 

## Khi không chắc

**Dừng và hỏi Owner.** Không suy đoán remote, branch, secret, path API, hay phạm vi Deferred.
