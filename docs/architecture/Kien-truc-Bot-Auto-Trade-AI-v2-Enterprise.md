# Nền tảng Bot Auto-Trade tích hợp AI tự học & tự huấn luyện lại

**ENTERPRISE ARCHITECTURE BLUEPRINT — ENTERPRISE-GRADE**

Phiên bản v2.1 — hardening từ v2.0: bổ sung Security & Compliance, DR/BCP, Test Strategy & Release Gates, Schema Registry, dual-control/SoD, OpenTelemetry, FinOps, Model Risk Management, và ADR-05..09. Đủ để CTO duyệt ngân sách, Risk Officer ký an toàn vốn, SRE vận hành lúc 3 giờ sáng, và Security/QA chặn go-live khi chưa đạt gate.

|  |  |
|---|---|
| **PHIÊN BẢN** | v2.1 — xem lịch sử phiên bản ở Phần 00 |
| **PHẠM VI** | Enterprise Architecture Blueprint — quyết định kiến trúc & gate vận hành; chi tiết cấp code thuộc design/spec theo module |
| **THỊ TRƯỜNG** | Áp dụng cho crypto / forex (MT5) / chứng khoán |
| **TRẠNG THÁI** | Bản hiện hành — chờ phê duyệt (CTO + Risk Officer + SRE Lead) |
| **LƯU Ý** | Không phải lời khuyên đầu tư, tài chính, hay pháp lý chính thức |

## Mục lục

- **00** — Metadata & Quản trị tài liệu
- **01** — Tổng quan & yêu cầu hệ thống (FR/NFR)
- **02** — Kiến trúc tổng thể
- **03** — Backend chi tiết theo module
- **03B** — Mô hình dữ liệu & Data Contracts
- **03C** — Vòng đời lệnh & Máy trạng thái
- **03D** — Phân cấp giới hạn rủi ro & Kill-Switch
- **04** — Frontend chi tiết theo màn hình
- **05** — Vòng lặp AI “tự học và làm lại” & Model Risk Management
- **06** — Bảng phân chia Backend / Frontend theo tính năng
- **07** — Tech stack đề xuất
- **08** — Lộ trình phát triển theo giai đoạn
- **09** — Rủi ro, bảo mật & pháp lý (Risk Register)
- **10** — Kết nối đa nền tảng & tích hợp MT5
- **11** — Vận hành & SRE Runbook
- **12** — Nhật ký quyết định kiến trúc (ADR Log)
- **13** — Security & Compliance Controls
- **14** — Disaster Recovery & Business Continuity (DR/BCP)
- **15** — Test Strategy & Release Gates
- **A** — Phụ lục — Sơ đồ C4 & Sequence

---

## 00. Metadata & Quản trị tài liệu

### Lịch sử phiên bản

| Phiên bản | Ngày | Thay đổi chính | Trạng thái |
|---|---|---|---|
| v1.0 | — | Bản kiến trúc đầu tiên: 13 module BE, 8 màn hình FE, vòng lặp AI 9 bước, bảng phân chia BE/FE. | Đã thay thế |
| v1.1 | — | Bổ sung Exchange/Broker Adapter Layer, Phần 10 (kết nối đa nền tảng & MT5). | Đã thay thế |
| v2.0 | — | Nâng cấp enterprise-grade: máy trạng thái, data contract, giới hạn rủi ro có số, kill-switch, ADR log, risk register, SRE runbook. | Đã thay thế |
| v2.1 | 2026-07-22 | Enterprise Hardening: Phần 13–15 (Security, DR/BCP, QA Gates); Schema Registry & events thiếu; SoD/dual-control; OTel; FinOps; MRM; ADR-05..09; siết NFR/error budget. | Bản hiện hành — chờ phê duyệt |

### Quy trình phê duyệt tài liệu

| Vai trò | Phạm vi phê duyệt | Bắt buộc trước |
|---|---|---|
| CTO / Kiến trúc sư trưởng | Toàn bộ blueprint + ADR | Giai đoạn 0 exit |
| Risk Officer | Phần 03D, 05 (gate promote), 09, 14 (RPO vốn) | Phase 2 live capital |
| SRE Lead | Phần 11, 14, 15 (chaos/game-day) | Phase 2 live capital |
| Security Lead (hoặc CTO nếu đội nhỏ) | Phần 13 | Phase 2 live capital |
| Cố vấn pháp lý | Phần 09 hồ sơ (b)/(c) | Trước onboard user thứ ba |

Mọi thay đổi material sau khi đã phê duyệt phải tạo phiên bản mới (v2.2+), ghi diff trong lịch sử, và lấy lại sign-off của chủ sở hữu hạng mục bị ảnh hưởng.

### Chủ sở hữu quyết định

| Hạng mục quyết định | Chủ sở hữu |
|---|---|
| Kiến trúc hệ thống & ADR | CTO / Kiến trúc sư trưởng |
| Giới hạn rủi ro & kill-switch | Risk Officer (hoặc Founder ở giai đoạn đội nhỏ) |
| Thay đổi risk limit / resume L2+ | Dual-control: đề xuất (Operator) + phê duyệt (Risk Officer) — Phần 03D |
| Phê duyệt promote model (champion → production) | ML Lead (+ Risk Officer nếu canary >10% vốn) |
| Pháp lý & tuân thủ (đặc biệt Giai đoạn 4 — SaaS) | Cố vấn pháp lý |
| Ứng phó sự cố (SEV1/SEV2) | SRE / On-call lead |
| Security control & secret policy | Security Lead / CTO |
| Lựa chọn sàn/broker & review ToS | Người phụ trách vận hành giao dịch |
| Ngân sách hạ tầng / FinOps | CTO + Founder |

### Thuật ngữ

| Thuật ngữ | Giải thích |
|---|---|
| Champion / Challenger | Model đang chạy production (champion) và model ứng viên đang được kiểm định để thay thế (challenger). |
| Shadow trading | Challenger chạy song song với dữ liệu live nhưng không đặt lệnh thật. |
| Canary rollout | Cấp một phần vốn nhỏ cho model/chiến lược mới, tăng dần nếu ổn định. |
| Drift (PSI / KS-test) | Độ lệch phân phối dữ liệu hiện tại so với dữ liệu lúc train; PSI và KS-test là hai phép đo phổ biến. |
| Sharpe / Sortino | Chỉ số lợi nhuận điều chỉnh theo rủi ro (Sortino chỉ tính rủi ro giảm giá). |
| PSR / DSR | Probabilistic / Deflated Sharpe Ratio — kiểm định Sharpe có hiệu chỉnh theo số lần thử nghiệm, chống overfitting khi so sánh nhiều model. |
| Idempotency | Gửi lại cùng một yêu cầu nhiều lần chỉ tạo ra đúng một hiệu lực — tránh đặt lệnh trùng. |
| Circuit breaker / Kill-switch | Cơ chế tự động (hoặc thủ công) ngắt một phần hoặc toàn bộ hoạt động giao dịch khi vượt ngưỡng rủi ro. |
| Reconciliation break | Sai lệch giữa dữ liệu nội bộ (ledger) và dữ liệu thực tế từ sàn/broker. |
| Walk-forward | Phương pháp kiểm định model theo thời gian: train trên quá khứ, test trên giai đoạn kế tiếp, trượt dần về sau. |
| Slippage | Chênh lệch giữa giá dự kiến và giá khớp thực tế của lệnh. |
| SLO / SLI | Service Level Objective / Indicator — mục tiêu và chỉ số đo mức độ vận hành của một service. |
| Error budget | Phần “được phép lỗi” còn lại trong chu kỳ SLO; hết budget → đóng băng thay đổi rủi ro cao. |
| FMEA | Failure Mode and Effects Analysis — bảng phân tích các kiểu lỗi, hệ quả và cách ứng phó. |
| RPO / RTO | Recovery Point/Time Objective — lượng dữ liệu tối đa được phép mất / thời gian tối đa để khôi phục sau sự cố. |
| SoD / Dual-control | Segregation of Duties — người đề xuất không đồng thời là người phê duyệt hành động nguy hiểm. |
| Schema Registry | Kho đăng ký schema sự kiện; chặn producer gửi payload không tương thích. |
| WORM | Write Once Read Many — lưu trữ audit không cho sửa/xoá trong retention window. |
| MRM | Model Risk Management — quản trị rủi ro model (card, owner, review, calibration). |
| SBOM | Software Bill of Materials — danh mục thành phần phần mềm để quét CVE. |
| Game-day | Buổi diễn tập có kiểm soát các kịch bản sự cố (kill-switch, DR) trên staging. |

---

## 01. Tổng quan & yêu cầu hệ thống

Hệ thống cần giải quyết bốn bài toán lớn: (1) lấy và xử lý dữ liệu thị trường liên tục trên nhiều nền tảng, (2) ra quyết định giao dịch dựa trên mô hình AI kết hợp luật quản trị rủi ro, (3) thực thi lệnh an toàn trên sàn/broker, và (4) khiến AI tự học lại khi thị trường thay đổi hoặc hiệu suất suy giảm — không cần con người huấn luyện lại thủ công.

Vì hệ thống chạm vào tiền thật, các yêu cầu dưới đây được đánh số để có thể truy vết trực tiếp từ mã nguồn và kiểm thử ngược lại tài liệu này.

### Yêu cầu chức năng (FR)

| ID | Yêu cầu | Ghi chú |
|---|---|---|
| FR-01 | Hệ thống thu thập, chuẩn hoá dữ liệu thị trường theo thời gian thực từ nhiều nền tảng (crypto/forex/chứng khoán). | Xem Phần 03 (Market Data), Phần 10 |
| FR-02 | Hệ thống sinh tín hiệu giao dịch từ model AI kèm độ tin cậy đã hiệu chỉnh và giải thích được. | Xem Phần 05 |
| FR-03 | Hệ thống tự động đặt/huỷ/theo dõi lệnh trên sàn/broker với đảm bảo không trùng lặp. | Xem Phần 03C |
| FR-04 | Hệ thống thực thi kiểm tra rủi ro trước mọi lệnh và có khả năng ngắt giao dịch theo nhiều mức. | Xem Phần 03D |
| FR-05 | Hệ thống tự động huấn luyện lại model theo lịch hoặc theo sự kiện, kiểm định trước khi thay thế model đang chạy. | Xem Phần 05 |
| FR-06 | Hệ thống cung cấp giao diện giám sát thời gian thực và điều khiển khẩn cấp (kill-switch). | Xem Phần 04 |
| FR-07 | Hệ thống ghi lại đầy đủ lý do cho mọi quyết định giao dịch, truy vấn được sau này. | Xem Phần 03B, Phần 11, Phần 13 |
| FR-08 | Hệ thống đối soát định kỳ giữa dữ liệu nội bộ và dữ liệu từ sàn/broker, phát hiện và xử lý sai lệch. | Xem Phần 03C |
| FR-09 | Hệ thống tôn trọng lịch thị trường (phiên, holiday, halt) và mô hình phí/margin theo từng adapter. | Xem Phần 03D, Phần 10 |
| FR-10 | Hệ thống hỗ trợ dual-control cho hành động nguy hiểm (đổi risk limit, resume L2+, L4, promote >10% vốn). | Xem Phần 03D, Phần 13 |

### Yêu cầu phi chức năng (NFR)

| ID | Yêu cầu | Tiêu chí chấp nhận (đo được) |
|---|---|---|
| NFR-01 | An toàn vốn: không lệnh nào được đặt mà bỏ qua kiểm tra rủi ro. | 100% lệnh gửi tới sàn có bản ghi risk-check tương ứng; mọi dependency rủi ro mặc định fail-closed (Phần 03D). |
| NFR-02 | Khả năng truy vết: mọi quyết định giao dịch có thể tái dựng lại lý do. | 100% lệnh có bản ghi audit truy vấn được trong <2 giây; `trace_id` + `client_order_id` liên kết được end-to-end; audit WORM tối thiểu 5 năm (Phần 11, 13). |
| NFR-03 | Khả năng rollback: mọi thay đổi model/chiến lược đảo ngược được nhanh chóng. | Rollback model về phiên bản trước hoàn tất trong <5 phút kể từ khi phát hiện suy giảm hiệu suất. |
| NFR-04 | Độ trễ suy luận AI không làm chậm chu kỳ giao dịch. | Độ trễ suy luận < 50% chu kỳ nến của khung thời gian đang giao dịch (đo p99). |
| NFR-05 | Độ khả dụng của đường găng giao dịch (Strategy → Risk → OMS). | Uptime ≥ 99.9% trong giờ thị trường mở; error budget & chính sách đóng băng thay đổi khi hết budget (Phần 11). |
| NFR-06 | Thông lượng lệnh. | p99 submit→ack < 500ms; burst ≥ 20 lệnh/giây/account trong 5 giây mà không mất idempotency (đo theo adapter). |
| NFR-07 | Phục hồi thảm họa. | RPO/RTO theo tier ở Phần 14; restore drill thành công tối thiểu mỗi quý. |
| NFR-08 | Bảo mật credential & đường điều khiển. | 0 secret plaintext trong log/repo; pen-test/security review gate pass trước Phase 2 live (Phần 13, 15). |
| NFR-09 | Retention theo lớp dữ liệu. | Audit/ledger: ≥5 năm WORM; metrics: ≥90 ngày; feature store training snapshots: ≥2 năm hoặc theo policy ML Lead. |
| NFR-10 | Đồng bộ thời gian. | Mọi host giao dịch đồng bộ NTP; lệch đồng hồ >100ms so với stratum tin cậy → cảnh báo SEV2; >500ms → L1 cục bộ cho account bị ảnh hưởng. |

> **Ngoài phạm vi:** Tư vấn đầu tư cá nhân hoá, quản lý quỹ được cấp phép chính thức, và mọi hoạt động thuộc hồ sơ pháp lý (c) ở Phần 09 cho tới khi có sign-off pháp lý riêng.

---

## 02. Kiến trúc tổng thể

Kiến trúc hướng sự kiện (event-driven) cho phần lớn hệ thống, với một ngoại lệ tường minh: đường găng Strategy → Risk → OMS chạy đồng bộ để đảm bảo giới hạn rủi ro luôn được áp dụng trước khi lệnh rời hệ thống (xem ADR-04, Phần 12).

| STT | Thành phần | Vai trò | Luồng dữ liệu | Kiểu giao tiếp |
|---|---|---|---|---|
| 1 | Sàn / Broker (nguồn) | Cung cấp dữ liệu giá & tiếp nhận lệnh | — | — |
| 2 | Exchange/Broker Adapter | Chuẩn hoá khác biệt giữa các nền tảng sau một interface chung | Sàn ↔ Adapter | Bất đồng bộ |
| 3 | Market Data Service | Chuẩn hoá OHLCV/tick, phát sự kiện nến mới | Adapter → Feature Eng. | Bất đồng bộ |
| 4 | Feature Engineering | Tính chỉ báo kỹ thuật, ghi Feature Store | Market Data → AI Inference | Bất đồng bộ |
| 5 | AI Inference Engine | Sinh tín hiệu BUY/SELL/HOLD kèm xác suất hiệu chỉnh | Feature Store → Strategy | Bất đồng bộ |
| 6 | Strategy Engine | Kết hợp tín hiệu AI với luật lọc, định cỡ vị thế | AI Inference → Risk Mgmt | **ĐỒNG BỘ** (RPC, timeout fail-closed) |
| 7 | Risk Management | Kiểm tra giới hạn rủi ro, kill-switch, calendar/margin/fee | Strategy → Order Execution | **ĐỒNG BỘ** (RPC, timeout fail-closed) |
| 8 | Order Execution (OMS) | Đặt lệnh qua Adapter, đối soát với sàn | Risk Mgmt → Adapter → Sàn | **ĐỒNG BỘ** tới Adapter |

> **Event Bus:** Kafka cho toàn bộ sự kiện lõi cần audit/replay (candle.closed, signal.generated, order.\*, risk.\*, reconciliation.\*, kill_switch.\*, position.\*, model.\*, fee.\*) — ADR-01. Mọi event bắt buộc có `schema_version`, `trace_id`, `produced_at_utc` và đăng ký trên Schema Registry (Phần 03B).

> **GPU:** AI Inference KHÔNG cần GPU ở baseline (XGBoost/LightGBM chạy CPU). GPU chỉ cần xem xét nếu/khi áp dụng model deep learning (LSTM/Transformer, tuỳ chọn ở Phần 07).

> **Observability:** OpenTelemetry traces xuyên suốt Gateway → Strategy → Risk → OMS → Adapter; `client_order_id` và `signal_id` là baggage bắt buộc (Phần 11).

**[FE]** Frontend chỉ đọc/ghi qua API Gateway (REST + OpenAPI) cho thao tác cấu hình và WebSocket cho dữ liệu thời gian thực — không kết nối thẳng vào Event Bus hay các service nội bộ.

### Môi trường triển khai

| Môi trường | Mục đích | Dữ liệu | Quy tắc promote |
|---|---|---|---|
| `dev` | Phát triển cục bộ / CI | Synthetic + lịch sử công khai | Tự do |
| `staging` | Tích hợp, chaos, game-day | Paper / demo broker | CI xanh + review |
| `prod-paper` | Paper trading dài hạn | Paper keys | Checklist Phase 1 (Phần 15) |
| `prod-live` | Vốn thật | Live keys (Vault) | Dual gate: Risk + SRE + Security (Phần 15) |

Cấu hình hạ tầng và risk policy lưu dạng Infrastructure-as-Code / Config-as-Code (GitOps từ Phase 3; Phase 1 tối thiểu Compose + versioned config trong Git).

---

## 03. Backend chi tiết theo module

15 module với ranh giới trách nhiệm rõ ràng. Ở Phase 1, phần lớn được gộp thành ít container hơn theo mô hình modular-monolith (xem ADR-02, Phần 12) — ranh giới interface giữa các module vẫn giữ nguyên để tách container thật ở Phase 3-4 là một quyết định dựa trên tải thực tế, không phải giả định ban đầu.

#### **[BE]** API Gateway & Auth

*Phân kỳ triển khai: Container độc lập ngay từ Phase 1 (biên bảo mật rõ, tách sớm).*

*Cửa ngõ duy nhất cho Frontend. Xác thực, phân quyền, chống lạm dụng request.*

- JWT ngắn hạn + refresh token rotation; revoke list / phiên bị thu hồi
- RBAC theo vai trò: `admin` / `trader` / `viewer` / `risk_officer` / `ml_lead` / `sre` (+ break-glass có TTL)
- OpenAPI 3.x versioned (`/v1/...`); breaking change = major version song song trong cửa sổ deprecation
- Quản lý API key sàn: mã hoá bằng Vault/KMS, không log plaintext; step-up auth cho L3/L4 và đổi risk limit
- Rate limiting, request validation, idempotency-key cho mọi mutation nguy hiểm (không chỉ order)

#### **[BE]** Exchange / Broker Adapter Layer

*Phân kỳ triển khai: Module Core trong "Core Trading Service" ở Phase 1; ranh giới interface giữ nguyên để tách container riêng ở Phase 3-4 nếu tải yêu cầu.*

*Lớp trung gian chuẩn hoá mọi khác biệt giữa các sàn/broker sau một interface chung; Market Data Service và OMS gọi qua lớp này chứ không nối thẳng vào từng sàn.*

- Interface thống nhất: connect(), subscribe_market_data(), get_ohlcv(), place_order(), cancel_order(), get_order_status(), get_positions(), get_balance(), get_fees(), get_margin_state()
- Mỗi nền tảng là một adapter cắm rời: Crypto (CCXT — Binance/Bybit/OKX…), MT5 (forex/vàng/chỉ số qua MetaTrader5 hoặc MetaApi), Chứng khoán (Interactive Brokers/Alpaca)
- Chuẩn hoá symbol, khung thời gian và loại lệnh về một định dạng nội bộ duy nhất — có bảng ánh xạ (symbol registry) cho từng adapter
- Rate-limit budget tường minh per adapter (token bucket); vượt budget → queue có bound + SEV2, không spam sàn
- Che giấu khác biệt kết nối: WebSocket reconnect cho crypto, kiểm tra sức khoẻ terminal cho MT5; phát sự kiện candle.closed đã chuẩn hoá lên Event Bus
- Thêm sàn mới = viết thêm một adapter + contract test (Phần 15), không đụng tới Strategy Engine, Risk Management hay lõi AI

#### **[BE]** Market Data Service

*Phân kỳ triển khai: Gộp trong "Data Service" (cùng Feature Engineering) ở Phase 1.*

*Kết nối tới Adapter Layer, chuẩn hoá dữ liệu, phát sự kiện nến mới.*

- Tự động kết nối lại khi mất kết nối sàn (qua Adapter)
- Ghi OHLCV / order book vào time-series DB (TimescaleDB — ADR-05)
- Phát sự kiện candle.closed lên Event Bus; gắn `exchange_clock_skew_ms` khi phát hiện lệch thời gian
- Tích hợp Market Calendar (phiên mở/đóng, holiday, halt) — FR-09

#### **[BE]** Feature Engineering

*Phân kỳ triển khai: Gộp trong "Data Service" ở Phase 1.*

*Biến dữ liệu thô thành đặc trưng (feature) có ý nghĩa cho mô hình AI.*

- Chỉ báo kỹ thuật: RSI, MACD, Bollinger Bands, EMA, ATR...
- Feature Store có version — đảm bảo lúc train và lúc suy luận dùng cùng công thức (ADR-06)
- Chỉ service được uỷ quyền mới ghi Feature Store production; mọi ghi có audit
- Sentiment tin tức qua LLM **ngoài đường găng** (ADR-07): không chặn suy luận nếu LLM chậm/lỗi

#### **[AI]** AI Training Pipeline

*Phân kỳ triển khai: Gộp trong "AI Service" ở Phase 1 (cùng Inference + Registry).*

*Huấn luyện ngoại tuyến (offline), chạy trong container cô lập, không ảnh hưởng hệ thống đang chạy thật.*

- Nhận kích hoạt theo lịch định kỳ hoặc theo sự kiện phát hiện drift
- Chia dữ liệu train / validation / test theo thời gian, có purge + embargo (walk-forward nghiêm ngặt — xem Phần 05)
- Ngân sách chi phí: giới hạn giờ CPU/GPU và số trial Optuna / tuần (FinOps — Phần 08)
- Đẩy model ứng viên (challenger) vào Model Registry kèm Model Card (Phần 05)

#### **[AI]** AI Inference Service

*Phân kỳ triển khai: Gộp trong "AI Service" ở Phase 1.*

*Nạp model đang chạy production, sinh tín hiệu giao dịch theo thời gian thực.*

- Đầu vào: feature thời gian thực → đầu ra: xác suất đã hiệu chỉnh P(lợi nhuận > ngưỡng) theo horizon H, không phải điểm confidence thô
- Kèm giải thích (feature importance / SHAP) để hiển thị lên Frontend
- Độ trễ suy luận phải nhỏ hơn 50% thời gian một nến của khung thời gian đang giao dịch (NFR-04)
- Giám sát calibration live (reliability) — lệch quá ngưỡng → SEV2 + không tăng canary

#### **[AI]** Model Registry

*Phân kỳ triển khai: Gộp trong "AI Service" ở Phase 1.*

*Lưu vết mọi phiên bản mô hình — bắt buộc để rollback và tuân thủ MRM.*

- Lưu: dữ liệu train lineage, hyperparameter, chỉ số hiệu suất, Model Card, trạng thái champion/challenger/retired
- Công cụ tham khảo: MLflow, hoặc registry tự xây trên PostgreSQL
- Model bất biến sau publish; thay trạng thái không ghi đè lịch sử

#### **[BE]** Strategy Engine

*Phân kỳ triển khai: Gộp trong "Core Trading Service" ở Phase 1.*

*Kết hợp tín hiệu AI với các luật lọc bổ sung để ra quyết định cuối cùng.*

- Bộ lọc chế độ thị trường (trending / sideways), lọc thanh khoản
- Định cỡ vị thế: Kelly criterion giới hạn ở 25% full-Kelly; trừ phí/funding/swap ước tính từ Fee Model trước khi gửi Risk
- Gọi Risk Management theo kiểu ĐỒNG BỘ (RPC + timeout, fail-closed) — xem Phần 02

#### **[BE]** Risk Management

*Phân kỳ triển khai: Gộp trong "Core Trading Service" ở Phase 1 — KHÔNG được tối giản hoá hay bỏ qua dù gộp module.*

*Tuyến phòng thủ cuối cùng trước khi lệnh chạm tới sàn thật.*

- Thực thi phân cấp giới hạn rủi ro có số (Phần 03D), không cho phép Strategy Engine tự vượt qua
- Kill-switch 4 mức (L1-L4) + SoD/dual-control (Phần 03D)
- Giới hạn exposure theo tài sản, kiểm tra tương quan giữa các bot đang chạy
- Market Calendar + Margin state + Fee model là input bắt buộc của risk-check (FR-09)
- Mọi thay đổi risk limit chỉ qua API có audit + dual-control

#### **[BE]** Order Execution (OMS)

*Phân kỳ triển khai: Gộp trong "Core Trading Service" ở Phase 1.*

*Đặt / huỷ lệnh qua Adapter Layer, đảm bảo không đặt trùng khi có lỗi mạng.*

- Máy trạng thái lệnh đầy đủ, bao gồm trạng thái UNKNOWN khi mất ack (Phần 03C)
- Idempotency key cho mỗi lệnh; từ trạng thái UNKNOWN bắt buộc truy vấn trước khi retry — không bao giờ gửi lại mù
- Xử lý khớp một phần (partial fill), tính giá trung bình khối lượng; đối soát định kỳ với sàn (Phần 03C)

#### **[BE]** Portfolio & Ledger

*Phân kỳ triển khai: Gộp trong "Core Trading Service" ở Phase 1.*

*Sổ cái ghi nhận ý định và lịch sử giao dịch; đối soát VỀ PHÍA sàn/broker (sàn là sự thật cho vị thế/số dư hiện tại).*

- Thiết kế kiểu double-entry, có quy đổi đa tiền tệ về một đồng tiền báo cáo (ADR-08, Phần 10)
- Khi lệch với sàn: sàn thắng, ledger được sửa theo, chênh lệch ghi thành sự kiện audit (Phần 03C)
- Ghi fee/commission/funding/swap thành bút toán riêng (không gộp ẩn vào P&L)
- Tính lãi/lỗ theo thời gian thực để Frontend hiển thị

#### **[BE]** Backtesting Engine

*Phân kỳ triển khai: Container riêng — tải tính toán theo đợt, tách biệt khỏi đường găng giao dịch ngay từ Phase 1.*

*Mô phỏng chiến lược / model trên dữ liệu lịch sử trước khi cho chạy thật.*

- Tính Sharpe, Sortino, Max Drawdown, Win rate, và PSR/DSR khi so sánh nhiều model (Phần 05)
- Walk-forward + purge + embargo để tránh việc mô hình học vẹt (overfit)
- Mô hình slippage + fee + (tuỳ chọn) funding phải khớp contract với live Fee Model
- Chạy dưới dạng job bất đồng bộ vì có thể mất vài phút

#### **[BE]** Notification Service

*Phân kỳ triển khai: Gộp trong "Core Trading Service" ở Phase 1.*

*Đẩy cảnh báo khi có sự kiện cần con người chú ý, theo phân cấp mức độ nghiêm trọng (Phần 11).*

- Kênh: email, Telegram, push notification, kênh page riêng cho SEV1
- Sự kiện: lệnh khớp lớn, vượt ngưỡng drawdown, model bị rollback, lệch đối soát, dual-control pending

#### **[BE]** Observability Stack

*Phân kỳ triển khai: Hạ tầng dùng chung, triển khai song song từ Phase 1 — không hoãn tới sau.*

*Không thể vận hành một hệ thống chạm tới tiền thật mà thiếu khả năng quan sát.*

- Log tập trung (ELK/Loki), metrics (Prometheus/Grafana) theo bộ SLO/SLI ở Phần 11
- Distributed tracing: OpenTelemetry; bắt buộc `trace_id`, `client_order_id`, `signal_id`, `account_id`
- Audit trail WORM (append-only + lưu trữ không xoá trong retention): mọi quyết định giao dịch và mọi hành động dual-control

---

## 03B. Mô hình dữ liệu & Data Contracts

*Ngôn ngữ chung bắt buộc để 15 module ở Phần 03 ăn khớp với nhau*

### Chính sách Schema Registry

| Quy tắc | Chi tiết |
|---|---|
| Công cụ | Schema Registry (Avro hoặc JSON Schema — mặc định JSON Schema + Confluent-compatible registry; ADR có thể chốt binary sau) |
| Compatibility | `BACKWARD` trong cùng major version; breaking → tăng major + chạy dual-publish trong cửa sổ chuyển tiếp |
| CI gate | Pipeline fail nếu schema mới vi phạm compatibility hoặc thiếu field bắt buộc (`trace_id`, `schema_version`, `produced_at_utc`) |
| Additive-only | Chỉ được thêm field mới trong cùng major; đổi kiểu / xoá field = major mới |

### Domain model

| Entity | Mô tả | Bất biến chính |
|---|---|---|
| Order | Một lệnh gửi tới sàn/broker. | Có đúng 1 trạng thái tại một thời điểm (Phần 03C); `client_order_id` duy nhất toàn hệ thống. |
| Position | Vị thế đang mở trên một symbol/account. | Số lượng + giá vốn phải khớp giữa ledger và sàn sau mỗi lần đối soát. |
| Trade | Một lần khớp lệnh (có thể một Order sinh nhiều Trade do khớp một phần). | Tổng khối lượng các Trade của một Order không vượt quá khối lượng Order gốc. |
| Account | Tài khoản giao dịch trên một broker/sàn cụ thể. | Thuộc đúng một Adapter; số dư luôn đối chiếu được với sàn. |
| Strategy | Một cấu hình chiến lược (tham số + model gắn kèm + giới hạn rủi ro riêng). | Không được vượt giới hạn rủi ro cấp Account/Portfolio dù cấu hình riêng nới hơn. |
| Model | Một phiên bản model AI trong Model Registry. | Bất biến sau khi publish (immutable); trạng thái champion/challenger/retired không ghi đè lịch sử. |
| Signal | Một tín hiệu AI Inference sinh ra tại một thời điểm. | Luôn gắn với đúng một Model version và một feature snapshot — truy vết được nguồn gốc. |
| FeeLeg | Một khoản phí/commission/funding/swap gắn với Trade hoặc Position. | Không âm spoof; luôn quy đổi được sang reporting currency. |
| RiskLimitChange | Đề xuất thay đổi giới hạn rủi ro. | Không hiệu lực cho đến khi có phê duyệt dual-control. |

### DDL tối thiểu (logical — Phase 0 chốt physical)

| Bảng | Khoá / Index bắt buộc | Ghi chú |
|---|---|---|
| `orders` | PK `client_order_id`; index `(account_id, state, updated_at)`; unique `(adapter, broker_order_id)` khi not null | Lưu state machine |
| `trades` | PK `trade_id`; index `client_order_id`; index `(account_id, executed_at)` | Partial fills |
| `positions` | PK `(account_id, symbol)`; index `updated_at` | Snapshot hiện tại |
| `accounts` | PK `account_id`; unique `(adapter, external_account_id)` | |
| `risk_checks` | PK `risk_check_id`; index `client_order_id` | NFR-01 |
| `audit_events` | PK `event_id`; index `(trace_id)`, `(entity_type, entity_id, at)` | WORM sink |
| `model_versions` | PK `(model_id, version)` | Immutable blob + metadata |
| `schema_outbox` / Kafka topics | Theo Schema Registry subject | |

### Schema sự kiện (Event Bus)

Mọi event dưới đây kế thừa envelope chung:

```
trace_id: uuid
produced_at_utc: datetime
producer_service: string
schema_version: int   // major của subject
```

**`candle.closed  (v1)`**

```
symbol: string
adapter: string
timeframe: string
open_time_utc: datetime
close_time_utc: datetime
ohlcv: { open, high, low, close, volume }
ingested_at_utc: datetime
exchange_clock_skew_ms: int | null
session_state: "open" | "closed" | "halt" | "auction"
```

**`signal.generated  (v1)`**

```
signal_id: uuid
symbol: string
model_id: string
model_version: string
prediction_target: string
probability_calibrated: float
feature_snapshot_id: string
generated_at_utc: datetime
```

**`order.submitted / .acknowledged / .partially_filled / .filled / .canceled / .rejected / .unknown  (v1)`**

```
client_order_id: uuid
broker_order_id: string | null
symbol: string
side: "buy" | "sell"
state: string
signal_id: uuid | null
risk_check_id: uuid          // bắt buộc — không có = không được submit (NFR-01)
avg_fill_price: number | null
filled_qty: number
timestamp_utc: datetime
```

**`position.updated  (v1)`**

```
account_id: string
symbol: string
qty: number
avg_price: number
unrealized_pnl: number
margin_used: number | null
source: "fill" | "recon" | "corporate_action"
timestamp_utc: datetime
```

**`fee.posted  (v1)`**

```
account_id: string
client_order_id: uuid | null
fee_type: "commission" | "funding" | "swap" | "other"
amount: number
currency: string
amount_reporting: number
fx_rate: number
timestamp_utc: datetime
```

**`risk.limit_breached  (v1)`**

```
account_id: string
limit_type: string
threshold: number
observed_value: number
action_taken: string
timestamp_utc: datetime
```

**`kill_switch.activated / .resumed  (v1)`**

```
scope: "strategy" | "account" | "portfolio" | "global"
level: "L1" | "L2" | "L3" | "L4"
triggered_by: "auto" | "manual"
actor_id: string | null
approver_id: string | null   // bắt buộc với L3 resume, L4, và mọi resume L2+
reason: string
timestamp_utc: datetime
```

**`model.promoted / .rolled_back / .retired  (v1)`**

```
model_id: string
from_version: string | null
to_version: string
stage: "shadow" | "canary" | "champion" | "retired"
approver_id: string
canary_capital_pct: number | null
timestamp_utc: datetime
```

**`reconciliation.break_detected  (v1)`**

```
account_id: string
break_type: "position" | "cash" | "trade" | "fee" | "margin"
internal_value: number
broker_value: number
status: "INVESTIGATING" | "RESOLVED"
detected_at_utc: datetime
```

---

## 03C. Vòng đời lệnh & Máy trạng thái

*Loại bỏ mơ hồ ở đúng chỗ tiền có thể mất*

### Máy trạng thái lệnh (Order)

```
CREATED
  → RISK_APPROVED  |  RISK_REJECTED   (kiểm tra đồng bộ, fail-closed nếu Risk Mgmt không phản hồi)
      RISK_APPROVED → SUBMITTED
          SUBMITTED → ACKNOWLEDGED
          SUBMITTED → UNKNOWN         (timeout chờ ack — KHÔNG được tự retry mù)
              UNKNOWN → [truy vấn get_order_status(client_order_id)] → về lại trạng thái thật
          ACKNOWLEDGED → PARTIALLY_FILLED → FILLED
          ACKNOWLEDGED → FILLED
          ACKNOWLEDGED → CANCELED  |  REJECTED  |  EXPIRED
```

> **Quy tắc bắt buộc:** từ trạng thái UNKNOWN (mất ack do timeout mạng), hệ thống PHẢI truy vấn `get_order_status(client_order_id)` trước khi thực hiện bất kỳ hành động nào khác — không bao giờ gửi lại lệnh một cách mù quáng.

### Máy trạng thái đối soát (Reconciliation)

```
RECONCILIATION_BREAK  (phát hiện lệch giữa Ledger và Sàn/Broker)
  → tự động kích hoạt L2 HALT_ALL_ORDERS trên account/symbol liên quan
  → phát sự kiện SEV1 (Phần 11)
  → INVESTIGATING  (quy tắc: SÀN LÀ SỰ THẬT — ledger được sửa theo sàn)
  → RESOLVED  (chênh lệch được ghi thành sự kiện audit, không xoá lịch sử)
```

> **Nguồn sự thật:** khi ledger nội bộ và sàn/broker lệch nhau, SÀN LUÔN THẮNG. Ledger nội bộ là hệ thống ghi nhận ý định và lịch sử, không phải nguồn sự thật cho vị thế/số dư hiện tại.

### Enforce Stop-loss / Take-profit theo từng adapter

| Adapter | Cơ chế | Rủi ro tồn dư |
|---|---|---|
| Crypto (CCXT) | Ưu tiên stop-order native trên sàn khi hỗ trợ (stop-market/stop-limit). | Sàn có thể tạm ngừng khớp stop trong biến động cực đoan (circuit breaker của sàn) — cần watchdog dự phòng. |
| MT5 (official / MetaApi) | SL/TP gắn native vào lệnh MT5. | Nếu dùng MetaApi, phụ thuộc uptime bên thứ ba; terminal ngắt kết nối có thể trễ việc sửa/huỷ stop. |
| Chứng khoán (IBKR/Alpaca) | Stop order native qua broker. | Giờ ngoài phiên hoặc halted symbol: stop có thể không khớp đúng giá kỳ vọng (gap risk). |
| Trường hợp chỉ có synthetic stop | Hệ thống tự giám sát giá và tự gửi lệnh đóng khi chạm ngưỡng. | Watchdog bắt buộc: nếu khoảng gián đoạn giám sát > ngưỡng định nghĩa (Phần 11), tự động L3 FLATTEN vị thế liên quan. |

---

## 03D. Phân cấp giới hạn rủi ro & Kill-Switch

*Con số để Risk Officer thật sự có thể ký duyệt*

### Bảng giới hạn rủi ro (mặc định đề xuất — cần tinh chỉnh theo khẩu vị rủi ro thật)

| Loại giới hạn | Mặc định đề xuất | Ghi chú |
|---|---|---|
| Rủi ro tối đa / lệnh | ≤ 1% vốn chủ sở hữu | Tính trên khoảng cách entry–stop loss × khối lượng, **sau phí ước tính**. |
| Exposure tối đa / symbol | ≤ 20% vốn chủ sở hữu | Cộng dồn mọi vị thế đang mở trên cùng symbol. |
| Exposure tối đa / strategy | ≤ 30% vốn chủ sở hữu | Áp dụng dù cấu hình chiến lược có đặt tham số nới hơn. |
| Gross exposure toàn danh mục | ≤ 150% vốn (≤100% nếu không dùng đòn bẩy) | Kiểm tra trước mỗi lệnh mới ở Risk Management. |
| Margin usage | ≤ 70% margin available của account | Nếu broker báo gần liquidation → L2 ngay. |
| Ngưỡng dừng trong ngày | Lỗ −3% vốn → L1; −5% vốn → L3 | Tính theo múi giờ giao dịch chính của tài khoản. |
| Ngưỡng dừng 7 ngày trượt | Lỗ −8% vốn → L2, chờ review thủ công | Không tự resume — cần xác nhận của Risk Officer. |
| Số lệnh thua liên tiếp | 6 lệnh → tự tạm dừng chiến lược (L1 cho strategy đó) | Reset bộ đếm khi có 1 lệnh thắng hoặc khi resume thủ công. |
| Giới hạn tương quan | Tối đa 3 vị thế mở đồng thời có tương quan cặp > 0.7 | Tính trên cửa sổ trượt 30 ngày gần nhất. |
| Định cỡ vị thế (Kelly) | Tối đa 25% full-Kelly | Đầu vào là xác suất đã hiệu chỉnh + payoff thực đo từ walk-forward (Phần 05). |
| Ngoài giờ / holiday | Không mở entry mới khi session_state ≠ open | Cho phép quản lý/đóng vị thế theo policy riêng từng adapter. |

### Taxonomy Kill-Switch

| Mức | Tên | Phạm vi hành động | Kích hoạt bởi | Điều kiện khôi phục |
|---|---|---|---|---|
| L1 | PAUSE_NEW_ENTRIES | Dừng mở vị thế mới; vị thế hiện có tiếp tục được quản lý bình thường. | Tự động (ngưỡng lệch chuẩn) hoặc thủ công | **Cooldown tối thiểu 15 phút**; chỉ auto-resume nếu điều kiện kích hoạt hết **và** không có L2/L3 active trên cùng scope. Sau 2 lần auto-resume trong 24h → khoá, yêu cầu thủ công. |
| L2 | HALT_ALL_ORDERS | Huỷ mọi lệnh đang chờ; không lệnh mới; vị thế hiện có giữ nguyên với stop vẫn hoạt động. | Tự động (reconciliation break, mất kết nối sàn) hoặc thủ công | Chỉ resume thủ công; dual-control nếu scope ≥ account. |
| L3 | FLATTEN_ALL | Đóng thị trường toàn bộ vị thế + huỷ mọi lệnh, SLA thực thi ≤30s cho tài sản thanh khoản cao. | Tự động (vượt ngưỡng dừng ngày) hoặc thủ công (nút khẩn trên FE) | Chỉ resume thủ công sau Risk Officer xác nhận; dual-control bắt buộc. |
| L4 | FULL_LOCKDOWN | L3 + thu hồi quyền trade của API key/tài khoản khi sàn hỗ trợ. | Chỉ thủ công | Two-person rule bắt buộc để mở lại (Risk Officer + Admin/CTO). |

### Ma trận Segregation of Duties (SoD) / Dual-control

| Hành động | Người đề xuất | Người phê duyệt | Tự thực thi? |
|---|---|---|---|
| Đổi risk limit (mọi cấp) | `trader` / `admin` | `risk_officer` | Không — chờ approve |
| Resume L2 (account+) | `sre` / `admin` | `risk_officer` | Không |
| Kích hoạt thủ công L3 | `admin` / `risk_officer` | Xác nhận step-up (cùng actor được phép nếu SEV1) | Có sau step-up |
| Resume L3 | `admin` | `risk_officer` | Không |
| Kích hoạt / Resume L4 | `admin` hoặc `risk_officer` | Người còn lại (two-person) | Không |
| Promote canary → 100% | `ml_lead` | `risk_officer` nếu vốn canary >10% NAV | Không |
| Break-glass login | `sre` | TTL ≤ 60 phút; audit SEV1 | Có trong TTL |

Người đề xuất **không** được tự phê duyệt cùng một yêu cầu (trừ break-glass có TTL và post-review bắt buộc trong 24h).

### Ma trận Fail-open / Fail-closed

Quy tắc NFR-01: mọi đường liên quan tới rủi ro mặc định FAIL-CLOSED (không kiểm tra được = không có lệnh), trừ các ngoại lệ liệt kê rõ ràng dưới đây.

| Dependency | Mặc định | Chi tiết |
|---|---|---|
| Risk Management không phản hồi | Fail-closed | Strategy Engine chặn mọi lệnh mới cho tới khi Risk Management phản hồi lại. |
| Vault/KMS không truy cập được | Fail-closed | Chặn đặt lệnh mới và chặn đọc credential mới; stop-loss native trên sàn vẫn hoạt động. |
| Event Bus down/phân mảnh | Fail-closed cho đường găng; fail-open cho hiển thị | Đường Strategy→Risk→OMS không đi qua bus; dừng nhận tín hiệu mới tới khi bus phục hồi. FE hiển thị dữ liệu cũ kèm "stale". |
| Feed dữ liệu thị trường chết | Fail-closed cho symbol bị ảnh hưởng | L1 cục bộ; vị thế hiện có dùng stop native nếu có. |
| Model Registry/Inference không phản hồi | Fail-closed | Không có tín hiệu mới = không có lệnh mới. |
| Market Calendar không tải được | Fail-closed cho entry mới | Không mở vị thế mới cho tới khi calendar healthy. |
| Schema Registry unavailable | Fail-closed cho publish event mới | Không publish event không validate được; đường găng đồng bộ vẫn dùng DB local state. |

---

## 04. Frontend chi tiết theo màn hình

Frontend là lớp giám sát & điều khiển — không tự xử lý logic giao dịch, chỉ hiển thị trạng thái từ Backend và gửi lệnh cấu hình.

#### **[FE]** Dashboard tổng quan

- Equity curve, lãi/lỗ hôm nay và tổng (đồng tiền báo cáo — ADR-08), số bot đang chạy
- Cảnh báo gần nhất kèm SEV1/2/3, trạng thái kết nối sàn, error budget còn lại

#### **[FE]** Thanh điều khiển khẩn cấp (Kill-switch)

- Hiện 4 mức L1-L4 trên mọi màn hình; L3/L4 bắt buộc hộp thoại xác nhận + step-up
- Hiển thị dual-control pending (ai đề xuất / chờ ai duyệt)
- Trạng thái từng account/strategy (đang chạy / tạm dừng / khoá)

#### **[FE]** Strategy / Bot Builder

- Form có kiểm tra hợp lệ; giai đoạn sau: builder kéo-thả
- Không cho phép đặt giới hạn rủi ro riêng vượt cấp Account/Portfolio (Backend enforce)

#### **[FE]** AI Model Center

- Danh sách phiên bản, PSR/DSR, calibration live, Model Card
- Trạng thái champion / challenger / shadow / canary, log drift
- Nút huấn luyện lại / promote — tôn trọng dual-control khi >10% vốn

#### **[FE]** Backtest Studio

- Form khoảng thời gian, vốn, phí, slippage
- Equity curve, drawdown; so sánh chạy kèm PSR/DSR

#### **[FE]** Live Monitor

- Nến realtime, overlay tín hiệu + xác suất hiệu chỉnh
- Danh sách lệnh đúng state Phần 03C (kể cả UNKNOWN); log WS có resume-from-sequence
- Chỉ báo stale rõ ràng khi feed gián đoạn

#### **[FE]** Account & API Key

- Nhập API key một lần, chỉ masked sau đó
- Nhắc tắt quyền rút tiền; MT5 phân biệt master/investor password

#### **[FE]** Alerts & Notification

- Kênh theo SEV1/2/3 (Phần 11)

#### **[FE]** Reports & History

- Lịch sử giao dịch, CSV, P&L reporting currency
- Báo cáo tuần/tháng; xuất audit theo `trace_id` / `client_order_id`

#### **[FE]** Approvals (mới ở v2.1)

- Hàng đợi dual-control: đổi risk limit, resume L2+, promote canary
- Hiển thị diff trước/sau; bắt buộc lý do phê duyệt

---

## 05. Vòng lặp AI “tự học và làm lại” & Model Risk Management

Đây là phần khác biệt hệ thống này với một bot rule-based thông thường: mô hình tự phát hiện khi nó đang “đuối” và tự thay thế chính mình một cách có kiểm soát.

### Prediction target

```
target = P( lợi_nhuận(H nến tiếp theo) > ngưỡng_đã_trừ_chi_phí )
// H = horizon, cấu hình theo khung thời gian của chiến lược
// Bắt buộc hiệu chỉnh xác suất (Platt scaling / isotonic regression),
//   kiểm tra bằng reliability diagram trước khi đưa vào Kelly sizing
```

### Chín bước vòng lặp

**Bước 1 — Thu thập dữ liệu liên tục**

Market Data cùng kết quả giao dịch thực tế được ghi lại. Mỗi nhãn mang timestamp `label_available_at` = thời điểm LỆNH ĐÓNG (không phải thời điểm mở) — tránh rò rỉ nhãn từ tương lai vào dữ liệu train.

**Bước 2 — Feature Store có version**

Đặc trưng được tính và lưu có phiên bản, đảm bảo dữ liệu train và dữ liệu suy luận luôn khớp công thức (ADR-06).

**Bước 3 — Kích hoạt huấn luyện lại**

Theo lịch (ví dụ mỗi tuần) hoặc theo sự kiện: hiệu suất live giảm dưới ngưỡng, hoặc phát hiện drift (PSI, KS-test) — phân biệt feature drift, concept drift và performance decay, mỗi loại có ngưỡng riêng.

**Bước 4 — Huấn luyện model ứng viên**

Training job chạy cô lập, sinh "challenger". Snapshot loại bỏ mọi mẫu có `label_available_at` sau thời điểm snapshot. Áp dụng purge + embargo. Tôn trọng ngân sách Optuna/CPU tuần.

**Bước 5 — Kiểm định trên dữ liệu holdout**

Điều kiện đi tiếp: Deflated Sharpe Ratio (DSR) > 0 @ 95% có hiệu chỉnh theo số lần thử Optuna, **VÀ** edge ròng sau phí/trượt giá ≥ 2× chi phí round-trip, **VÀ** tối thiểu N≥100 lệnh trong giai đoạn shadow trước canary.

**Bước 6 — Shadow / Paper trading**

Challenger chạy song song với champion trên dữ liệu live nhưng KHÔNG đặt lệnh thật, trong N ngày.

**Bước 7 — Canary rollout có kiểm soát**

Cấp vốn nhỏ (ví dụ 10%) thật; tăng dần. Promote 100% cần ML Lead; nếu canary >10% NAV cần thêm Risk Officer (SoD).

**Bước 8 — Rollback tự động**

Suy giảm dưới ngưỡng an toàn → rollback <5 phút (NFR-03) + SEV1.

**Bước 9 — Ghi vết vào Model Registry**

Mọi phiên bản — kể cả bị loại — lưu đầy đủ metadata + Model Card. Quay lại Bước 1.

### Model Risk Management (MRM)

| Hạng mục | Yêu cầu |
|---|---|
| Model Card | Bắt buộc trước shadow: mục tiêu, dữ liệu, hạn chế, chỉ số, owner, ngày review |
| Owner | Mỗi model production có đúng một ML owner chịu trách nhiệm |
| Review chu kỳ | Tối thiểu mỗi quý hoặc sau 3 lần rollback — cái nào đến trước |
| Calibration live | Reliability diagram rolling 30 ngày; ECE vượt ngưỡng → SEV2 + khoá tăng canary |
| Training lineage | Hash dataset snapshot + feature version + code commit |
| Human gate | Không auto-promote 100% không có xác nhận |

---

## 06. Bảng phân chia Backend / Frontend theo tính năng

Nguyên tắc xuyên suốt: Backend giữ mọi logic và trạng thái sự thật; Frontend chỉ hiển thị và thu thập input. Không có tính toán tài chính nào chạy ở phía client.

| Tính năng | Backend chịu trách nhiệm | Frontend chịu trách nhiệm | Giao tiếp qua |
|---|---|---|---|
| Đăng nhập / xác thực | JWT, refresh rotation, revoke, RBAC, step-up | Form đăng nhập, lưu token an toàn, điều hướng theo quyền | REST |
| API key sàn giao dịch | Vault/KMS, xác minh quyền hạn key | Form nhập, masked, trạng thái kết nối | REST |
| Cấu hình bot / chiến lược | Validate tham số + risk ceiling, lưu cấu hình | Form / Builder, xem trước | REST + WS |
| Dual-control approvals | Hàng đợi đề xuất/phê duyệt, audit | Màn Approvals, diff, lý do | REST + WS |
| Dữ liệu thị trường | Adapter → chuẩn hoá → realtime | Biểu đồ, stale warning | WebSocket |
| Tín hiệu AI & lý do | Xác suất hiệu chỉnh, SHAP | Overlay, tooltip | WS + REST |
| Đặt / huỷ lệnh thủ công | Risk đồng bộ trước khi gửi sàn | Nút Buy/Sell, xác nhận; không hiện "đã khớp" sớm | REST |
| Kill-switch toàn cục | L1–L4 + SoD | Control thường trực, step-up L3/L4 | REST + WS |
| Giám sát vị thế & P&L | Ledger realtime + FX reporting | Bảng vị thế, biểu đồ | WS + REST |
| Backtest | Job async + PSR/DSR + fee model | Form, tiến độ, kết quả | REST + WS |
| Quản lý model AI | Registry, training, MRM gates | Model Center, Model Card | REST |
| Cảnh báo / thông báo | Rule SEV1/2/3 | Cấu hình ngưỡng, inbox | REST + WS |
| Báo cáo lịch sử | Query phân trang, CSV, audit export | Bộ lọc, tải xuống | REST |

### WebSocket contract (tóm tắt)

- Auth: ticket ngắn hạn gắn session JWT
- Resume-from-sequence: client gửi `last_seq`; server replay hoặc gửi snapshot + gap warning
- Backpressure: server có thể disconnect chậm; client phải reconnect theo backoff có jitter

---

## 07. Tech stack đề xuất

Ưu tiên hệ sinh thái Python cho phần AI; tách riêng phần thực thi lệnh nếu cần độ trễ thấp. Các quyết định có ADR ở Phần 12.

**BE — Dịch vụ & hạ tầng dữ liệu**

- Python · FastAPI (+ OpenAPI 3.x)
- PostgreSQL
- TimescaleDB (ADR-05) — không InfluxDB ở baseline
- Redis (cache/tín hiệu nội bộ phi audit — không dùng cho event bus lõi, ADR-01)
- Kafka + Schema Registry (ADR-01, Phần 03B)
- Docker + Kubernetes (từ Phase 3; Phase 1 Docker Compose — ADR-02)
- OpenTelemetry Collector → Tempo/Jaeger + Prometheus

**BE — Kết nối sàn / broker (adapter)**

- CCXT — crypto
- MetaTrader5 (official) hoặc MetaApi — ADR-03 / ADR-09
- ib_insync / Alpaca — chứng khoán

**AI/ML — Mô hình & huấn luyện**

- scikit-learn / XGBoost / LightGBM — baseline CPU
- PyTorch — tuỳ chọn tương lai
- Optuna (multiple-testing aware)
- MLflow (registry + Model Card artifacts)
- Feature Store: tự xây trên Postgres/Timescale ở Phase 1–2; đánh giá Feast ở Phase 3 (ADR-06)
- Claude API — ngoài đường găng (ADR-07)

**FE — Giao diện**

- React + Next.js + TypeScript
- TailwindCSS
- TradingView Lightweight Charts
- WebSocket client — resume-from-sequence
- React Query / Zustand

**Vận hành & bảo mật**

- GitHub Actions (CI/CD) + SBOM (Syft) + CVE scan (Grype/Trivy)
- Prometheus + Grafana + Loki/ELK
- HashiCorp Vault
- GitOps (Argo CD / Flux) từ Phase 3
- Object storage WORM/Object Lock cho audit archive (Phần 13, 14)

---

## 08. Lộ trình phát triển theo giai đoạn

Nguyên tắc: chạy paper trading cho tới khi Backtest lẫn Shadow ổn định, mới chuyển vốn thật — bắt đầu nhỏ. Mỗi giai đoạn có tiêu chí thoát đo được.

| Giai đoạn | Thời gian | Mục tiêu | Mô tả | Tiêu chí thoát |
|---|---|---|---|---|
| Giai đoạn 0 | 2–4 tuần | Chuẩn bị | Chọn thị trường/broker, review ToS, pháp lý, schema, chốt ADR-01..09 cần thiết (tối thiểu 01–05, 08). | ADR tối thiểu đã ký; risk register khởi tạo; ToS review xong; schema subjects v1 đăng ký. |
| Giai đoạn 1 | 4–6 tuần | MVP nền tảng | Core Trading + Data + Backtesting + 1 chiến lược rule-based + Dashboard + kill-switch + Observability cơ bản. Paper trading. | ≥30 ngày paper liên tục; 0 bug nghiêm trọng; 0 lệch đối soát chưa xử lý; checklist Phần 15 Phase 1 pass. |
| Giai đoạn 2 | 6–8 tuần | Tích hợp AI + live nhỏ | AI Service baseline + Strategy AI; **vốn thật thử nghiệm ≤ 5% NAV tổng** (hoặc số tuyệt đối Risk Officer chốt); đủ giới hạn 03D; security gate pass. | ≥4 tuần live trong drawdown đã định; 0 kill-switch do lỗi hệ thống; game-day L3 ≤30s; restore drill 1 lần thành công. |
| Giai đoạn 3 | 6–8 tuần | Tự động hoá học lại | Training Pipeline, Registry/MRM, drift, Shadow/Canary, Approvals FE, SRE runbook đầy đủ, GitOps. | ≥3 promote canary thành công; 0 auto-rollback do lỗi triển khai; OTel trace cover ≥95% đường găng. |
| Giai đoạn 4 | Liên tục | Mở rộng | Đa chiến lược/model, no-code builder, tối ưu hạ tầng; multi-user **chỉ sau** sign-off pháp lý. | Review pháp lý (09) có chữ ký trước user thứ ba — không ngoại lệ. |

### FinOps (ngân sách tham chiếu — tinh chỉnh theo quy mô)

| Hạng mục | Phase 1–2 | Cảnh báo |
|---|---|---|
| Kafka / Schema Registry | Managed nhỏ hoặc single-node staging | Chi phí partition/retention audit 5 năm |
| MetaApi | Theo số account | ADR-09: chuyển EA bridge nếu > ngưỡng $/tháng |
| TimescaleDB storage | Retention hot 90d + cold tier | Nén + tiering |
| Claude API (nếu bật) | Budget $/ngày cứng | Circuit-break feature, không ảnh hưởng trading path |
| Training (CPU) | Trần giờ/tuần | Job bị reject khi vượt trần |

---

## 09. Rủi ro, bảo mật & pháp lý

*Risk Register chính thức*

| ID | Hạng mục | Khả năng | Ảnh hưởng | Chủ sở hữu | Biện pháp / Trạng thái |
|---|---|---|---|---|---|
| R-01 | API key: chỉ cấp quyền trade, không rút tiền | Trung bình | Cao | Người vận hành | Quy trình + review quý; Vault policy |
| R-02 | Circuit breaker / kill-switch không đủ nhanh | Thấp | Cao | Risk Officer | SLA L3 ≤30s; game-day bắt buộc trước live |
| R-03 | Đặt lệnh trùng do retry mù | Trung bình | Cao | BE Lead | FSM + idempotency; chaos test Phần 15 |
| R-04 | Overfitting / promote model kém | Cao | Cao | ML Lead | PSR/DSR + MRM + calibration live |
| R-05 | Audit trail không đầy đủ / bị sửa | Thấp | Cao | SRE / Security | WORM + Schema Registry + OTel |
| R-06 | Ràng buộc pháp lý khi mở SaaS | Cao | Rất cao | Cố vấn pháp lý | Gate cứng trước Giai đoạn 4 |
| R-07 | Vi phạm ToS broker về automated trading | Trung bình | Cao | Người vận hành | Review ToS Giai đoạn 0 |
| R-08 | Lệ thuộc MetaApi nắm credential MT5 | Trung bình | Trung bình | CTO | ADR-03/09; phương án EA bridge |
| R-09 | Thay đổi risk limit trái phép / insider | Thấp | Cao | Risk Officer | SoD dual-control (03D, 13) |
| R-10 | Mất dữ liệu / DR thất bại | Thấp | Rất cao | SRE Lead | Phần 14; drill quý |
| R-11 | CVE trong dependency (CCXT…) | Trung bình | Cao | Security Lead | SBOM + scan CI; patch SLA |
| R-12 | Lệch đồng hồ / sai timestamp | Thấp | Trung bình | SRE | NTP + NFR-10 |

### Ba hồ sơ pháp lý — không được gộp làm một

| Hồ sơ | Mô tả | Rủi ro / Yêu cầu |
|---|---|---|
| (a) Tự doanh vốn riêng | Chủ dự án trade vốn của chính mình. | Rủi ro pháp lý thấp nhất; lưu ý thuế và (với forex) quy định ngoại hối nếu broker offshore. |
| (b) Cung cấp phần mềm cho người tự trade | User tự kết nối tài khoản, tự chịu trách nhiệm; nền tảng là công cụ. | ToS rõ, giới hạn trách nhiệm; không bị coi là tư vấn đầu tư; tenant isolation khi multi-user. |
| (c) Quản lý vốn hộ người khác | Nền tảng ra quyết định và quản lý vốn bên thứ ba. | Có thể cần cấp phép. BẮT BUỘC gate pháp lý trước khi vào (c). |

### Threat model rút gọn (STRIDE) — mở rộng ở Phần 13

| Thành phần | Mối đe doạ tiêu biểu | Biện pháp |
|---|---|---|
| API Gateway | Spoofing, leo thang RBAC | JWT ngắn hạn + refresh rotation + revoke; test RBAC mỗi release |
| Vault / KMS | Lộ secret qua log / lateral movement | Không log secret; AppRole/mTLS; xoay khoá; audit đọc secret |
| OMS | Session bị chiếm, đặt lệnh trái phép | Step-up hành động nguy hiểm; risk Backend không bị FE ghi đè |
| Model Registry / Training | Data poisoning | Integrity check; hạn chế ghi Feature Store; human gate promote |
| Dual-control queue | Approve giả mạo | Approver ≠ proposer; step-up; audit WORM |

---

## 10. Kết nối đa nền tảng & tích hợp MT5

Phần này chi tiết hoá lớp Exchange/Broker Adapter: mọi khác biệt nền tảng bị cô lập trong adapter; lõi (AI, Strategy, Risk, OMS) chỉ làm việc với một mô hình dữ liệu duy nhất.

MT5 không có “API đám mây” như sàn crypto — cách kết nối là quyết định kiến trúc (ADR-03, ADR-09).

### Ba hướng kết nối MT5

| Hướng kết nối | Cách hoạt động | Đánh đổi |
|---|---|---|
| MetaTrader5 (Python, official) | Kết nối terminal đang mở trên cùng máy; thiên về polling. | Windows-only; hợp prototype / 1 account. |
| MetaApi (cloud) | Bên thứ ba bắc cầu REST + streaming. | Linux/K8s-friendly; phí; credential bên thứ ba (R-08). |
| Cầu nối EA (MQL5) tự viết | EA nói chuyện với backend qua socket/WebRequest/file. | Toàn quyền kiểm soát; tự bảo trì; vẫn cần terminal. |

### Thông tin đăng nhập: crypto vs MT5

| Yếu tố | Sàn crypto | MT5 |
|---|---|---|
| Định danh | API key + secret (+ passphrase) | Login + password + server |
| Phân quyền | Tắt withdraw bắt buộc | Master vs investor password |
| Lưu trữ | Vault/KMS, masked | Vault/KMS; MetaApi = thêm rủi ro bên thứ ba |

### P&L đa tiền tệ

Ledger lưu P&L theo tiền gốc instrument **và** giá trị quy đổi sang đồng tiền báo cáo (mặc định USD — ADR-08; có thể VND cho báo cáo nội bộ). Nguồn tỷ giá và thời điểm quy đổi (lúc khớp lệnh) phải nhất quán; FX rate lưu kèm mỗi `fee.posted` / trade.

### Corporate actions (chứng khoán)

Stock split và cổ tức phải áp dụng vào OHLCV lịch sử backtest và đối soát số lượng vị thế qua thời điểm chia tách.

### Market Calendar, phí, margin

- **Market Calendar:** forex có phiên/cuối tuần; CK có holiday/halt; crypto 24/7 — Risk và drift detection phải đọc calendar.
- **Fee model:** commission, funding (crypto perp), swap (forex) — adapter cung cấp; Strategy/Risk/Backtest dùng cùng contract.
- **Margin:** `get_margin_state()` trước lệnh có đòn bẩy; gần liquidation → L2.
- **Symbol registry:** EURUSD / XAUUSD vs BTC/USDT vs AAPL.
- **Định cỡ:** lot forex vs coin/contract — chỉ trong adapter, không hard-code Strategy Engine.

---

## 11. Vận hành & SRE Runbook

*Cho SRE vận hành lúc 3 giờ sáng*

### SLO / SLI theo service

| Service | Chỉ số | Mục tiêu | Ghi chú |
|---|---|---|---|
| OMS (đặt lệnh) | Thời gian submit → ack | p99 < 500ms | Đo tại Adapter; tách theo sàn |
| Market Data | Staleness | Cảnh báo nếu không có candle.closed > 2× chu kỳ kỳ vọng | Khác nhau forex vs crypto |
| API Gateway | Uptime | ≥ 99.9% giờ thị trường mở | Theo từng thị trường |
| AI Inference | Độ trễ suy luận | p99 < 50% chu kỳ nến | NFR-04 |
| Risk Management | Thời gian risk-check | p99 < 200ms | Nằm trong ngân sách 500ms OMS |
| Reconciliation | Chu kỳ đối soát | 1–5 phút khi có vị thế mở | Break → L2 tự động |
| Tracing | Coverage đường găng | ≥ 95% request có full trace | Phase 3 exit |

### Error budget (NFR-05)

| Chu kỳ | Budget | Khi còn < 25% | Khi hết |
|---|---|---|---|
| 30 ngày trượt | 0.1% downtime đường găng (~43 phút) | Đóng băng thay đổi rủi ro cao (promote 100%, nới limit) | Chỉ hotfix SEV1; postmortem bắt buộc trước khi mở lại change |

### FMEA — Bảng phân tích kiểu lỗi

| Lỗi | Cách phát hiện | Phản ứng tự động | Thời gian mục tiêu | Leo thang |
|---|---|---|---|---|
| Feed dữ liệu chết | Staleness > ngưỡng | L1 cục bộ; failover nguồn nếu có | < 2× chu kỳ nến | SEV2 → SEV1 nếu >15 phút |
| Broker 5xx / rate-limit | Lỗi liên tục 1 endpoint | Backoff có bound; vượt ngưỡng → L2 account/adapter | < 5 phút | SEV2 |
| Event Bus down | Consumer lag / mất broker | Đường găng đồng bộ OK; dừng tín hiệu mới | < 5 phút phát hiện | SEV1 |
| DB failover | Health check primary | Chuyển replica theo HA | RTO < 5 phút, RPO < 1 phút | SEV1 |
| Vault down | Health check | Fail-closed lệnh mới | Ngay | SEV1 |
| Inference/Registry down | Timeout / health | Không tín hiệu = không lệnh | < 1 phút | SEV2 → SEV1 >30 phút |
| MT5 terminal disconnect | Health / mất stream | L1 symbols MT5; reconnect backoff | < 3 phút | SEV2 |
| Clock skew | NTP monitor | SEV2; >500ms → L1 account | < 5 phút | SEV2 |

### Taxonomy cảnh báo

| Mức | Ví dụ sự kiện | Kênh | Phản hồi yêu cầu |
|---|---|---|---|
| SEV1 | Kill-switch auto, lệch đối soát, mất kết nối khi còn vị thế, break-glass | Page + escalation 5–10 phút | Xác nhận tiếp nhận trong SLA |
| SEV2 | Feed stale 1 symbol, broker lỗi có fallback, calibration lệch | Chat ngay | Trong ca hiện tại |
| SEV3 | Promote thành công, báo cáo định kỳ | Digest | Khi thuận tiện |

### Runbook rút gọn

- **Đối soát:** break → L2 → SEV1 → xác nhận 5–10 phút → sàn là sự thật → RESOLVED + audit.
- **Kill-switch:** chọn mức → thực thi → L3/L4 = SEV1 → resume theo SoD.
- **Bảo trì broker:** L1 trước cửa sổ bảo trì → resume khi healthy.
- **DR:** xem Phần 14; không improvise trên prod-live.
- **Postmortem:** mọi SEV1 có bản ghi trong 5 ngày làm việc (blameless).

### On-call

| Hạng mục | Quy định tối thiểu |
|---|---|
| Rotation | Có người primary; Phase 2+ có secondary cho SEV1 |
| Handoff | Checklist trạng thái kill-switch, vị thế mở, change đang pending |
| Truy cập | Break-glass TTL ≤60 phút; không dùng tài khoản shared |

---

## 12. Nhật ký quyết định kiến trúc

*ADR Log — để 6 tháng sau không ai phải đoán lại lý do*

### ADR-01 — Event Bus: Kafka vs Redis Streams

**Bối cảnh:** Cần tín hiệu nội bộ tốc độ cao + replay/audit (NFR-02).

**Lựa chọn:** Kafka (durable, replay, consumer group) vs Redis Streams (nhẹ hơn, durability yếu hơn).

**Quyết định:** Kafka (hoặc managed tương đương) cho event bus lõi. Redis chỉ cho tín hiệu phi audit.

**Hệ quả:** Thêm chi phí vận hành; đạt truy vết bắt buộc.

### ADR-02 — Modular-monolith vs microservice đầy đủ ở Phase 1

**Bối cảnh:** 15 module là ranh giới hợp lý nhưng 15 service độc lập quá sớm thì đắt.

**Quyết định:** Modular-monolith theo nhóm container ở Phase 1; tách thật ở Phase 3–4 theo tải.

**Hệ quả:** Rẻ hơn lúc đầu; cần kỷ luật ranh giới module trong code.

### ADR-03 — Kết nối MT5: official vs MetaApi vs EA bridge

**Bối cảnh:** MT5 không có cloud API thuần.

**Quyết định:** Mặc định MetaApi giai đoạn đầu để giữ Linux/K8s; có phương án EA bridge (ADR-09).

**Hệ quả:** Phụ thuộc bên thứ ba (R-08).

### ADR-04 — Strategy → Risk → OMS: đồng bộ

**Bối cảnh:** Risk là tuyến cuối; async qua bus có thể để lệnh “bay” trước khi limit mới có hiệu lực.

**Quyết định:** Đồng bộ RPC + timeout + fail-closed.

**Hệ quả:** Thêm latency nhỏ; đảm bảo risk trước khi lệnh rời hệ thống.

### ADR-05 — TimescaleDB vs InfluxDB

**Bối cảnh:** Cần time-series OHLCV + SQL quen thuộc + JOIN với ledger Postgres.

**Quyết định:** TimescaleDB (extension Postgres) cho market data/feature time-series ở baseline.

**Hệ quả:** Một operational model với Postgres; tránh dual-skill Influx trừ khi có nhu cầu cardinality cực cao sau này.

### ADR-06 — Feature Store: tự xây vs Feast

**Bối cảnh:** Cần versioning train/serve nhất quán sớm nhưng không muốn nặng ops Phase 1.

**Quyết định:** Phase 1–2: Feature Store mỏng trên Postgres/Timescale (versioned transforms + snapshot IDs). Phase 3: đánh giá Feast nếu số feature/team tăng.

**Hệ quả:** Time-to-MVP nhanh; phải thiết kế interface để thay Feast không viết lại Inference.

### ADR-07 — Claude / LLM sentiment ngoài đường găng

**Bối cảnh:** LLM có độ trễ, chi phí, và rủi ro sẵn có — không được làm hỏng chu kỳ nến.

**Quyết định:** Sentiment là feature phụ trợ bất đồng bộ; Inference không chờ LLM; thiếu sentiment → dùng feature còn lại hoặc bỏ qua, không fail-open sang “guess”.

**Hệ quả:** Edge từ news có thể yếu hơn; đổi lại ổn định latency và FinOps.

### ADR-08 — Đồng tiền báo cáo mặc định USD

**Bối cảnh:** Đa thị trường (USDT, tiền tài khoản MT5, USD CK) cần một reporting currency.

**Quyết định:** Mặc định USD cho equity/P&L hợp nhất; cho phép báo cáo phụ VND với FX rate đã lưu tại thời điểm sự kiện.

**Hệ quả:** Phụ thuộc nguồn FX tin cậy; mọi bút toán phải lưu `fx_rate` + `amount_reporting`.

### ADR-09 — Điều kiện thoát MetaApi → EA bridge

**Bối cảnh:** MetaApi thuận tiện nhưng phí và credential bên thứ ba tăng theo số account.

**Quyết định:** Chuyển EA bridge (hoặc hybrid) khi một trong các điều kiện đúng: (1) chi phí MetaApi > ngưỡng tháng do CTO chốt, (2) sự cố credential/ToS không chấp nhận được, (3) ≥ N account MT5 (N do vận hành chốt ở Giai đoạn 0). Phải có prototype EA bridge trước khi vượt ngưỡng.

**Hệ quả:** Có exit ramp rõ; tránh bị khoá nhà cung cấp.

---

## 13. Security & Compliance Controls

*Đủ để Security Lead / CTO ký gate trước vốn thật*

### Cơ sở mật mã & mạng

| Control | Yêu cầu |
|---|---|
| In-transit | TLS 1.2+ ra Internet; mTLS giữa service nội bộ từ Phase 3 (Phase 1: mạng riêng + TLS tới Gateway tối thiểu) |
| At-rest | Mã hoá volume DB & object storage; secret chỉ trong Vault |
| Network | Tách subnet trading; hạn chế egress; IP allowlist tới sàn nếu hỗ trợ |
| NTP | Bắt buộc (NFR-10) |

### Identity & Access

| Control | Yêu cầu |
|---|---|
| JWT | Access TTL ngắn (ví dụ ≤15 phút); refresh rotation; revoke được |
| RBAC | Vai trò ở Phần 03; kiểm thử RBAC mỗi release |
| Step-up | Bắt buộc cho L3/L4, đổi risk limit, xuất secret, break-glass |
| Break-glass | TTL ≤60 phút; SEV1 audit; post-review ≤24h |
| SoD | Phần 03D — proposer ≠ approver |

### Secrets

| Control | Yêu cầu |
|---|---|
| Lưu trữ | Vault/KMS only; không commit `.env` có secret |
| Rotation | API key/broker credential: tối thiểu mỗi 90 ngày hoặc theo sự cố |
| Audit | Mọi lần đọc secret production có log; cảnh báo đọc bất thường |
| CI | Secret scanning pre-commit + pipeline |

### Application & supply chain

| Control | Yêu cầu |
|---|---|
| Input validation | Gateway + service |
| Dependency | SBOM mỗi build; CVE critical/high có SLA vá (critical ≤7 ngày) |
| Pen-test / review | Gate trước Phase 2 live (nội bộ hoặc bên thứ ba) |
| Logging | Cấm log secret, full card, plaintext password |

### Audit WORM

- Stream audit (quyết định trade, risk-check, kill-switch, dual-control, secret read) → log append-only + archive object-lock/WORM
- Retention ≥5 năm (NFR-02/09) hoặc theo luật áp dụng — lấy mức chặt hơn
- Không có API xoá audit trên prod; ngoại lệ pháp lý phải có ticket + 2 approver

### Data classification (chuẩn bị multi-user)

| Lớp | Ví dụ | Quy tắc |
|---|---|---|
| Secret | API keys, MT5 master password | Vault only |
| Restricted | Vị thế, lệnh, P&L, audit | RBAC + mã hoá at-rest |
| Internal | Config chiến lược không secret | RBAC |
| Public | Docs marketing | — |

Tenant isolation (hồ sơ b/c): mọi query bắt buộc filter `tenant_id`; test xâm nhập chéo là gate Phase 4.

---

## 14. Disaster Recovery & Business Continuity (DR/BCP)

*RPO/RTO có số — không chỉ glossary*

### Tier dữ liệu & mục tiêu phục hồi

| Tier | Dữ liệu | RPO | RTO | Ghi chú |
|---|---|---|---|---|
| T0 | Vault credentials config (không phải giá trị secret thô ngoài Vault) | ≤ 0 (HA) | ≤ 15 phút | Vault HA |
| T1 | Orders, trades, positions, risk_checks, ledger | ≤ 1 phút | ≤ 15 phút | Postgres HA + PITR |
| T2 | Kafka topics audit/order/risk (retention dài) | ≤ 5 phút | ≤ 30 phút | Multi-AZ / replica |
| T3 | Market data hot (Timescale) | ≤ 15 phút | ≤ 1 giờ | Có thể backfill từ sàn |
| T4 | Metrics / logs non-audit | ≤ 1 giờ | ≤ 4 giờ | Không chặn trading nếu thiếu |

### Kiến trúc sẵn sàng

- Postgres: primary + sync/async replica; PITR liên tục; backup mã hoá hàng ngày offsite
- Kafka: tối thiểu 3 broker ở staging/prod có HA; replication factor ≥ 3 cho topic audit/order
- Core Trading: ≥ 2 instance sau Phase 2; health-check fail → không nhận traffic
- Object storage audit: versioning + Object Lock
- MetaApi / MT5: phương án dự phòng theo ADR-09; runbook mất kết nối = L1/L2 không đoán mò

### Single Point of Failure (SPOF) register

| Thành phần | Rủi ro | Giảm thiểu |
|---|---|---|
| Postgres primary | Mất ghi ledger | Auto-failover đã test |
| Kafka controller/quorum | Mất event | RF≥3; monitor ISR |
| Vault | Không đọc secret mới | HA; cache ngắn hạn cấm với trading secrets nếu policy fail-closed |
| MetaApi | Mất MT5 path | L1 + ADR-09 bridge |
| Một region cloud | Mất vùng | Phase 3+: warm standby region cho T1 (tuỳ ngân sách) |

### Backup & drill

| Hạng mục | Tần suất | Tiêu chí pass |
|---|---|---|
| Backup verification | Tuần | Restore sample table thành công |
| DR restore drill (staging) | Quý | Đạt RTO/RPO T1 trên staging |
| Game-day kill-switch + mất DB | Trước mỗi Phase 2 go-live & hàng năm | L3 ≤30s; DB failover trong RTO |
| MetaApi outage drill | 6 tháng | L1 đúng scope; không lệnh mù |

### BCP giao dịch

Khi DR đang chạy: mặc định **fail-closed mở lệnh mới**; ưu tiên bảo vệ vị thế hiện có (stop native). Chỉ flatten hàng loạt (L3) khi Risk Officer/SRE xác nhận không kiểm soát được rủi ro tồn đọng.

---

## 15. Test Strategy & Release Gates

*Không đạt gate = không được đụng tiền thật*

### Test pyramid

| Tầng | Phạm vi | Bắt buộc từ |
|---|---|---|
| Unit | Risk limits, Kelly, FSM chuyển trạng thái, idempotency key | Phase 1 |
| Contract (adapter) | Mock sàn: place/cancel/status/partial/fee/margin | Phase 1 mỗi adapter |
| Integration | Strategy→Risk→OMS→Adapter fake; Kafka schema publish/consume | Phase 1 |
| E2E paper | Full path trên `prod-paper` ≥ N ngày | Phase 1 exit |
| Chaos | Mất ack → UNKNOWN; bus down; Vault down; stale feed; clock skew | Trước Phase 2 |
| Load | Burst NFR-06; OMS p99 | Trước Phase 2 |
| Security | RBAC matrix, secret scan, dependency CVE, pen-test/review | Trước Phase 2 |
| ML validation | Walk-forward, purge/embargo, DSR, calibration | Phase 2+ |

### Chaos scenarios tối thiểu (pass/fail)

| Scenario | Kỳ vọng |
|---|---|
| Timeout ack sau submit | State UNKNOWN → poll status → không nhân đôi lệnh |
| Risk service kill trong lúc signal | Fail-closed; 0 order ra sàn |
| Vault unreachable | 0 order mới; stop native vẫn còn |
| Kafka down | Đường găng đồng bộ vẫn risk-check được từ state local; không mất audit khi recover (outbox/retry) |
| Stale market data | L1 symbol; UI stale |
| Dual-control bypass attempt | API reject; audit SEV1 |

### Definition of Done (DoD) thay đổi liên quan trading

1. Test unit/integration liên quan xanh  
2. Schema compatibility xanh (nếu đụng event)  
3. RBAC/SoD không bị phá  
4. Observability: log/metric/trace cho đường mới  
5. Runbook cập nhật nếu đổi hành vi sự cố  
6. Risk Officer review nếu đụng limit/kill-switch/promote  

### Checklist release

**Phase 1 → prod-paper**

- [ ] Kill-switch L1–L4 hoạt động trên staging  
- [ ] Reconciliation job chạy và alert được  
- [ ] 0 secret trong repo  
- [ ] Paper ≥30 ngày tiêu chí Phần 08  

**Phase 2 → prod-live (vốn ≤5% NAV)**

- [ ] Chaos scenarios trên bảng trên = PASS  
- [ ] Game-day L3 flatten ≤30s trên staging  
- [ ] Restore drill T1 pass trong quý gần nhất  
- [ ] Security review / pen-test gate PASS  
- [ ] Risk Officer ký bảng limit 03D  
- [ ] Capital sizing ghi nhận bằng văn bản  
- [ ] On-call rotation có tên người thật  

**Phase 3 → auto-retrain/canary**

- [ ] MRM Model Card bắt buộc  
- [ ] Dual-control promote >10%  
- [ ] OTel coverage ≥95% đường găng  
- [ ] ≥1 rollback drill thành công <5 phút  

**Phase 4 → multi-user**

- [ ] Sign-off pháp lý hồ sơ (b) hoặc (c)  
- [ ] Tenant isolation tests PASS  
- [ ] ToS sản phẩm + data classification  

---

## A. Phụ lục — Sơ đồ C4 & Sequence

*Trình bày dạng bảng để tránh phụ thuộc công cụ vẽ ngoài*

### C4 — Context

| Actor / Hệ thống ngoài | Tương tác với hệ thống |
|---|---|
| Trader / Operator | Cấu hình, giám sát, kill-switch, đề xuất dual-control |
| Risk Officer / ML Lead / SRE | Phê duyệt limit/promote, xử lý SEV1, DR |
| Sàn / Broker | Market data + lệnh qua Adapter |
| MetaApi (nếu ADR-03) | Cầu MT5 — R-08 / ADR-09 |
| Claude API (tuỳ chọn) | Sentiment ngoài đường găng — ADR-07 |
| Vault / IdP | Secret & (tuỳ chọn) SSO |

### C4 — Container (Phase 1)

| Container | Gồm module | Công nghệ chính |
|---|---|---|
| Core Trading Service | Adapter, Strategy, Risk, OMS, Ledger, Notification | Python/FastAPI, PostgreSQL |
| Data Service | Market Data, Feature Engineering, Market Calendar | Python, TimescaleDB, Kafka |
| AI Service | Training, Inference, Registry/MRM | Python, XGBoost, MLflow |
| Backtesting Engine | Backtesting | Python |
| API Gateway | Auth, OpenAPI, Approvals API | FastAPI, JWT, Vault |
| Observability | Metrics, logs, traces, audit sink | Prometheus, Loki/ELK, OTel, WORM storage |
| Frontend | 9 màn hình (thêm Approvals) + kill-switch | React/Next.js, WebSocket |

### Sequence — Đặt lệnh

```
1. AI Inference sinh signal.generated (xác suất hiệu chỉnh + feature_snapshot_id + trace_id)
2. Strategy Engine nhận signal, định cỡ (Kelly 25%, trừ fee ước tính)
3. Strategy gọi ĐỒNG BỘ Risk Management (RPC + timeout) — kèm calendar/margin/fee
4a. Risk TỪ CHỐI → dừng, ghi risk_checks + audit, không tạo Order
4b. Risk CHẤP THUẬN → Order CREATED → RISK_APPROVED
5. OMS gửi qua Adapter (SUBMITTED); gắn idempotency = client_order_id
6. Ack → ACKNOWLEDGED; timeout → UNKNOWN → bắt buộc get_order_status trước mọi hành động
7. Fill / partial → Portfolio & Ledger + fee.posted + position.updated + order.*
```

### Sequence — Promote model

```
1. Trigger → train challenger (tôn trọng label_available_at) + Model Card
2. Backtest: purge + embargo + walk-forward → DSR + edge kinh tế
3. Không đạt ngưỡng → dừng, ghi registry
4. Đạt → Shadow N ngày
5. N≥100 lệnh shadow ổn định → ML Lead approve canary
6. Canary 10% → theo dõi calibration live → tăng dần
7. Promote 100%: ML Lead; nếu >10% NAV cần Risk Officer (SoD)
8. Suy giảm → auto-rollback <5 phút + SEV1 + model.rolled_back
```

### Sequence — Dual-control đổi risk limit

```
1. Actor A (trader/admin) tạo RiskLimitChange (pending) + audit
2. Thông báo SEV2 tới Risk Officer
3. Actor B (risk_officer, B≠A) duyệt hoặc từ chối kèm lý do
4. Nếu duyệt → Risk Management nạp limit mới atomically + kill_switch/risk events
5. Mọi lệnh sau thời điểm hiệu lực dùng limit mới; không áp dụng ngược lệnh đã SUBMITTED
```

---

*Tài liệu này là Enterprise Architecture Blueprint — mô tả kiến trúc kỹ thuật tham khảo và các gate vận hành, không phải lời khuyên đầu tư, tài chính, hay pháp lý chính thức. Mọi quyết định giao dịch bằng vốn thật, và đặc biệt mọi quyết định mở rộng phục vụ bên thứ ba, cần được cân nhắc rủi ro cẩn thận và tuân thủ quy định pháp luật tại khu vực áp dụng, với tư vấn từ luật sư có chuyên môn phù hợp.*

**Chữ ký phê duyệt (điền khi sign-off):**

| Vai trò | Họ tên | Ngày | Chữ ký / xác nhận |
|---|---|---|---|
| CTO / Kiến trúc sư trưởng |  |  |  |
| Risk Officer |  |  |  |
| SRE Lead |  |  |  |
| Security Lead (hoặc CTO) |  |  |  |
