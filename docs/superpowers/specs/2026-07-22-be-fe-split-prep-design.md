# Design: Tách tài liệu & scaffold BE/FE song song (Contract-First)

| | |
|---|---|
| **Ngày** | 2026-07-22 |
| **Trạng thái** | Approved + scaffolded; root folders: `BE_Bot_Auto_Trade_AI_Tu_Hoc/` (toàn bộ backend) + `FE_Bot_Auto_Trade_AI_Tu_Hoc/` (toàn bộ frontend); shared: `packages/contracts` + `docs/shared` |
| **Blueprint gốc** | `Kien-truc-Bot-Auto-Trade-AI-v2-Enterprise.md` (v2.1) |
| **Phạm vi** | Full Phase 0–4: docs tách + cây folder theo container + skeleton kỹ thuật tối thiểu — **chưa** business logic |
| **Mục tiêu** | Hai AI (BE / FE) làm song song không đụng folder nhau; khớp lại qua `packages/contracts` |

---

## 1. Quyết định đã chốt

| # | Quyết định | Lựa chọn |
|---|---|---|
| 1 | Phân tách tài liệu / ownership | **A** — Ba phần: shared + backend + frontend |
| 2 | Phạm vi nội dung | **C** — Full blueprint v2.1 (Phase 0–4) |
| 3 | Cây runtime | **C** — Theo container C4 v2.1 (`services/*`, `apps/web`) |
| 4 | Mức chuẩn bị | **C** — Docs + folder + skeleton (`pyproject` / `package.json` / Compose / OpenAPI stub validate được) |
| 5 | Cách triển khai | **Cách 1** — Monorepo Contract-First Hub |

### Ownership song song

| Vai trò | Được sở hữu / sửa | Không được sửa |
|---|---|---|
| AI Frontend | `apps/web`, `docs/frontend` | `services/*`, `infra` |
| AI Backend | `services/*`, `infra`, `docs/backend` | `apps/web` |
| Shared (RFC) | `packages/contracts`, `docs/shared` | Đổi contract bắt buộc RFC + approve trước khi implement |
| Owner (bạn) | Merge RFC, ưu tiên breaking change | Blueprint v2.1 tham chiếu tại `docs/architecture/` |

**Quy tắc cứng:** FE không import code từ `services/*`. BE không commit vào `apps/web`. Mọi path API/WS/event mới phải có trong `packages/contracts` trước khi implement.

### Di trú từ placeholder hiện có

Repo hiện có:

- `BE_Bot_Auto_Trade_AI_Tu_hoc/.gitkeep`
- `FE_Bot_Auto_Trade_AI_Tu_hoc/.gitkeep`

Khi scaffold (bước sau khi spec được user review):

1. Tạo cây mới (`services/`, `apps/web`, `packages/contracts`, `docs/`, `infra/`, `scripts/`).
2. Xóa hai folder placeholder trên (hoặc để lại một sprint rồi xóa) — **không** đặt code nghiệp vụ vào tên cũ.
3. Cập nhật `README.md` root trỏ tới cấu trúc mới và ownership.

---

## 2. Cây thư mục mục tiêu

```
docs/
  architecture/                 # copy/move blueprint v2.1 + INDEX.md
  shared/
    README.md
    api-overview.md
    auth-rbac-sod.md
    error-model.md
    websocket-protocol.md
    environments.md
    release-gates.md
    glossary.md
    rfcs/
      RFC-0001-template.md
  backend/
    README.md
    HANDOFF-AI.md
    modules/
      gateway-auth.md
      adapter-layer.md
      market-data.md
      feature-store.md
      ai-training.md
      ai-inference.md
      model-registry-mrm.md
      strategy-engine.md
      risk-management.md
      oms.md
      portfolio-ledger.md
      backtesting.md
      notification.md
      observability.md
    data-contracts.md           # trỏ packages/contracts
    sre-runbook.md
    security.md
    dr-bcp.md
    roadmap-phases.md
    adrs/                       # ADR-01..09
  frontend/
    README.md
    HANDOFF-AI.md
    screens/                    # 9 màn hình (khớp blueprint C4 / §04)
      dashboard.md
      strategy-builder.md
      ai-model-center.md
      backtest-studio.md
      live-monitor.md
      account-api-keys.md
      alerts.md
      reports.md
      approvals.md
    layout/
      kill-switch.md            # thanh điều khiển chung overlay mọi màn — không đếm vào 9
    state-and-data.md
    ux-rules.md

packages/contracts/
  VERSION
  openapi/openapi.yaml
  events/*.schema.json
  rbac/roles.yaml
  ws/ws-protocol.md
  ws/examples/

services/
  gateway/
  core-trading/                 # submodules: adapter, strategy, risk, oms, ledger, notification
  data/                         # market-data, features, calendar
  ai/                           # training, inference, registry
  backtest/

apps/web/                       # Next.js + TS + Tailwind

infra/
  compose/docker-compose.yml
  vault/README.md
  k8s/.gitkeep

scripts/
  validate-contracts.sh
  validate-contracts.ps1
  generate-fe-client.md
```

---

## 3. Điểm nối hệ thống (contracts)

Năm bề mặt bắt buộc để BE/FE khớp khi ghép:

1. **REST OpenAPI** `/v1/...` — auth, accounts/keys, strategies, market phụ, orders manual (+ `Idempotency-Key`), positions/P&L, kill-switch, approvals, backtests, models, alerts/reports, health.
2. **WebSocket protocol** — channels, resume-from-sequence, stale, auth ticket; chỉ qua Gateway.
3. **RBAC + SoD** — roles + dual-control actions (khớp Phần 03D v2.1).
4. **Event schemas** — BE nội bộ (Kafka); FE **không** subscribe bus.
5. **Error model** — `code`, `message`, `trace_id`, `details[]`.

### OpenAPI groups (đánh dấu `x-phase`)

| Nhóm | Phase tối thiểu |
|---|---|
| Auth, accounts/keys, strategies, market REST, orders manual, positions/P&L, kill-switch, backtest jobs, alerts/reports, health | 1 |
| Approvals (SoD) | 2–3 |
| Models / MRM (retrain, promote) | 2–3 |

Stub được phép trả `501 Not Implemented` cho path nghiệp vụ; schema request/response phải có đủ để FE generate client và BE viết contract test.

### Events (JSON Schema + envelope)

Subjects: `candle.closed`, `signal.generated`, `order.*`, `position.updated`, `fee.posted`, `risk.limit_breached`, `kill_switch.*`, `model.*`, `reconciliation.break_detected`.

Envelope bắt buộc: `trace_id`, `schema_version`, `produced_at_utc`, `producer_service`.

### VERSION + RFC

- Semver trong `packages/contracts/VERSION`.
- Breaking change = major + RFC trong `docs/shared/rfcs/`.
- Flow: draft RFC → owner approve → update contracts → cả hai AI mới implement.

---

## 4. Skeleton kỹ thuật (không business logic)

### Mỗi `services/*`

- `pyproject.toml` (Python ≥3.11)
- `src/<pkg>/` với `/health` + `/ready`
- `tests/test_health.py` smoke
- `README.md` trỏ `docs/backend/modules/...`
- **Không:** logic risk/OMS/ML, kết nối sàn thật, secret thật

### `services/gateway`

- FastAPI app; serve/mount OpenAPI từ `packages/contracts/openapi/openapi.yaml`
- Route nghiệp vụ stub → 501

### `services/core-trading`

- Subpackages rỗng + docstring ranh giới: `adapter`, `strategy`, `risk`, `oms`, `ledger`, `notification`

### `apps/web`

- Next.js + TypeScript + Tailwind
- App Router: 9 màn hình + layout slot kill-switch (overlay mọi màn; không phải route riêng)
- `lib/api/`, `lib/ws/` placeholder
- `.env.example`: `NEXT_PUBLIC_API_URL`, `NEXT_PUBLIC_WS_URL`
- **Không:** chart thật, P&L tính ở client, hard-code risk rules

### Infra

- Compose: `gateway`, `web`, `postgres`, `redis`, `redpanda` (Kafka-compatible)
- `.env.example` root — không commit secret
- Vault/k8s: README / `.gitkeep` cho Phase sau

### Tooling

- `scripts/validate-contracts.(sh|ps1)` — Spectral/OpenAPI + JSON Schema
- Root README: ownership, validate, compose up
- `.gitignore`, `.editorconfig`

---

## 5. Gói việc sau scaffold & DoD chuẩn bị

### Hai làn độc lập (sau khi DoD chuẩn bị pass)

| Làn | Việc được làm | Cấm |
|---|---|---|
| BE-Track | Chi tiết `docs/backend/modules/*`; health thật; Compose wire; migration stub DDL 03B; khung contract test adapter | Sửa `apps/web`; sàn thật; train model |
| FE-Track | Chi tiết `docs/frontend/screens/*` (9 màn) + `layout/kill-switch.md`; shell + kill-switch UI stub; routes IA; auth form mock; client từ OpenAPI | Sửa `services/*`; đoán path ngoài OpenAPI; P&L client-side |

### DoD giai đoạn chuẩn bị (ký trước khi code nghiệp vụ)

- [ ] Spec này đã được user review OK
- [ ] Cây folder + README ownership đủ
- [ ] `validate-contracts` pass trên máy local
- [ ] `docker compose up` → gateway `/health` + web trang chủ
- [ ] OpenAPI đủ nhóm path Mục 3 (501 chấp nhận)
- [ ] Event JSON Schema đủ subjects v2.1
- [ ] `docs/backend/HANDOFF-AI.md` và `docs/frontend/HANDOFF-AI.md` có mặt

### HANDOFF prompt (ý chính)

**BE:** Chỉ làm trong `services/`, `infra/`, `docs/backend/`. Nguồn sự thật API = `packages/contracts`. Không sửa `apps/web`.

**FE:** Chỉ làm trong `apps/web`, `docs/frontend/`. Mọi API/WS khớp contracts. Không sửa `services/`.

---

## 6. Mapping tài liệu từ blueprint v2.1

| Nguồn v2.1 | Đích |
|---|---|
| Toàn bộ file gốc | `docs/architecture/` (tham chiếu) |
| 00 thuật ngữ, 01 FR/NFR chung, 06 giao tiếp, 08 gate chung, 15 | `docs/shared/` |
| 02–03, 03B–D, 05, 07 (BE), 09–14 (BE/SRE/Sec/DR), ADR, phụ lục sequence BE | `docs/backend/` |
| 04, 06 (cột FE), UX kill-switch/approvals | `docs/frontend/` |
| Event/OpenAPI/RBAC/WS | `packages/contracts/` (+ `docs/shared` mô tả) |

Nguyên tắc: **không** để hai AI phải đọc toàn bộ 1300+ dòng mỗi lần — mỗi bên đọc shared + phần của mình; architecture chỉ khi cần ngữ cảnh.

---

## 7. Rủi ro & giảm thiểu

| Rủi ro | Giảm thiểu |
|---|---|
| Hai AI sửa contract đồng thời | RFC bắt buộc; lock văn hóa “contracts trước code” |
| FE đoán field không có trong OpenAPI | HANDOFF cấm; CI validate; review PR |
| BE implement path chưa có trong OpenAPI | Cấm; RFC trước |
| Folder placeholder cũ gây nhầm | Xóa/migrate trong bước scaffold; README cảnh báo |
| Scope creep business logic vào skeleton | DoD chuẩn bị tách bạch; checklist “no business logic” |

---

## 8. Thứ tự thực hiện sau khi user approve spec này

1. **Không** invoke coding nghiệp vụ.
2. Tạo implementation plan ngắn (writing-plans) **hoặc** scaffold trực tiếp theo spec nếu user yêu cầu scaffold ngay.
3. Scaffold: docs tách + folder + skeleton + contracts stub + compose.
4. Chạy validate-contracts + compose smoke.
5. Dừng lại để user ký DoD chuẩn bị; sau đó mới giao 2 AI HANDOFF.

---

## 9. Spec self-review

| Check | Kết quả |
|---|---|
| Placeholder / TBD mơ hồ | Không còn TBD blocking; phase gắn trên OpenAPI groups |
| Mâu thuẫn nội bộ | Ownership, cây folder, contracts thống nhất Cách 1 |
| Scope | Chỉ chuẩn bị (docs+skeleton); không implement trading |
| Nhập nhằng | Placeholder `BE_Bot_*`/`FE_Bot_*` → migrate tường minh |
| Ambiguity FE propose OpenAPI? | Không — FE consume; propose qua RFC, owner merge |

---

**Gate:** User review file spec này. Chỉ khi OK mới scaffold / viết implementation plan chi tiết.
