# AGENTS.md — Luật thực thi cho mọi AI trong repo

Bạn là agent coding trong monorepo Bot Auto-Trade AI. **Không đoán. Không tiện tay. Không nhảy cóc phase.**

Governance được **ép bằng máy**: `scripts/validate_governance.py` + CI `.github/workflows/governance.yml` phải PASS.

## Thứ tự đọc bắt buộc (trước khi sửa code)

1. `.specify/memory/constitution.md`
2. File này (`AGENTS.md`)
3. `docs/shared/mvp-capability-matrix.md` (+ YAML)
4. `docs/shared/agent-assignment.yaml` — chỉ assignment `status: active` mà Owner **gọi tên**
5. Chỉ các **task ID được giao** trong `specs/<feature>/tasks.md`
6. `packages/contracts/` (OpenAPI / events / RBAC / WS) — thiếu shape → dừng → RFC
7. HANDOFF của lane:
   - Backend → `BE_Bot_Auto_Trade_AI_Tu_Hoc/docs/HANDOFF-AI.md`
   - Frontend → `FE_Bot_Auto_Trade_AI_Tu_Hoc/docs/HANDOFF-AI.md`
8. Blueprint `docs/architecture/...` **chỉ khi** task trỏ rõ section

## Cấm tuyệt đối

- Invent path/field REST/WS/event không có trong `packages/contracts`
- Sửa folder lane kia (`BE_*` ↔ `FE_*`) trong cùng thay đổi product code (CI path policy)
- Implement mục **Deferred** trong matrix nếu Owner chưa amend bằng văn bản
- Commit secret (`.env` thật, key, token, private key)
- FE: P&L/risk math client làm nguồn sự thật; nối Kafka/DB trực tiếp
- Tự làm task/`assignment` ngoài danh sách active được Owner giao
- Đọc blueprint rồi tự build cả Phase 1–4
- Coi `validate-contracts` PASS cũ là đủ nếu chưa chạy lại sau khi sửa contracts

## Bắt buộc

- Contract-first: thiếu contract → RFC/Owner approve → cập nhật `packages/contracts` → rồi mới code
- Breaking: major `VERSION` + RFC + migration
- Fail-closed cho entry khi risk không sẵn sàng (constitution II)
- Chỉ làm **In-MVP** trừ khi Owner amend matrix
- Trước khi tuyên bố sẵn sàng: `.\scripts\validate-contracts.ps1` (gọi governance validator) → **RESULT: PASS**
- Xong việc được giao → **dừng** và báo cáo

## Ownership thư mục

| Lane | Được sửa | Không được sửa |
|---|---|---|
| Backend AI | `BE_Bot_Auto_Trade_AI_Tu_Hoc/` | `FE_Bot_Auto_Trade_AI_Tu_Hoc/` |
| Frontend AI | `FE_Bot_Auto_Trade_AI_Tu_Hoc/` | `BE_Bot_Auto_Trade_AI_Tu_Hoc/` |
| Shared (RFC) | `packages/contracts`, `docs/shared`, scripts/CI/rules | Implement trading trước khi RFC/assignment mở |

## Ưu tiên hiện tại

1. Tôn trọng matrix + OpenAPI MVP (`x-mvp: true`); Deferred vẫn cấm
2. `TRADING-E2E` (002 paper E2E) = **done** — không reopen trừ Owner
3. `P1-*-PAPER-STUB` = **done**
4. Việc mới: Owner mở Speckit feature + assignment `active` mới (vd. live capital / Phase 2)
5. Speckit: specify → plan → tasks → implement → converge — không nhảy cóc
6. Không live capital / Phase 4 SaaS trừ Owner amend matrix + assignment mới

## Khi không chắc

**Dừng và hỏi Owner.** Không suy đoán remote, branch, secret, path API, hay phạm vi Deferred.
