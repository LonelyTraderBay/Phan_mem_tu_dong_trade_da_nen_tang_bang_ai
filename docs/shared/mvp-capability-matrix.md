# MVP Capability Matrix (canonical)

**Version:** 0.1.0 · **Updated:** 2026-07-22  
**Primary market:** crypto paper · **Operator:** solo paper  
**Machine copy:** [mvp-capability-matrix.yaml](./mvp-capability-matrix.yaml)  
**Schema:** [specs/.../capability-matrix.schema.json](../../specs/001-mvp-feature-scope/contracts/capability-matrix.schema.json)  
**Governance:** `.specify/memory/constitution.md` · Spec `specs/001-mvp-feature-scope/`

Đây là **phạm vi Phase 1 bắt buộc**. AI và contributor **MUST NOT** implement mục Deferred trừ khi Owner mở rộng scope bằng văn bản (xem Amendment rules).

---

## In-MVP

| ID | Name | Lane | Contract touch | Safety | Rationale |
|---|---|---|---|---|---|
| operator-auth | Operator authentication | both | yes | | Required before any account or bot actions |
| broker-credentials | Secure broker credential entry | both | yes | critical | Connect paper account safely |
| simple-strategy-run | Simple strategy configure/start/stop | both | yes | | Core paper loop value |
| paper-market-visibility | Paper market data visibility | both | yes | | Operator needs market context |
| positions-pnl | Positions and P&L visibility | both | yes | | Understand exposure |
| activity-list | Order and activity list | both | yes | | Trace what the bot did |
| emergency-pause | Emergency pause new entries | both | yes | critical | Mandatory safety for MVP day |
| basic-alerts | Basic alerts | both | yes | | Operator awareness |
| history-review | Trade history review | both | yes | | Personal record after paper day |
| fail-closed-entries | Fail-closed when risk unavailable | backend | no (docs) | critical | Constitution capital safety |
| mvp-capability-matrix | Published MVP capability matrix | shared | no (docs) | | Primary deliverable of scope feature |

---

## Deferred (out of Phase 1 MVP)

| ID | Name | Return phase | Safety | Rationale |
|---|---|---|---|---|
| ai-auto-retrain-promote | Automatic model retrain and canary promote | phase-3 | | Model-risk gates; not needed for first paper day |
| no-code-builder | No-code strategy builder | phase-4 | | Form-based simple strategy is enough |
| multi-user-saas | Multi-user third-party capital SaaS | phase-4 | critical | Legal gate; constitution forbids without sign-off |
| mt5-forex-adapter | MT5 forex adapter in MVP | phase-2 | | Crypto paper first (FR-008) |
| deep-learning-primary | Deep learning as primary signal | phase-3 | | Baseline/simple signal enough for paper MVP |

---

## Lane ownership (In-MVP)

### Shared
- `mvp-capability-matrix` — Owner / docs-shared maintainers

### Backend only
- `fail-closed-entries` — enforce in Risk/OMS path (docs until trading implement feature)

### Frontend only
- _(none in v0.1.0 — FE work is via Both items)_

### Both (BE + FE; contract-first)

| ID | BE responsibility | FE responsibility |
|---|---|---|
| operator-auth | Issue/validate tokens, RBAC | Login UI, safe token storage |
| broker-credentials | Vault storage, never log secrets | Masked input, never show full key after save |
| simple-strategy-run | Persist config, start/stop workers | Forms, status display |
| paper-market-visibility | Market data via adapter/gateway | Charts/status; show stale |
| positions-pnl | Compute from ledger (server truth) | Display only; no client P&L as truth |
| activity-list | Query orders/events | Lists/filters |
| emergency-pause | Execute L1 pause; audit | Always-visible control; confirm higher levels later |
| basic-alerts | Alert rules/API | Inbox / toast |
| history-review | Reports API | History UI + export/copy |

---

## Contract prerequisites (Both items — trước khi code)

Các mục `contract_touch: true` **MUST** có shape trong `packages/contracts` (hoặc RFC) trước khi BE implement / FE bind UI:

| Capability | contract_refs (operation targets) |
|---|---|
| operator-auth | `postAuthLogin`, `postAuthRefresh`, `postAuthLogout` |
| broker-credentials | `postAccounts`, `postAccountApiKeys` |
| simple-strategy-run | `getStrategies`, `postStrategies`, `patchStrategy` |
| paper-market-visibility | `getMarketSymbols`, `getMarketCandles` |
| positions-pnl | `getPositions`, `getPnlSummary` |
| activity-list | `getReportsTrades` |
| emergency-pause | `getKillSwitchStatus`, `postKillSwitch` |
| basic-alerts | `getAlerts` |
| history-review | `getReportsTrades` |

Nếu thiếu path/field: **dừng coding** → RFC trong `docs/shared/rfcs/` → cập nhật contracts → rồi mới code.

Docs-only (không cần OpenAPI mới cho MVP matrix):
- `fail-closed-entries` → `docs-only:risk-fail-closed`
- `mvp-capability-matrix` → `docs-only:mvp-matrix`

---

## Amendment rules

1. **Binding:** Matrix này + YAML đồng bộ là nguồn phạm vi Phase 1.
2. **Deferred → In-MVP:** Chỉ khi Owner ghi nhận bằng văn bản (PR comment / RFC / issue được approve) kèm lý do và cập nhật `version` semver của matrix.
3. **In-MVP → Deferred:** Cần Owner approve (có thể làm hẹp scope khẩn).
4. **Cấm:** AI tự thêm capability In-MVP hoặc implement Deferred vì “có trong blueprint”.
5. **Đồng bộ:** Mọi sửa Markdown **MUST** cập nhật `mvp-capability-matrix.yaml` (và example trong specs nếu còn dùng).
6. **Máy ép:** `scripts/validate_governance.py` FAIL nếu `contract_refs` không có trong OpenAPI `operationId`.

---

## Paper-day operator checklist (In-MVP)

Thứ tự tối thiểu cho một ngày paper (FR-002 / US3) — **không** yêu cầu MT5, no-code, hay AI promote:

1. **Connect** — auth (`operator-auth`) → lưu credentials paper đã mask (`broker-credentials`)
2. **Configure & run** — simple strategy start (`simple-strategy-run`) + thấy market (`paper-market-visibility`)
3. **Monitor** — positions/P&L server-truth (`positions-pnl`) + activity (`activity-list`) + alerts (`basic-alerts`)
4. **Pause** — emergency L1 pause luôn sẵn (`emergency-pause`); fail-closed nếu risk down (`fail-closed-entries`)
5. **Review** — history (`history-review`)

Nếu bất kỳ bước nào thiếu contract: **dừng** → RFC → cập nhật OpenAPI.

---

## Reading order for AI agents

1. `.specify/memory/constitution.md`  
2. `AGENTS.md` (repo root)  
3. This matrix + `docs/shared/agent-assignment.yaml`  
4. Only assigned IDs in `specs/.../tasks.md`  
5. `packages/contracts`  
6. Lane HANDOFF  
7. Blueprint — only if a task cites a section  
