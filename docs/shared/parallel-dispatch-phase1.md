# Parallel Dispatch — Phase 1 Paper Stub (BE ∥ FE)

**Status:** Ready for Owner-activated dispatch  
**Assignment ids:** `P1-BE-PAPER-STUB` · `P1-FE-PAPER-STUB` (see `agent-assignment.yaml`)  
**Scope:** Chỉ **In-MVP**. Cấm Deferred (AI retrain/promote, no-code, multi-user SaaS, MT5-first, DL-primary).  
**Mức độ:** Stub/contract-aligned paper UI+API — **không** broker E2E thật (`TRADING-E2E` vẫn blocked).

---

## 0. Luật dispatch (bắt buộc cho parent Cursor agent)

Trước khi spawn subagent:

1. Đọc `.specify/memory/constitution.md` → `AGENTS.md` → matrix → **file này** → `agent-assignment.yaml`.
2. Chỉ spawn task có `wave` đã mở (dependency `depends_on` = done hoặc `none`).
3. Mỗi subagent nhận **đúng 1 task id** (hoặc 1 wave-lane bundle nếu ghi rõ).
4. Prompt subagent **MUST** gồm:
   - `lane`, `allowed_paths`, `forbidden_paths`
   - `contract_refs` (operationId) — **không invent** field/path
   - DoD checklist
   - “Xong → dừng; không làm task khác”
5. Song song tối đa: **1 BE + 1 FE** cùng wave (không 2 BE đụng cùng file).
6. Sau mỗi wave: chạy `.\scripts\validate-contracts.ps1` (PASS) trước khi mở wave kế.
7. Thiếu shape OpenAPI → **dừng** → RFC — không đoán.

### Cấm tuyệt đối (nhắc lại)

| Cấm | Lý do |
|---|---|
| Sửa folder lane kia | Path policy / HANDOFF |
| Implement Deferred / `postModelPromote` | `x-mvp: false` |
| FE tính P&L/risk làm truth | Constitution + HANDOFF |
| FE nối Kafka/DB | Gateway-only |
| Broker live / withdraw keys | Paper stub only |
| Đọc blueprint rồi tự mở Phase 3–4 | INDEX + banner |

---

## 1. Waves (thứ tự mở)

```text
Wave 0  [done]  Contracts + governance (không spawn)
Wave 1  ∥       Foundation: Gateway routes shell + FE API client/auth shell
Wave 2  ∥       Auth
Wave 3  ∥       Accounts + API keys (masked)
Wave 4  ∥       Strategies simple start/stop (form, không no-code)
Wave 5  ∥       Market symbols/candles + stale UX
Wave 6  ∥       Positions + PnL (server truth) + activity/trades list
Wave 7  ∥       Kill-switch L1 always visible + alerts inbox
Wave 8  ∥       History/reports polish + BE fail-closed guard docs→code hook
Wave 9  [gate]  Parent: smoke checklist paper-day; STOP (chưa TRADING-E2E)
```

---

## 2. Bảng BE (chỉ `BE_Bot_Auto_Trade_AI_Tu_Hoc/`)

| Task ID | Wave | Matrix | Contract refs | Việc làm | DoD | Depends |
|---|---|---|---|---|---|---|
| **P1-BE-01** | 1 | — | `getHealth`, `getReady` | Gateway: đảm bảo `/health` `/ready` ổn; cấu trúc router sẵn cho `/v1/*` | pytest health PASS; không đổi contracts | none |
| **P1-BE-02** | 2 | `operator-auth` | `postAuthLogin`, `postAuthRefresh`, `postAuthLogout` | Implement stub theo OpenAPI (dev paper user OK); Error shape chuẩn; 501→200 stub có kiểm soát | OpenAPI paths tồn tại + response khớp schema; không log password | P1-BE-01 |
| **P1-BE-03** | 3 | `broker-credentials` | `postAccounts`, `postAccountApiKeys` | Lưu stub vault/in-memory; response **masked** only; cấm log secret | Masked key only; không full secret trong response/log | P1-BE-02 |
| **P1-BE-04** | 4 | `simple-strategy-run` | `getStrategies`, `postStrategies`, `patchStrategy` | CRUD stub + status draft/active/paused/stopped; **không** worker exchange thật | Status transitions theo schema; 501→stub OK | P1-BE-02 |
| **P1-BE-05** | 5 | `paper-market-visibility` | `getMarketSymbols`, `getMarketCandles` | Fixture/symbols + candles stub (hoặc paper feed mock); đánh dấu stale nếu không live | Schema OK; header/field stale nếu có trong contract/docs | P1-BE-01 |
| **P1-BE-06** | 6 | `positions-pnl`, `activity-list`, `history-review` | `getPositions`, `getPnlSummary`, `getReportsTrades` | Stub ledger/read models; PnL **chỉ server** | Ba GET khớp schema; empty list hợp lệ | P1-BE-04 |
| **P1-BE-07** | 7 | `emergency-pause`, `basic-alerts` | `getKillSwitchStatus`, `postKillSwitch`, `getAlerts` | L1 engage/disengage stub + audit log; alerts list stub | L1 đổi state được; không implement L4 flatten thật | P1-BE-02 |
| **P1-BE-08** | 8 | `fail-closed-entries` | docs-only | Trong Risk path: nếu risk unavailable → reject entry (hook/guard); unit test | Test fail-closed PASS; không fail-open | P1-BE-04, P1-BE-07 |

**BE allowed_paths:** `BE_Bot_Auto_Trade_AI_Tu_Hoc/**`  
**BE forbidden:** `FE_Bot_Auto_Trade_AI_Tu_Hoc/**`, Deferred modules as product features, invent OpenAPI fields

---

## 3. Bảng FE (chỉ `FE_Bot_Auto_Trade_AI_Tu_Hoc/`)

| Task ID | Wave | Matrix | Contract refs | Việc làm | DoD | Depends |
|---|---|---|---|---|---|---|
| **P1-FE-01** | 1 | — | (consume OpenAPI) | API client typed từ contracts; env `.env.example`; không hardcode path lạ | Client chỉ gọi operation đã có; 501/Error UX chung | none |
| **P1-FE-02** | 2 | `operator-auth` | `postAuthLogin`, `postAuthRefresh`, `postAuthLogout` | Login page + token storage an toàn; logout | Login flow UI; không lộ refresh token trên UI | P1-FE-01 |
| **P1-FE-03** | 3 | `broker-credentials` | `postAccounts`, `postAccountApiKeys` | Accounts form; mask sau save; không re-display full key | Khớp `docs/screens/account-api-keys.md` | P1-FE-02 |
| **P1-FE-04** | 4 | `simple-strategy-run` | `getStrategies`, `postStrategies`, `patchStrategy` | Form strategy đơn giản start/stop — **không** no-code builder | Khớp HANDOFF; `/models` không quảng cáo promote live | P1-FE-02 |
| **P1-FE-05** | 5 | `paper-market-visibility` | `getMarketSymbols`, `getMarketCandles` | Symbols + candles/status; **stale** banner khi lỗi/gap | Không bịa nến khi API fail | P1-FE-01 |
| **P1-FE-06** | 6 | `positions-pnl`, `activity-list` | `getPositions`, `getPnlSummary`, `getReportsTrades` | Dashboard positions/PnL + activity — display only | Không tính PnL client làm truth | P1-FE-02 |
| **P1-FE-07** | 7 | `emergency-pause`, `basic-alerts` | `getKillSwitchStatus`, `postKillSwitch`, `getAlerts` | `KillSwitchBar` L1 luôn visible; alerts page/inbox | L1 không bị ẩn trong menu; confirm trước mutate | P1-FE-02 |
| **P1-FE-08** | 8 | `history-review` | `getReportsTrades` | Reports/history filter + copy/export summary | Stub 501 → empty/error rõ | P1-FE-06 |

**FE allowed_paths:** `FE_Bot_Auto_Trade_AI_Tu_Hoc/**`  
**FE forbidden:** `BE_Bot_Auto_Trade_AI_Tu_Hoc/**`, Kafka/DB, invent fields, Deferred screens as “live MVP”

---

## 4. Map song song (parent spawn cùng lúc)

| Wave | Spawn BE | Spawn FE | Ghi chú |
|---|---|---|---|
| 1 | P1-BE-01 | P1-FE-01 | Song song an toàn |
| 2 | P1-BE-02 | P1-FE-02 | FE có thể mock/tolerate 501 đến khi BE xong cùng wave |
| 3 | P1-BE-03 | P1-FE-03 | Safety-critical credentials |
| 4 | P1-BE-04 | P1-FE-04 | Không no-code |
| 5 | P1-BE-05 | P1-FE-05 | Stale UX bắt buộc FE |
| 6 | P1-BE-06 | P1-FE-06 | Server PnL truth |
| 7 | P1-BE-07 | P1-FE-07 | L1 always visible |
| 8 | P1-BE-08 | P1-FE-08 | BE fail-closed + FE history |
| 9 | — | — | Parent only: checklist dưới |

---

## 5. Prompt mẫu subagent (copy)

### Backend

```text
Lane: backend. Assignment: P1-BE-PAPER-STUB. Task: <P1-BE-0X>.
Read order: constitution → AGENTS.md → docs/shared/mvp-capability-matrix.md →
docs/shared/parallel-dispatch-phase1.md → BE_Bot_.../docs/HANDOFF-AI.md →
packages/contracts/openapi/openapi.yaml (only listed operationIds).
Allowed: BE_Bot_Auto_Trade_AI_Tu_Hoc/ only.
Forbidden: FE tree; Deferred; invent API; live broker; commit secrets.
Implement ONLY task <P1-BE-0X> DoD. Prefer 501→schema-valid stub over guessing.
Run relevant unit tests. Then STOP and report files changed + DoD checklist.
```

### Frontend

```text
Lane: frontend. Assignment: P1-FE-PAPER-STUB. Task: <P1-FE-0X>.
Read order: constitution → AGENTS.md → docs/shared/mvp-capability-matrix.md →
docs/shared/parallel-dispatch-phase1.md → FE_Bot_.../docs/HANDOFF-AI.md →
packages/contracts/openapi/openapi.yaml (only listed operationIds).
Allowed: FE_Bot_Auto_Trade_AI_Tu_Hoc/ only.
Forbidden: BE tree; client PnL truth; Kafka/DB; Deferred as live; invent fields.
Implement ONLY task <P1-FE-0X> DoD. Handle 401/501/Error model. Then STOP and report.
```

---

## 6. Wave 9 — Paper-day smoke (parent, không spawn trading E2E)

Checklist (manual/script nhẹ):

1. Connect: login → create account → masked api key  
2. Configure & run: create strategy → patch status  
3. Monitor: symbols/candles (stale OK) → positions/pnl → activity  
4. Pause: L1 kill-switch visible + works  
5. Review: reports/trades list  
6. `validate-contracts.ps1` PASS  

**STOP.** Không mở `TRADING-E2E` trừ Owner amend assignment.

---

## 7. Deferred — không bao giờ vào queue này

- `ai-auto-retrain-promote` / `postModelPromote`
- `no-code-builder`
- `multi-user-saas`
- `mt5-forex-adapter`
- `deep-learning-primary`
