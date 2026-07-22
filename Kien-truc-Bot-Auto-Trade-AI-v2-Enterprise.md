# Nền tảng Bot Auto-Trade tích hợp AI tự học & tự huấn luyện lại

**TÀI LIỆU KIẾN TRÚC KỸ THUẬT — ENTERPRISE-GRADE**

Phiên bản v2.0 — nâng cấp từ v1.1 theo chuẩn enterprise-grade: đủ để CTO duyệt ngân sách, kỹ sư build không phải tự suy đoán quyết định, risk officer ký duyệt an toàn vốn, và SRE vận hành lúc 3 giờ sáng.

|  |  |
|---|---|
| **PHIÊN BẢN** | v2.0 — xem lịch sử phiên bản ở Phần 00 |
| **PHẠM VI** | Kiến trúc tham khảo enterprise-grade — chưa phải bản thiết kế chi tiết cấp code |
| **THỊ TRƯỜNG** | Áp dụng cho crypto / forex (MT5) / chứng khoán |
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
- **05** — Vòng lặp AI “tự học và làm lại”
- **06** — Bảng phân chia Backend / Frontend theo tính năng
- **07** — Tech stack đề xuất
- **08** — Lộ trình phát triển theo giai đoạn
- **09** — Rủi ro, bảo mật & pháp lý (Risk Register)
- **10** — Kết nối đa nền tảng & tích hợp MT5
- **11** — Vận hành & SRE Runbook
- **12** — Nhật ký quyết định kiến trúc (ADR Log)
- **A** — Phụ lục — Sơ đồ C4 & Sequence

---

## 00. Metadata & Quản trị tài liệu

### Lịch sử phiên bản

| Phiên bản | Ngày | Thay đổi chính | Trạng thái |
|---|---|---|---|
| v1.0 | — | Bản kiến trúc đầu tiên: 13 module BE, 8 màn hình FE, vòng lặp AI 9 bước, bảng phân chia BE/FE. | Đã thay thế |
| v1.1 | — | Bổ sung Exchange/Broker Adapter Layer, Phần 10 (kết nối đa nền tảng & MT5). | Đã thay thế |
| v2.0 | Bản hiện tại | Nâng cấp enterprise-grade: thêm máy trạng thái, data contract, giới hạn rủi ro có số, kill-switch, ADR log, risk register, SRE runbook. | Bản hiện hành — chờ phê duyệt |

### Chủ sở hữu quyết định

| Hạng mục quyết định | Chủ sở hữu |
|---|---|
| Kiến trúc hệ thống & ADR | CTO / Kiến trúc sư trưởng |
| Giới hạn rủi ro & kill-switch | Risk Officer (hoặc Founder ở giai đoạn đội nhỏ) |
| Phê duyệt promote model (champion → production) | ML Lead |
| Pháp lý & tuân thủ (đặc biệt Giai đoạn 4 — SaaS) | Cố vấn pháp lý |
| Ứng phó sự cố (SEV1/SEV2) | SRE / On-call lead |
| Lựa chọn sàn/broker & review ToS | Người phụ trách vận hành giao dịch |

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
| FMEA | Failure Mode and Effects Analysis — bảng phân tích các kiểu lỗi, hệ quả và cách ứng phó. |
| RPO / RTO | Recovery Point/Time Objective — lượng dữ liệu tối đa được phép mất / thời gian tối đa để khôi phục sau sự cố. |

## 01. Tổng quan & yêu cầu hệ thống

Hệ thống cần giải quyết bốn bài toán lớn: (1) lấy và xử lý dữ liệu thị trường liên tục trên nhiều nền tảng, (2) ra quyết định giao dịch dựa trên mô hình AI kết hợp luật quản trị rủi ro, (3) thực thi lệnh an toàn trên sàn/broker, và (4) khiến AI tự học lại khi thị trường thay đổi hoặc hiệu suất suy giảm — không cần con người huấn luyện lại thủ công.

Vì hệ thống chạm vào tiền thật, các yêu cầu dưới đây được đánh số để có thể truy vết trực tiếp từ mã nguồn và kiểm thử ngược lại tài liệu này.

### Yêu cầu chức năng (FR)

| ID | Yêu cầu | Ghi chú |
|---|---|---|
| FR-01 | Hệ thống thu thập, chuẩn hoá dữ liệu thị trường theo thời gian thực từ nhiều nền tảng (crypto/forex/chứng khoán). | Xem Phần 03 (Market Data), Phần 10 (đa nền tảng) |
| FR-02 | Hệ thống sinh tín hiệu giao dịch từ model AI kèm độ tin cậy đã hiệu chỉnh và giải thích được. | Xem Phần 05 |
| FR-03 | Hệ thống tự động đặt/huỷ/theo dõi lệnh trên sàn/broker với đảm bảo không trùng lặp. | Xem Phần 03c |
| FR-04 | Hệ thống thực thi kiểm tra rủi ro trước mọi lệnh và có khả năng ngắt giao dịch theo nhiều mức. | Xem Phần 03d |
| FR-05 | Hệ thống tự động huấn luyện lại model theo lịch hoặc theo sự kiện, kiểm định trước khi thay thế model đang chạy. | Xem Phần 05 |
| FR-06 | Hệ thống cung cấp giao diện giám sát thời gian thực và điều khiển khẩn cấp (kill-switch). | Xem Phần 04 |
| FR-07 | Hệ thống ghi lại đầy đủ lý do cho mọi quyết định giao dịch, truy vấn được sau này. | Xem Phần 03b, Phần 11 |
| FR-08 | Hệ thống đối soát định kỳ giữa dữ liệu nội bộ và dữ liệu từ sàn/broker, phát hiện và xử lý sai lệch. | Xem Phần 03c |

### Yêu cầu phi chức năng (NFR)

| ID | Yêu cầu | Tiêu chí chấp nhận (đo được) |
|---|---|---|
| NFR-01 | An toàn vốn: không lệnh nào được đặt mà bỏ qua kiểm tra rủi ro. | 100% lệnh gửi tới sàn có bản ghi risk-check tương ứng; mọi dependency rủi ro mặc định fail-closed (Phần 03d). |
| NFR-02 | Khả năng truy vết: mọi quyết định giao dịch có thể tái dựng lại lý do. | 100% lệnh có bản ghi audit truy vấn được trong <2 giây; sự kiện lưu tối thiểu 5 năm (điều chỉnh theo quy định áp dụng). |
| NFR-03 | Khả năng rollback: mọi thay đổi model/chiến lược đảo ngược được nhanh chóng. | Rollback model về phiên bản trước hoàn tất trong <5 phút kể từ khi phát hiện suy giảm hiệu suất. |
| NFR-04 | Độ trễ suy luận AI không làm chậm chu kỳ giao dịch. | Độ trễ suy luận < 50% chu kỳ nến của khung thời gian đang giao dịch (đo p99). |
| NFR-05 | Độ khả dụng của đường găng giao dịch (Strategy → Risk → OMS). | Uptime ≥ 99.9% trong giờ thị trường mở; xem SLO chi tiết ở Phần 11. |

> **Ngoài phạm vi:** Tư vấn đầu tư cá nhân hoá, quản lý quỹ được cấp phép chính thức, và mọi hoạt động thuộc hồ sơ pháp lý (c) ở Phần 09 cho tới khi có sign-off pháp lý riêng.

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
| 7 | Risk Management | Kiểm tra giới hạn rủi ro, kill-switch | Strategy → Order Execution | **ĐỒNG BỘ** (RPC, timeout fail-closed) |
| 8 | Order Execution (OMS) | Đặt lệnh qua Adapter, đối soát với sàn | Risk Mgmt → Adapter → Sàn | **ĐỒNG BỘ** tới Adapter |

> **Event Bus:** Kafka cho toàn bộ sự kiện lõi cần audit/replay (candle.closed, signal.generated, order.\*, risk.\*, reconciliation.\*) — quyết định chính thức ở ADR-01, không còn xem Kafka/Redis Streams là hai lựa chọn ngang nhau như bản v1.1.

> **GPU:** AI Inference KHÔNG cần GPU ở baseline (XGBoost/LightGBM chạy CPU). GPU chỉ cần xem xét nếu/khi áp dụng model deep learning (LSTM/Transformer, đang là tuỳ chọn ở Phần 07) — sửa lại tuyên bố "cần GPU" ở bản v1.1.

**[FE]** Frontend chỉ đọc/ghi qua API Gateway (REST) cho thao tác cấu hình và WebSocket cho dữ liệu thời gian thực — không kết nối thẳng vào Event Bus hay các service nội bộ.

## 03. Backend chi tiết theo module

15 module với ranh giới trách nhiệm rõ ràng. Ở Phase 1, phần lớn được gộp thành ít container hơn theo mô hình modular-monolith (xem ADR-02, Phần 12) — ranh giới interface giữa các module vẫn giữ nguyên để tách container thật ở Phase 3-4 là một quyết định dựa trên tải thực tế, không phải giả định ban đầu.

#### **[BE]** API Gateway & Auth

*Phân kỳ triển khai: Container độc lập ngay từ Phase 1 (biên bảo mật rõ, tách sớm).*

*Cửa ngõ duy nhất cho Frontend. Xác thực, phân quyền, chống lạm dụng request.*

- JWT + refresh token, RBAC theo vai trò (admin / trader / viewer)
- Quản lý API key sàn: mã hoá bằng Vault/KMS, không log ra dạng plaintext
- Rate limiting, kiểm tra hợp lệ dữ liệu đầu vào (request validation)

#### **[BE]** Exchange / Broker Adapter Layer

*Phân kỳ triển khai: Module Core trong "Core Trading Service" ở Phase 1; ranh giới interface giữ nguyên để tách container riêng ở Phase 3-4 nếu tải yêu cầu.*

*Lớp trung gian chuẩn hoá mọi khác biệt giữa các sàn/broker sau một interface chung; Market Data Service và OMS gọi qua lớp này chứ không nối thẳng vào từng sàn.*

- Interface thống nhất: connect(), subscribe_market_data(), get_ohlcv(), place_order(), cancel_order(), get_positions(), get_balance()
- Mỗi nền tảng là một adapter cắm rời: Crypto (CCXT — Binance/Bybit/OKX…), MT5 (forex/vàng/chỉ số qua MetaTrader5 hoặc MetaApi), Chứng khoán (Interactive Brokers/Alpaca)
- Chuẩn hoá symbol, khung thời gian và loại lệnh về một định dạng nội bộ duy nhất — có bảng ánh xạ (symbol registry) cho từng adapter
- Che giấu khác biệt kết nối: WebSocket reconnect cho crypto, kiểm tra sức khoẻ terminal cho MT5; phát sự kiện candle.closed đã chuẩn hoá lên Event Bus
- Thêm sàn mới = viết thêm một adapter, không đụng tới Strategy Engine, Risk Management hay lõi AI

#### **[BE]** Market Data Service

*Phân kỳ triển khai: Gộp trong "Data Service" (cùng Feature Engineering) ở Phase 1.*

*Kết nối tới Adapter Layer, chuẩn hoá dữ liệu, phát sự kiện nến mới.*

- Tự động kết nối lại khi mất kết nối sàn (qua Adapter)
- Ghi OHLCV / order book vào time-series DB
- Phát sự kiện candle.closed lên Event Bus cho các service khác dùng

#### **[BE]** Feature Engineering

*Phân kỳ triển khai: Gộp trong "Data Service" ở Phase 1.*

*Biến dữ liệu thô thành đặc trưng (feature) có ý nghĩa cho mô hình AI.*

- Chỉ báo kỹ thuật: RSI, MACD, Bollinger Bands, EMA, ATR...
- Feature Store có version — đảm bảo lúc train và lúc suy luận dùng cùng công thức
- Tuỳ chọn: sentiment tin tức qua LLM làm feature phụ trợ (xem lưu ý độ trễ/chi phí ở Phần 03b)

#### **[AI]** AI Training Pipeline

*Phân kỳ triển khai: Gộp trong "AI Service" ở Phase 1 (cùng Inference + Registry).*

*Huấn luyện ngoại tuyến (offline), chạy trong container cô lập, không ảnh hưởng hệ thống đang chạy thật.*

- Nhận kích hoạt theo lịch định kỳ hoặc theo sự kiện phát hiện drift
- Chia dữ liệu train / validation / test theo thời gian, có purge + embargo (walk-forward nghiêm ngặt — xem Phần 05)
- Đẩy model ứng viên (challenger) vào Model Registry — xem chi tiết vòng lặp ở Phần 05

#### **[AI]** AI Inference Service

*Phân kỳ triển khai: Gộp trong "AI Service" ở Phase 1.*

*Nạp model đang chạy production, sinh tín hiệu giao dịch theo thời gian thực.*

- Đầu vào: feature thời gian thực → đầu ra: xác suất đã hiệu chỉnh P(lợi nhuận > ngưỡng) theo horizon H, không phải điểm confidence thô
- Kèm giải thích (feature importance / SHAP) để hiển thị lên Frontend
- Độ trễ suy luận phải nhỏ hơn 50% thời gian một nến của khung thời gian đang giao dịch (NFR-04)

#### **[AI]** Model Registry

*Phân kỳ triển khai: Gộp trong "AI Service" ở Phase 1.*

*Lưu vết mọi phiên bản mô hình — bắt buộc để rollback và tuân thủ.*

- Lưu: dữ liệu train, hyperparameter, chỉ số hiệu suất, trạng thái champion/challenger
- Công cụ tham khảo: MLflow, hoặc registry tự xây trên PostgreSQL

#### **[BE]** Strategy Engine

*Phân kỳ triển khai: Gộp trong "Core Trading Service" ở Phase 1.*

*Kết hợp tín hiệu AI với các luật lọc bổ sung để ra quyết định cuối cùng.*

- Bộ lọc chế độ thị trường (trending / sideways), lọc thanh khoản
- Định cỡ vị thế: Kelly criterion giới hạn ở 25% full-Kelly, đầu vào là xác suất đã hiệu chỉnh (không phải confidence thô — xem Phần 05)
- Gọi Risk Management theo kiểu ĐỒNG BỘ (RPC + timeout, fail-closed) — xem Phần 02

#### **[BE]** Risk Management

*Phân kỳ triển khai: Gộp trong "Core Trading Service" ở Phase 1 — KHÔNG được tối giản hoá hay bỏ qua dù gộp module.*

*Tuyến phòng thủ cuối cùng trước khi lệnh chạm tới sàn thật.*

- Thực thi phân cấp giới hạn rủi ro có số (Phần 03d), không cho phép Strategy Engine tự vượt qua
- Kill-switch 4 mức (L1-L4) — Phần 03d
- Giới hạn exposure theo tài sản, kiểm tra tương quan giữa các bot đang chạy

#### **[BE]** Order Execution (OMS)

*Phân kỳ triển khai: Gộp trong "Core Trading Service" ở Phase 1.*

*Đặt / huỷ lệnh qua Adapter Layer, đảm bảo không đặt trùng khi có lỗi mạng.*

- Máy trạng thái lệnh đầy đủ, bao gồm trạng thái UNKNOWN khi mất ack (Phần 03c)
- Idempotency key cho mỗi lệnh; từ trạng thái UNKNOWN bắt buộc truy vấn trước khi retry — không bao giờ gửi lại mù
- Xử lý khớp một phần (partial fill), đối soát định kỳ với sàn (Phần 03c)

#### **[BE]** Portfolio & Ledger

*Phân kỳ triển khai: Gộp trong "Core Trading Service" ở Phase 1.*

*Sổ cái ghi nhận ý định và lịch sử giao dịch; đối soát VỀ PHÍA sàn/broker (sàn là sự thật cho vị thế/số dư hiện tại).*

- Thiết kế kiểu double-entry, có quy đổi đa tiền tệ về một đồng tiền báo cáo (Phần 10)
- Khi lệch với sàn: sàn thắng, ledger được sửa theo, chênh lệch ghi thành sự kiện audit (Phần 03c)
- Tính lãi/lỗ theo thời gian thực để Frontend hiển thị

#### **[BE]** Backtesting Engine

*Phân kỳ triển khai: Container riêng — tải tính toán theo đợt, tách biệt khỏi đường găng giao dịch ngay từ Phase 1.*

*Mô phỏng chiến lược / model trên dữ liệu lịch sử trước khi cho chạy thật.*

- Tính Sharpe, Sortino, Max Drawdown, Win rate, và PSR/DSR khi so sánh nhiều model (Phần 05)
- Walk-forward + purge + embargo để tránh việc mô hình học vẹt (overfit)
- Chạy dưới dạng job bất đồng bộ vì có thể mất vài phút

#### **[BE]** Notification Service

*Phân kỳ triển khai: Gộp trong "Core Trading Service" ở Phase 1.*

*Đẩy cảnh báo khi có sự kiện cần con người chú ý, theo phân cấp mức độ nghiêm trọng (Phần 11).*

- Kênh: email, Telegram, push notification, kênh page riêng cho SEV1
- Sự kiện: lệnh khớp lớn, vượt ngưỡng drawdown, model bị rollback, lệch đối soát

#### **[BE]** Observability Stack

*Phân kỳ triển khai: Hạ tầng dùng chung, triển khai song song từ Phase 1 — không hoãn tới sau.*

*Không thể vận hành một hệ thống chạm tới tiền thật mà thiếu khả năng quan sát.*

- Log tập trung (ELK/Loki), metrics (Prometheus/Grafana) theo bộ SLO/SLI ở Phần 11
- Audit trail bất biến (append-only): mọi quyết định giao dịch lưu lại lý do, truy vết được về sau

## 03B. Mô hình dữ liệu & Data Contracts
*Ngôn ngữ chung bắt buộc để 15 module ở Phần 03 ăn khớp với nhau*

### Domain model

| Entity | Mô tả | Bất biến chính |
|---|---|---|
| Order | Một lệnh gửi tới sàn/broker. | Có đúng 1 trạng thái tại một thời điểm (Phần 03c); client_order_id duy nhất toàn hệ thống. |
| Position | Vị thế đang mở trên một symbol/account. | Số lượng + giá vốn phải khớp giữa ledger và sàn sau mỗi lần đối soát. |
| Trade | Một lần khớp lệnh (có thể một Order sinh nhiều Trade do khớp một phần). | Tổng khối lượng các Trade của một Order không vượt quá khối lượng Order gốc. |
| Account | Tài khoản giao dịch trên một broker/sàn cụ thể. | Thuộc đúng một Adapter; số dư luôn đối chiếu được với sàn. |
| Strategy | Một cấu hình chiến lược (tham số + model gắn kèm + giới hạn rủi ro riêng). | Không được vượt giới hạn rủi ro cấp Account/Portfolio dù cấu hình riêng nới hơn. |
| Model | Một phiên bản model AI trong Model Registry. | Bất biến sau khi publish (immutable); trạng thái champion/challenger/retired không ghi đè lịch sử. |
| Signal | Một tín hiệu AI Inference sinh ra tại một thời điểm. | Luôn gắn với đúng một Model version và một feature snapshot — truy vết được nguồn gốc. |

### Schema sự kiện (Event Bus)

Chính sách versioning: chỉ được thêm field mới (additive-only) trong cùng một major version; đổi kiểu dữ liệu hoặc xoá field bắt buộc tăng major version và chạy song song 2 phiên bản trong giai đoạn chuyển tiếp.

**`candle.closed  (v1)`**

```
symbol: string        // định dạng nội bộ chuẩn hoá, vd BTC-USDT, EURUSD
adapter: string        // "ccxt.binance" | "mt5" | "ibkr" ...
timeframe: string      // "1m" | "5m" | "1h" ...
open_time_utc: datetime
close_time_utc: datetime
ohlcv: { open, high, low, close, volume }
ingested_at_utc: datetime   // thời điểm hệ thống nhận được (khác open/close time)
schema_version: 1
```

**`signal.generated  (v1)`**

```
signal_id: uuid
symbol: string
model_id: string        // trỏ tới Model Registry
model_version: string
prediction_target: string   // vd "P(return_4h > cost_threshold)"
probability_calibrated: float  // 0..1, đã hiệu chỉnh (Phần 05)
feature_snapshot_id: string
generated_at_utc: datetime
schema_version: 1
```

**`order.submitted / .acknowledged / .filled / .canceled / .rejected  (v1)`**

```
client_order_id: uuid   // do hệ thống sinh, dùng làm idempotency key
broker_order_id: string | null
symbol: string
side: "buy" | "sell"
state: string          // xem máy trạng thái, Phần 03c
signal_id: uuid | null // null nếu là lệnh thủ công
risk_check_id: uuid    // bắt buộc — không có = không được submit (NFR-01)
timestamp_utc: datetime
schema_version: 1
```

**`risk.limit_breached  (v1)`**

```
account_id: string
limit_type: string      // vd "daily_drawdown" | "per_symbol_exposure"
threshold: number
observed_value: number
action_taken: string    // "L1_PAUSE" | "L2_HALT" | "L3_FLATTEN" | "L4_LOCKDOWN"
timestamp_utc: datetime
schema_version: 1
```

**`reconciliation.break_detected  (v1)`**

```
account_id: string
break_type: string      // "position" | "cash" | "trade" | "fee"
internal_value: number
broker_value: number
status: string          // "INVESTIGATING" | "RESOLVED"
detected_at_utc: datetime
schema_version: 1
```

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

> **Nguồn sự thật:** khi ledger nội bộ và sàn/broker lệch nhau, SÀN LUÔN THẮNG. Ledger nội bộ là hệ thống ghi nhận ý định và lịch sử, không phải nguồn sự thật cho vị thế/số dư hiện tại — sửa lại cách diễn đạt ở bản v1.1.

### Enforce Stop-loss / Take-profit theo từng adapter

| Adapter | Cơ chế | Rủi ro tồn dư |
|---|---|---|
| Crypto (CCXT) | Ưu tiên stop-order native trên sàn khi hỗ trợ (stop-market/stop-limit). | Sàn có thể tạm ngừng khớp stop trong biến động cực đoan (circuit breaker của sàn) — cần watchdog dự phòng. |
| MT5 (official / MetaApi) | SL/TP gắn native vào lệnh MT5. | Nếu dùng MetaApi, phụ thuộc uptime bên thứ ba; terminal ngắt kết nối có thể trễ việc sửa/huỷ stop. |
| Chứng khoán (IBKR/Alpaca) | Stop order native qua broker. | Giờ ngoài phiên hoặc halted symbol: stop có thể không khớp đúng giá kỳ vọng (gap risk). |
| Trường hợp chỉ có synthetic stop | Hệ thống tự giám sát giá và tự gửi lệnh đóng khi chạm ngưỡng. | Watchdog bắt buộc: nếu khoảng gián đoạn giám sát > ngưỡng định nghĩa (Phần 11), tự động L3 FLATTEN vị thế liên quan. |

## 03D. Phân cấp giới hạn rủi ro & Kill-Switch
*Con số để Risk Officer thật sự có thể ký duyệt*

### Bảng giới hạn rủi ro (mặc định đề xuất — cần tinh chỉnh theo khẩu vị rủi ro thật)

| Loại giới hạn | Mặc định đề xuất | Ghi chú |
|---|---|---|
| Rủi ro tối đa / lệnh | ≤ 1% vốn chủ sở hữu | Tính trên khoảng cách entry–stop loss × khối lượng. |
| Exposure tối đa / symbol | ≤ 20% vốn chủ sở hữu | Cộng dồn mọi vị thế đang mở trên cùng symbol. |
| Exposure tối đa / strategy | ≤ 30% vốn chủ sở hữu | Áp dụng dù cấu hình chiến lược có đặt tham số nới hơn (FR ràng buộc ở Portfolio, không phải Strategy). |
| Gross exposure toàn danh mục | ≤ 150% vốn (≤100% nếu không dùng đòn bẩy) | Kiểm tra trước mỗi lệnh mới ở Risk Management. |
| Ngưỡng dừng trong ngày | Lỗ −3% vốn → L1; −5% vốn → L3 | Tính theo múi giờ giao dịch chính của tài khoản. |
| Ngưỡng dừng 7 ngày trượt | Lỗ −8% vốn → L2, chờ review thủ công | Không tự resume — cần xác nhận của Risk Officer. |
| Số lệnh thua liên tiếp | 6 lệnh → tự tạm dừng chiến lược (L1 cho strategy đó) | Reset bộ đếm khi có 1 lệnh thắng hoặc khi resume thủ công. |
| Giới hạn tương quan | Tối đa 3 vị thế mở đồng thời có tương quan cặp > 0.7 | Tính trên cửa sổ trượt 30 ngày gần nhất. |
| Định cỡ vị thế (Kelly) | Tối đa 25% full-Kelly | Đầu vào là xác suất đã hiệu chỉnh + tỷ lệ lãi/lỗ thực đo từ walk-forward (Phần 05), không dùng confidence thô. |

### Taxonomy Kill-Switch

| Mức | Tên | Phạm vi hành động | Kích hoạt bởi | Điều kiện khôi phục |
|---|---|---|---|---|
| L1 | PAUSE_NEW_ENTRIES | Dừng mở vị thế mới; vị thế hiện có tiếp tục được quản lý bình thường. | Tự động (ngưỡng lệch chuẩn) hoặc thủ công | Tự resume khi điều kiện kích hoạt hết hiệu lực, hoặc xác nhận thủ công. |
| L2 | HALT_ALL_ORDERS | Huỷ mọi lệnh đang chờ; không lệnh mới; vị thế hiện có giữ nguyên với stop vẫn hoạt động. | Tự động (reconciliation break, mất kết nối sàn) hoặc thủ công | Cần xác nhận thủ công của người vận hành sau khi nguyên nhân được xử lý. |
| L3 | FLATTEN_ALL | Đóng thị trường toàn bộ vị thế + huỷ mọi lệnh, SLA thực thi ví dụ ≤30s cho tài sản thanh khoản cao. | Tự động (vượt ngưỡng dừng ngày) hoặc thủ công (nút khẩn trên FE) | Chỉ resume thủ công, sau khi Risk Officer xác nhận nguyên nhân. |
| L4 | FULL_LOCKDOWN | L3 + thu hồi quyền trade của API key/tài khoản khi sàn hỗ trợ. | Chỉ thủ công | Bắt buộc xác nhận 2 người (two-person rule) để mở lại. |

### Ma trận Fail-open / Fail-closed

Quy tắc NFR-01: mọi đường liên quan tới rủi ro mặc định FAIL-CLOSED (không kiểm tra được = không có lệnh), trừ các ngoại lệ liệt kê rõ ràng dưới đây.

| Dependency | Mặc định | Chi tiết |
|---|---|---|
| Risk Management không phản hồi | Fail-closed | Strategy Engine chặn mọi lệnh mới cho tới khi Risk Management phản hồi lại (đường găng đồng bộ — Phần 02). |
| Vault/KMS không truy cập được | Fail-closed | Chặn đặt lệnh mới và chặn đọc credential mới; stop-loss native trên sàn (không cần đọc lại secret) vẫn hoạt động. |
| Event Bus down/phân mảnh | Fail-closed cho đường găng; fail-open cho hiển thị | Đường Strategy→Risk→OMS không đi qua bus (đã là đồng bộ); dừng nhận tín hiệu mới cho tới khi bus phục hồi. FE có thể hiển thị dữ liệu cũ kèm cảnh báo "stale". |
| Feed dữ liệu thị trường chết | Fail-closed cho symbol bị ảnh hưởng | Dừng mở vị thế mới trên symbol đó (L1 cục bộ); vị thế hiện có dùng stop native nếu có. |
| Model Registry/Inference không phản hồi | Fail-closed | Không có tín hiệu mới = không có lệnh mới; hệ thống không tự chọn "chạy theo luật mặc định" khi thiếu tín hiệu AI. |

## 04. Frontend chi tiết theo màn hình

Frontend là lớp giám sát & điều khiển — không tự xử lý logic giao dịch, chỉ hiển thị trạng thái từ Backend và gửi lệnh cấu hình. Bổ sung so với v1.1: control kill-switch toàn cục và phân cấp mức độ cảnh báo.

#### **[FE]** Dashboard tổng quan

*Màn hình mở đầu — trả lời câu hỏi "mọi thứ có ổn không" trong vài giây.*

- Equity curve, lãi/lỗ hôm nay và tổng (theo đồng tiền báo cáo hợp nhất — Phần 10), số bot đang chạy
- Cảnh báo gần nhất kèm mức độ nghiêm trọng SEV1/2/3, trạng thái kết nối sàn

#### **[FE]** Thanh điều khiển khẩn cấp (Kill-switch)

*Control toàn cục, luôn hiện diện trên mọi màn hình — không chỉ riêng một trang.*

- Hiện 4 mức L1-L4 (Phần 03d); L3/L4 bắt buộc hộp thoại xác nhận
- Hiển thị trạng thái hiện tại của từng account/strategy (đang chạy / đã tạm dừng / đã khoá)

#### **[FE]** Strategy / Bot Builder

*Nơi cấu hình một bot: cặp giao dịch, khung thời gian, model AI, tham số rủi ro.*

- Giai đoạn đầu: form có kiểm tra hợp lệ; giai đoạn sau: builder dạng kéo-thả
- Không cho phép đặt giới hạn rủi ro riêng vượt giới hạn cấp Account/Portfolio (ràng buộc phía Backend, FE chỉ phản ánh)

#### **[FE]** AI Model Center

*Nơi con người giám sát "bộ não" của bot đang làm gì.*

- Danh sách phiên bản model, biểu đồ chỉ số hiệu suất theo thời gian, biểu đồ PSR/DSR
- Trạng thái champion / challenger / shadow / canary, log phát hiện drift
- Nút "Huấn luyện lại thủ công" dùng cho trường hợp khẩn cấp — yêu cầu xác nhận

#### **[FE]** Backtest Studio

*Thử chiến lược trên dữ liệu quá khứ trước khi tin tưởng đưa vào chạy thật.*

- Form cấu hình khoảng thời gian, vốn ban đầu, phí giao dịch, mô hình slippage
- Biểu đồ equity curve, drawdown; so sánh nhiều lần chạy cạnh nhau kèm PSR/DSR

#### **[FE]** Live Monitor

*Phòng điều khiển thời gian thực khi bot đang giao dịch bằng tiền thật.*

- Biểu đồ nến thời gian thực, overlay tín hiệu AI kèm xác suất đã hiệu chỉnh
- Danh sách lệnh theo đúng trạng thái ở Phần 03c (kể cả trạng thái UNKNOWN nếu có), log hệ thống dạng luồng qua WebSocket
- Chỉ báo dữ liệu "cũ" (stale) rõ ràng khi feed gián đoạn — không hiển thị giá cũ như giá hiện tại

#### **[FE]** Account & API Key

*Nơi nhạy cảm nhất về bảo mật trong toàn bộ Frontend.*

- Nhập API key sàn một lần, chỉ hiển thị dạng che (masked) sau đó
- Nhắc người dùng chỉ cấp quyền giao dịch, tắt quyền rút tiền; với MT5 nhắc phân biệt master/investor password

#### **[FE]** Alerts & Notification

*Cấu hình khi nào và qua kênh nào hệ thống được phép làm phiền người dùng.*

- Chọn kênh theo mức độ nghiêm trọng: SEV1 → kênh page có escalation; SEV2 → chat ngay; SEV3 → tổng hợp định kỳ (Phần 11)

#### **[FE]** Reports & History

*Nhìn lại — phục vụ đánh giá hiệu suất và đối soát kế toán.*

- Bảng lịch sử giao dịch có bộ lọc, xuất file CSV, quy đổi P&L theo đồng tiền báo cáo
- Báo cáo hiệu suất theo tuần / tháng

## 05. Vòng lặp AI “tự học và làm lại”

Đây là phần khác biệt hệ thống này với một bot rule-based thông thường: mô hình tự phát hiện khi nó đang “đuối” và tự thay thế chính mình một cách có kiểm soát.

### Prediction target

```
target = P( lợi_nhuận(H nến tiếp theo) > ngưỡng_đã_trừ_chi_phí )
// H = horizon, cấu hình theo khung thời gian của chiến lược
// Bắt buộc hiệu chỉnh xác suất (Platt scaling / isotonic regression),
//   kiểm tra bằng reliability diagram trước khi đưa vào Kelly sizing (Phần 03)
```

Toàn bộ 9 bước dưới đây giữ cấu trúc v1.1, bổ sung cơ chế cụ thể để chống rò rỉ dữ liệu và chống overfitting khi so sánh nhiều model.

**Bước 1 — Thu thập dữ liệu liên tục**

Market Data cùng kết quả giao dịch thực tế được ghi lại. Mỗi nhãn mang timestamp label_available_at = thời điểm LỆNH ĐÓNG (không phải thời điểm mở) — tránh rò rỉ nhãn từ tương lai vào dữ liệu train.

**Bước 2 — Feature Store có version**

Đặc trưng được tính và lưu có phiên bản, đảm bảo dữ liệu train và dữ liệu suy luận luôn khớp công thức.

**Bước 3 — Kích hoạt huấn luyện lại**

Theo lịch (ví dụ mỗi tuần) hoặc theo sự kiện: hiệu suất live giảm dưới ngưỡng, hoặc phát hiện drift (PSI, KS-test) — phân biệt rõ feature drift, concept drift và performance decay, mỗi loại có ngưỡng riêng.

**Bước 4 — Huấn luyện model ứng viên**

Training job chạy cô lập trong container riêng, sinh ra một "challenger". Dữ liệu train tại thời điểm snapshot loại bỏ mọi mẫu có label_available_at sau thời điểm snapshot. Áp dụng purge (loại mẫu train có cửa sổ nhãn chồng lấn tập test) và embargo period sau mỗi fold test.

**Bước 5 — Kiểm định trên dữ liệu holdout**

Backtest challenger. Điều kiện đi tiếp: Deflated Sharpe Ratio (DSR) > 0 ở độ tin cậy 95% có hiệu chỉnh theo số lần thử của Optuna trong chu kỳ đó (chống overfitting do so sánh bội), VÀ edge ròng sau phí/trượt giá ≥ 2× chi phí round-trip (ý nghĩa kinh tế, không chỉ thống kê), VÀ tối thiểu N≥100 lệnh trong giai đoạn shadow trước khi canary.

**Bước 6 — Shadow / Paper trading**

Challenger chạy song song với champion trên dữ liệu live nhưng KHÔNG đặt lệnh thật, trong N ngày để kiểm chứng ngoài dữ liệu lịch sử.

**Bước 7 — Canary rollout có kiểm soát**

Nếu vượt qua giai đoạn shadow, challenger được cấp một phần vốn nhỏ (ví dụ 10%) thật, theo dõi sát rồi mới tăng dần lên 100%. Yêu cầu xác nhận thủ công của ML Lead trước khi promote 100% (Phần 00).

**Bước 8 — Rollback tự động**

Nếu sau khi lên production, model mới hoạt động dưới ngưỡng an toàn, hệ thống tự quay lại phiên bản trước trong <5 phút (NFR-03) và báo động SEV1 cho quản trị viên.

**Bước 9 — Ghi vết vào Model Registry**

Mọi phiên bản — kể cả bản bị loại — được lưu đầy đủ metadata để truy vết và cải thiện lần huấn luyện sau. Bước này quay lại Bước 1, tạo thành vòng lặp chạy liên tục, không có điểm kết thúc.

## 06. Bảng phân chia Backend / Frontend theo tính năng

Nguyên tắc xuyên suốt: Backend giữ mọi logic và trạng thái sự thật; Frontend chỉ hiển thị và thu thập input. Không có tính toán tài chính nào chạy ở phía client.

| Tính năng | Backend chịu trách nhiệm | Frontend chịu trách nhiệm | Giao tiếp qua |
|---|---|---|---|
| Đăng nhập / xác thực | Phát JWT, refresh token, kiểm tra RBAC | Form đăng nhập, lưu token an toàn, điều hướng theo quyền | REST |
| API key sàn giao dịch | Mã hoá lưu trữ (Vault/KMS), xác minh quyền hạn của key (chặn quyền rút tiền) | Form nhập key, hiển thị dạng che, trạng thái kết nối | REST |
| Cấu hình bot / chiến lược | Kiểm tra hợp lệ tham số (kể cả không vượt giới hạn rủi ro cấp trên), lưu cấu hình, khởi tạo worker chạy bot | Form / Builder trực quan, xem trước cấu hình | REST + WS |
| Dữ liệu thị trường | Lấy từ Adapter, chuẩn hoá, phát qua kênh thời gian thực | Subscribe kênh, vẽ biểu đồ nến / order book, hiển thị cảnh báo stale khi feed cũ | WebSocket |
| Tín hiệu AI & lý do | Sinh tín hiệu, xác suất hiệu chỉnh, feature importance để giải thích | Overlay lên biểu đồ, tooltip giải thích quyết định | WS + REST |
| Đặt / huỷ lệnh thủ công | Kiểm tra rủi ro đồng bộ trước khi chuyển lệnh tới sàn | Nút Buy/Sell, hộp thoại xác nhận rõ ràng, không hiển thị "đã khớp" cho tới khi Backend xác nhận | REST |
| Kill-switch toàn cục | Thực thi 4 mức L1-L4, ghi audit event cho mọi lần kích hoạt | Control thường trực trên mọi màn hình, xác nhận bắt buộc cho L3/L4 | REST + WS |
| Giám sát vị thế & P&L | Tính toán thời gian thực từ ledger, quy đổi đa tiền tệ | Bảng vị thế, biểu đồ lãi/lỗ | WS + REST |
| Backtest | Chạy mô phỏng bất đồng bộ, trả kết quả khi hoàn tất kèm PSR/DSR | Form cấu hình, theo dõi tiến độ job, hiển thị kết quả | REST + WS |
| Quản lý model AI | Model Registry API, kích hoạt training job, gate xác nhận thủ công trước promote 100% | Danh sách phiên bản, biểu đồ so sánh chỉ số, nút huấn luyện lại | REST |
| Cảnh báo / thông báo | Rule engine phát hiện sự kiện theo mức SEV1/2/3, gửi qua kênh, lưu lịch sử | Trang cấu hình ngưỡng, danh sách thông báo | REST + WS |
| Báo cáo lịch sử | Truy vấn có phân trang, xuất file CSV | Bảng có bộ lọc, nút tải xuống | REST |

## 07. Tech stack đề xuất

Ưu tiên hệ sinh thái Python cho phần AI (nhiều thư viện nhất), tách riêng phần thực thi lệnh nếu cần độ trễ thấp. Các quyết định có đánh dấu ADR đã được ghi chính thức ở Phần 12.

**BE — Dịch vụ & hạ tầng dữ liệu**

- Python · FastAPI
- PostgreSQL
- TimescaleDB / InfluxDB
- Redis (cache/tín hiệu nội bộ phi audit — không dùng cho event bus lõi, xem ADR-01)
- Kafka (event bus lõi — ADR-01)
- Docker + Kubernetes (từ Phase 3; Phase 1 dùng Docker Compose — ADR-02)

**BE — Kết nối sàn / broker (adapter)**

- CCXT — thư viện thống nhất cho nhiều sàn crypto
- MetaTrader5 (Python, official) hoặc MetaApi (cloud) cho MT5/MT4 — quyết định ở ADR-03
- ib_insync (Interactive Brokers) / Alpaca cho chứng khoán

**AI/ML — Mô hình & huấn luyện**

- scikit-learn / XGBoost / LightGBM — baseline, chạy CPU, KHÔNG cần GPU
- PyTorch (LSTM/Transformer) — tuỳ chọn tương lai, chỉ khi cần deep learning mới xét GPU
- Optuna (tuning, có hiệu chỉnh multiple-testing khi đánh giá kết quả — Phần 05)
- MLflow (registry)
- Claude API (sentiment tin tức, tuỳ chọn — cần đánh giá độ trễ/chi phí/rủi ro sẵn có trước khi đưa vào đường găng)

**FE — Giao diện**

- React + Next.js + TypeScript
- TailwindCSS
- TradingView Lightweight Charts
- WebSocket client — có resume-from-sequence khi reconnect, tránh mất fill
- React Query / Zustand

**Vận hành**

- GitHub Actions (CI/CD)
- Prometheus + Grafana
- ELK / Loki
- HashiCorp Vault

## 08. Lộ trình phát triển theo giai đoạn

Nguyên tắc: chạy paper trading (lệnh giả) cho tới khi cả Backtest lẫn Shadow trading đều ổn định, mới chuyển sang vốn thật — bắt đầu với số vốn nhỏ. Mỗi giai đoạn có tiêu chí thoát đo được — không chỉ mốc thời gian.

| Giai đoạn | Thời gian | Mục tiêu | Mô tả | Tiêu chí thoát |
|---|---|---|---|---|
| Giai đoạn 0 | 2–4 tuần | Chuẩn bị | Chọn thị trường mục tiêu và sàn/broker có API phù hợp, review ToS về automated trading, rà soát yêu cầu pháp lý, thiết kế schema dữ liệu, chốt ADR-01/02/03. | Toàn bộ ADR-01..03 đã ký; risk register khởi tạo; review ToS hoàn tất cho từng broker mục tiêu. |
| Giai đoạn 1 | 4–6 tuần | MVP nền tảng | Core Trading Service (modular-monolith) + Data Service + Backtesting Engine + 1 chiến lược rule-based đơn giản + Dashboard cơ bản + kill-switch. Chạy paper trading. | ≥30 ngày paper trading liên tục, 0 bug nghiêm trọng, 0 lệch đối soát chưa xử lý. |
| Giai đoạn 2 | 6–8 tuần | Tích hợp AI | AI Service (Feature Store + XGBoost baseline + Inference) + Strategy Engine kết hợp tín hiệu AI. Live trading vốn nhỏ, đủ giới hạn rủi ro Phần 03d. | Vốn thật ở mức thử nghiệm chạy ≥4 tuần trong giới hạn drawdown đã định, không có lần kill-switch nào do lỗi hệ thống (chỉ do thị trường). |
| Giai đoạn 3 | 6–8 tuần | Tự động hoá học lại | Training Pipeline tự động, Model Registry, phát hiện drift, Shadow/Canary deployment, AI Model Center trên Frontend, SRE runbook đầy đủ. | ≥3 lần promote qua canary thành công, 0 lần auto-rollback do lỗi triển khai (chỉ do model thật sự kém). |
| Giai đoạn 4 | Liên tục | Mở rộng | Đa chiến lược/đa model, Strategy Builder no-code, tối ưu hạ tầng; mở rộng đa người dùng CHỈ SAU khi hoàn tất review pháp lý. | Review pháp lý (Phần 09) hoàn tất và có sign-off bằng văn bản trước khi onboard người dùng thứ ba đầu tiên — không có ngoại lệ. |

## 09. Rủi ro, bảo mật & pháp lý
*Risk Register chính thức*

| ID | Hạng mục | Khả năng | Ảnh hưởng | Chủ sở hữu | Biện pháp / Trạng thái |
|---|---|---|---|---|---|
| R-01 | API key: chỉ cấp quyền trade, không rút tiền | Trung bình | Cao | Người vận hành | Đã có quy trình; review định kỳ mỗi quý |
| R-02 | Circuit breaker / kill-switch không đủ nhanh | Thấp | Cao | Risk Officer | Định nghĩa SLA thực thi L3 ≤30s (Phần 03d); cần đo bằng test tải trước go-live |
| R-03 | Đặt lệnh trùng do retry mù | Trung bình | Cao | BE Lead | Máy trạng thái + idempotency (Phần 03c) — cần test chaos trước go-live |
| R-04 | Overfitting khi backtest / promote model kém | Cao | Cao | ML Lead | PSR/DSR + ngưỡng kinh tế (Phần 05) — theo dõi hiệu suất live vs backtest hàng tuần |
| R-05 | Audit trail không đầy đủ để truy vết quyết định | Thấp | Trung bình | SRE Lead | Data contract + append-only log (Phần 03b, 11) |
| R-06 | Ràng buộc pháp lý khi mở SaaS cho bên thứ ba | Cao | Rất cao (có thể chấm dứt dự án) | Cố vấn pháp lý | Gate cứng trước Giai đoạn 4 — xem bảng hồ sơ pháp lý bên dưới |
| R-07 | Vi phạm ToS broker/sàn về automated/bridge trading | Trung bình | Cao (đóng băng tài khoản) | Người vận hành | Review ToS từng broker ở Giai đoạn 0, ghi vào hồ sơ nhà cung cấp |
| R-08 | Lệ thuộc bên thứ ba (MetaApi) nắm giữ credential MT5 | Trung bình | Trung bình | CTO | Đánh giá rủi ro nhà cung cấp trước khi chọn (ADR-03); có phương án dự phòng EA bridge tự viết |

### Ba hồ sơ pháp lý — không được gộp làm một

Lộ trình ở Phần 08 hiện trôi dần từ (a) sang (c) theo các giai đoạn mà không có điểm dừng tường minh. Đây chính là khoảng trống pháp lý nghiêm trọng nhất của bản v1.1.

| Hồ sơ | Mô tả | Rủi ro / Yêu cầu |
|---|---|---|
| (a) Tự doanh vốn riêng | Chủ dự án dùng bot để trade vốn của chính mình. | Rủi ro pháp lý thấp nhất; vẫn cần lưu ý quy định thuế và (với forex) Pháp lệnh ngoại hối nếu giao dịch qua broker offshore không được cấp phép tại Việt Nam. |
| (b) Cung cấp phần mềm cho người tự trade | Người dùng tự kết nối tài khoản, tự chịu trách nhiệm quyết định; nền tảng chỉ cung cấp công cụ. | Cần điều khoản sử dụng (ToS) rõ ràng, giới hạn trách nhiệm, và KHÔNG được tự động hoá quyết định thay người dùng theo cách bị coi là tư vấn đầu tư. |
| (c) Quản lý vốn hộ người khác (SaaS quản lý danh mục) | Nền tảng trực tiếp ra quyết định và quản lý vốn của bên thứ ba. | Nhóm rủi ro cao nhất — có thể chạm ngưỡng hoạt động quản lý quỹ/môi giới cần cấp phép. Lộ trình Giai đoạn 4 hiện đang trôi dần từ (a) sang (c) mà không có điểm dừng — BẮT BUỘC có gate pháp lý tường minh trước khi tiến vào (c). |

### Threat model rút gọn (STRIDE)

| Thành phần | Mối đe doạ tiêu biểu | Biện pháp |
|---|---|---|
| API Gateway | Giả mạo danh tính (spoofing), leo thang quyền qua RBAC lỗi | Xác thực JWT ngắn hạn + refresh; kiểm thử RBAC là một phần test bắt buộc trước mỗi release |
| Vault / KMS | Lộ secret qua log hoặc qua service bị xâm nhập đọc trực tiếp | Không log giá trị secret ở bất kỳ tầng nào; service auth riêng (AppRole/mTLS), xoay khoá định kỳ |
| OMS | Session Frontend bị chiếm, dùng để đặt lệnh trái phép | Xác nhận bắt buộc cho hành động nguy hiểm; giới hạn rủi ro ở Backend không thể bị FE ghi đè |
| Model Registry / Training Pipeline | Đầu độc dữ liệu huấn luyện (data poisoning) làm model học sai có chủ đích | Kiểm tra tính toàn vẹn dữ liệu train, giới hạn ai được ghi vào Feature Store production, gate xác nhận thủ công trước promote |

---

*Tài liệu này mô tả kiến trúc kỹ thuật tham khảo, không phải lời khuyên đầu tư, tài chính, hay pháp lý chính thức. Mọi quyết định giao dịch bằng vốn thật, và đặc biệt mọi quyết định mở rộng phục vụ bên thứ ba, cần được cân nhắc rủi ro cẩn thận và tuân thủ quy định pháp luật tại khu vực áp dụng, với tư vấn từ luật sư có chuyên môn phù hợp.*

## 10. Kết nối đa nền tảng & tích hợp MT5

Phần này chi tiết hoá lớp Exchange/Broker Adapter đã nêu ở Phần 03: cách một hệ thống thống nhất kết nối đồng thời crypto, forex/MT5 và chứng khoán. Nguyên tắc cốt lõi: mọi khác biệt của từng nền tảng bị cô lập trong adapter, còn phần lõi (AI, Strategy, Risk, OMS) chỉ làm việc với một mô hình dữ liệu duy nhất.

MT5 không có “API đám mây” như một sàn crypto. Sàn crypto cho REST + WebSocket qua HTTPS, gọi thẳng từ service Python trên Linux là xong; còn MT5 phụ thuộc vào một terminal của MetaTrader. Vì vậy cách kết nối MT5 là quyết định kiến trúc (ADR-03, Phần 12), không chỉ là “thêm một endpoint”.

### Ba hướng kết nối MT5

| Hướng kết nối | Cách hoạt động | Đánh đổi |
|---|---|---|
| MetaTrader5 (Python, official) | Kết nối tới MT5 terminal đang mở & đã đăng nhập trên cùng máy; thiên về polling tick/nến. | Chỉ chạy chính thức trên Windows; hợp prototype hoặc 1 tài khoản; nhiều tài khoản cần nhiều terminal/máy Windows. |
| MetaApi (cloud) | Dịch vụ bên thứ ba bắc cầu tới tài khoản MT5/MT4, cung cấp REST + streaming; họ chạy terminal hộ. | Hợp kiến trúc event-driven, chạy được từ Linux/K8s; đổi lại có phí theo tài khoản, phụ thuộc bên thứ ba, thêm độ trễ, credential nằm ở bên thứ ba (R-08). |
| Cầu nối EA (MQL5) tự viết | Expert Advisor chạy trong terminal, nói chuyện với backend qua socket/WebRequest/file. | Toàn quyền kiểm soát, không phí SaaS; nhưng tự xây & bảo trì, vẫn cần terminal chạy. |

### Thông tin đăng nhập: crypto vs MT5

| Yếu tố | Sàn crypto | MT5 |
|---|---|---|
| Định danh | API key + secret (đôi khi passphrase) | Số tài khoản (login) + mật khẩu + tên server broker |
| Phân quyền | Bật/tắt riêng quyền trade, withdraw, đọc | Master password (giao dịch) vs investor password (chỉ đọc) |
| Rút tiền | API key CÓ THỂ bị bật nhầm quyền rút — bắt buộc tắt | Tài khoản giao dịch thường không tự rút được; rút qua cổng riêng của broker |
| Lưu trữ | Vault/KMS, che (masked) sau khi nhập | Cũng Vault/KMS; nếu dùng MetaApi thì credential nằm ở bên thứ ba — cân nhắc rủi ro (R-08) |

### P&L đa tiền tệ

Ledger lưu lãi/lỗ theo tiền gốc của từng instrument (USDT cho crypto, tiền tài khoản cho MT5, USD cho chứng khoán) VÀ một giá trị đã quy đổi sang đồng tiền báo cáo hợp nhất (mặc định USD, có thể đổi sang VND cho báo cáo nội bộ). Nguồn tỷ giá và thời điểm quy đổi (tại thời điểm khớp lệnh, không phải tại thời điểm lập báo cáo) phải được ghi rõ và nhất quán trong toàn hệ thống.

### Corporate actions cho adapter chứng khoán

Chia tách cổ phiếu (stock split) và cổ tức phải được áp dụng vào dữ liệu OHLCV lịch sử dùng cho backtest, và đối soát số lượng vị thế qua thời điểm chia tách — dữ liệu chưa điều chỉnh sẽ làm sai lệch âm thầm cả số liệu backtest (Sharpe/Drawdown) lẫn số liệu đối soát vị thế live.

### Lưu ý triển khai

- Hạ tầng: package MT5 official phá vỡ giả định Linux/K8s (cần host Windows); MetaApi giữ được kiến trúc gọn nhưng thêm chi phí & phụ thuộc — chốt theo ADR-03 ở Giai đoạn 0.
- Chuẩn hoá symbol: EURUSD / XAUUSD (forex, kim loại) vs BTC/USDT (crypto) vs AAPL (cổ phiếu) cần một bảng ánh xạ trong mỗi adapter.
- Giờ giao dịch: forex có phiên và nghỉ cuối tuần, một số CFD có khung giờ riêng, crypto chạy 24/7 — Risk Management và cửa sổ phát hiện drift cần biết lịch thị trường; thời điểm phát candle.closed cũng khác nhau.
- Định cỡ vị thế & phí: mô hình slippage và cách tính khối lượng (lot của forex vs số coin/contract) khác nhau giữa các nền tảng — tách trong từng adapter, không hard-code ở Strategy Engine.

## 11. Vận hành & SRE Runbook
*Cho SRE thứ để vận hành theo lúc 3 giờ sáng*

### SLO / SLI theo service

| Service | Chỉ số | Mục tiêu | Ghi chú |
|---|---|---|---|
| OMS (đặt lệnh) | Thời gian submit → ack | p99 < 500ms | Đo tại Adapter Layer, tách riêng theo từng sàn/broker |
| Market Data | Độ tươi dữ liệu (staleness) | Cảnh báo nếu không có candle.closed cho 1 symbol quá 2× chu kỳ kỳ vọng | Ngưỡng khác nhau giữa forex (có phiên nghỉ) và crypto (24/7) |
| API Gateway | Uptime | ≥ 99.9% trong giờ thị trường mở | Đo theo từng thị trường (forex/crypto/chứng khoán có giờ mở khác nhau) |
| AI Inference | Độ trễ suy luận | p99 < 50% chu kỳ nến của khung thời gian đang dùng | NFR-04 |
| Risk Management | Thời gian phản hồi risk-check | p99 < 200ms (nằm trong ngân sách 500ms của OMS) | Đường găng đồng bộ — Phần 02 |
| Reconciliation | Chu kỳ đối soát | 1–5 phút cho account đang có vị thế mở | Tự động kích L2 nếu phát hiện break (Phần 03c) |

### FMEA — Bảng phân tích kiểu lỗi

| Lỗi | Cách phát hiện | Phản ứng tự động | Thời gian mục tiêu | Leo thang |
|---|---|---|---|---|
| Feed dữ liệu chết | Không có candle.closed quá ngưỡng staleness | L1 cục bộ trên symbol bị ảnh hưởng, chuyển sang nguồn dự phòng nếu có | < 2× chu kỳ nến | SEV2, leo SEV1 nếu >15 phút |
| Broker trả lỗi 5xx / rate-limit | Adapter phát hiện lỗi liên tục từ 1 endpoint | Backoff + retry có giới hạn; nếu vượt ngưỡng → L2 cho account/adapter đó | < 5 phút | SEV2 |
| Event Bus down/phân mảnh | Consumer lag hoặc mất kết nối broker Kafka | Đường găng đồng bộ không bị ảnh hưởng trực tiếp; dừng nhận tín hiệu mới cho tới khi phục hồi | < 5 phút phát hiện | SEV1 |
| DB (Postgres/Timescale) failover | Health check lỗi trên primary | Chuyển sang replica theo cấu hình HA đã thiết lập | RTO < 5 phút, RPO < 1 phút | SEV1 |
| Vault không truy cập được | Health check Vault lỗi | Fail-closed cho đặt lệnh mới (Phần 03d); stop native trên sàn không bị ảnh hưởng | Ngay lập tức | SEV1 |
| Model Registry/Inference không phản hồi | Health check lỗi hoặc timeout suy luận | Không có tín hiệu mới = không có lệnh mới (fail-closed) | < 1 phút phát hiện | SEV2, leo SEV1 nếu >30 phút |
| MT5 terminal ngắt kết nối | Health check terminal (official) hoặc mất stream (MetaApi) | L1 cho các symbol qua adapter MT5; thử kết nối lại theo lịch backoff | < 3 phút | SEV2 |

### Taxonomy cảnh báo

| Mức | Ví dụ sự kiện | Kênh | Phản hồi yêu cầu |
|---|---|---|---|
| SEV1 | Kill-switch tự động kích hoạt, lệch đối soát, mất kết nối sàn khi đang có vị thế | Kênh page có escalation nếu không xác nhận trong 5–10 phút → liên hệ dự phòng | Phải có người xác nhận đã tiếp nhận trong SLA |
| SEV2 | Feed một symbol bị stale, broker trả lỗi liên tục nhưng đã có fallback | Thông báo chat ngay (Telegram/Slack), không page | Xem trong ca làm việc hiện tại, không cần đánh thức |
| SEV3 | Model được promote thành công, báo cáo hiệu suất định kỳ | Chỉ tổng hợp trong digest | Xem khi thuận tiện |

### Runbook rút gọn

- Runbook đối soát: phát hiện break → tự động L2 trên account/symbol liên quan → SEV1 → người trực xác nhận trong 5-10 phút → điều tra theo quy tắc sàn-là-sự-thật → RESOLVED, ghi log không xoá lịch sử.
- Runbook kill-switch: xác định mức cần thiết (L1-L4) → thực hiện qua control FE hoặc tự động → với L3/L4 bắt buộc thông báo SEV1 ngay → chỉ resume sau khi xác nhận nguyên nhân đã xử lý (L3+ theo quy trình 2 người với L4).
- Runbook bảo trì sàn/broker: khi có thông báo bảo trì trước (MT5/broker), tự động L1 cho các symbol/account liên quan trước thời điểm bảo trì, resume sau khi xác nhận kết nối ổn định trở lại.

## 12. Nhật ký quyết định kiến trúc
*ADR Log — để 6 tháng sau không ai phải đoán lại lý do*

### ADR-01 — Event Bus: Kafka vs Redis Streams

**Bối cảnh:** Hệ thống cần vừa truyền tín hiệu nội bộ tốc độ cao, vừa cần khả năng replay đầy đủ để phục vụ audit và điều tra sự cố (NFR-02).

**Lựa chọn đã xét:** Kafka (durable log, replay, consumer group, retention cấu hình được) so với Redis Streams (nhẹ, vận hành đơn giản hơn nhưng retention/durability yếu hơn).

**Quyết định:** Kafka (hoặc dịch vụ managed tương đương) cho event bus lõi giao dịch (candle.closed, signal.generated, order.*, risk.*, reconciliation.*). Redis Streams/pub-sub chỉ dùng cho tín hiệu nội bộ phi audit (vd cache invalidation).

**Hệ quả đánh đổi:** Thêm chi phí vận hành Kafka so với Redis; đổi lại đạt được khả năng truy vết bắt buộc theo NFR-02.

### ADR-02 — Mức phân rã: modular-monolith vs microservice đầy đủ ở Phase 1

**Bối cảnh:** 15 module được liệt kê ở Phần 03 là ranh giới trách nhiệm hợp lý, nhưng một đội tiền-code triển khai cả 15 microservice độc lập ngay từ đầu sẽ tốn chi phí hạ tầng vượt xa giá trị thu được ở giai đoạn MVP.

**Lựa chọn đã xét:** Giữ nguyên 15 module như 15 service độc lập ngay từ Phase 1, so với gộp thành ít container hơn (Core Trading Service, Data Service, AI Service, Gateway, Backtesting) với ranh giới module nội bộ rõ ràng.

**Quyết định:** Modular-monolith theo nhóm container ở Phase 1 (xem cột "Phân kỳ triển khai" ở từng module, Phần 03); tách service thật là quyết định của Phase 3-4 dựa trên tải thực tế, không phải giả định ban đầu.

**Hệ quả đánh đổi:** Giảm chi phí CI/CD và vận hành ở Phase 1; đánh đổi là cần kỷ luật giữ ranh giới module rõ trong code để tách sau này không phải viết lại.

### ADR-03 — Kết nối MT5: official Python package vs MetaApi vs EA bridge tự viết

**Bối cảnh:** MT5 không có "API đám mây" như sàn crypto; cách kết nối là quyết định hạ tầng (Windows host bắt buộc với package official), không chỉ là thêm một endpoint.

**Lựa chọn đã xét:** 3 hướng — xem bảng so sánh chi tiết trong nội dung Phần 10 (official/Windows-only, MetaApi/cloud có phí và rủi ro bên thứ ba, EA bridge tự viết cần tự bảo trì).

**Quyết định:** Mặc định đề xuất MetaApi cho giai đoạn đầu để giữ kiến trúc Linux/K8s thống nhất, chấp nhận đánh đổi chi phí & rủi ro bên thứ ba (R-08); chuyển sang EA bridge tự viết nếu chi phí MetaApi vượt ngưỡng ở quy mô lớn hơn.

**Hệ quả đánh đổi:** Phụ thuộc uptime & bảo mật của MetaApi; cần phương án dự phòng đã thiết kế sẵn (không phải ứng biến khi sự cố xảy ra).

### ADR-04 — Luồng Strategy → Risk → OMS: đồng bộ vs bất đồng bộ

**Bối cảnh:** Risk Management được gọi là "tuyến phòng thủ cuối cùng"; nếu bước này bất đồng bộ qua Event Bus, một giới hạn rủi ro mới cập nhật có thể không kịp áp dụng cho lệnh đã đang bay.

**Lựa chọn đã xét:** Bất đồng bộ qua Event Bus (nhất quán với phần còn lại của kiến trúc) so với đồng bộ (RPC/HTTP nội bộ với timeout).

**Quyết định:** Đồng bộ, có timeout tường minh và mặc định fail-closed khi timeout (Phần 02, Phần 03d) — là ngoại lệ tường minh so với pattern pub/sub dùng ở phần còn lại của hệ thống.

**Hệ quả đánh đổi:** Thêm độ trễ nhỏ so với bất đồng bộ hoàn toàn; đổi lại đảm bảo giới hạn rủi ro luôn được áp dụng trước khi lệnh rời khỏi hệ thống.

## A. Phụ lục — Sơ đồ C4 & Sequence
*Trình bày dạng bảng để tránh phụ thuộc công cụ vẽ ngoài Word*

### C4 — Context (hệ thống & tác nhân ngoài)

| Actor / Hệ thống ngoài | Tương tác với hệ thống |
|---|---|
| Trader / Operator | Cấu hình chiến lược, giám sát, dùng kill-switch qua Frontend. |
| Sàn / Broker (crypto, MT5, chứng khoán) | Cung cấp dữ liệu thị trường, nhận lệnh, trả kết quả khớp lệnh — qua Adapter Layer. |
| MetaApi (nếu chọn theo ADR-03) | Bên thứ ba bắc cầu tới tài khoản MT5, nắm giữ credential — xem R-08. |
| Claude API (tuỳ chọn) | Cung cấp phân tích sentiment tin tức làm feature phụ trợ cho Feature Engineering. |
| Risk Officer / ML Lead / SRE | Phê duyệt promote model, xác nhận kill-switch L3/L4, xử lý sự cố SEV1. |

### C4 — Container

| Container (Phase 1) | Gồm module | Công nghệ chính |
|---|---|---|
| Core Trading Service | Adapter Layer, Strategy Engine, Risk Management, OMS, Portfolio & Ledger, Notification | Python/FastAPI, PostgreSQL |
| Data Service | Market Data Service, Feature Engineering | Python, TimescaleDB/InfluxDB, Kafka |
| AI Service | AI Training Pipeline, AI Inference Service, Model Registry | Python, XGBoost/PyTorch, MLflow |
| Backtesting Engine | Backtesting Engine (độc lập, tải theo đợt) | Python |
| API Gateway | API Gateway & Auth | FastAPI, JWT, Vault |
| Frontend | 8 màn hình + control kill-switch | React/Next.js, WebSocket |

### Sequence — Đặt lệnh (order placement)

```
1. AI Inference sinh signal.generated (xác suất hiệu chỉnh + feature_snapshot_id)
2. Strategy Engine nhận signal, định cỡ vị thế (Kelly giới hạn 25%)
3. Strategy Engine gọi ĐỒNG BỘ Risk Management (RPC + timeout)
4a. Risk Management TỪ CHỐI → dừng, ghi log risk-check, không tạo Order
4b. Risk Management CHẤP THUẬN → Strategy Engine tạo Order (state: CREATED → RISK_APPROVED)
5. OMS gửi lệnh qua Adapter Layer tới sàn/broker (state: SUBMITTED)
6. Sàn trả ack → state: ACKNOWLEDGED; mất ack do timeout → state: UNKNOWN → OMS bắt buộc truy vấn trạng thái trước khi làm gì tiếp
7. Khớp lệnh → state: FILLED/PARTIALLY_FILLED → Portfolio & Ledger cập nhật, phát order.filled
```

### Sequence — Promote model (champion → challenger → production)

```
1. Trigger (lịch hoặc drift) → AI Training Pipeline train challenger, tôn trọng label_available_at
2. Backtest challenger: purge + embargo + walk-forward → tính PSR/DSR + edge kinh tế
3. Không đạt ngưỡng (DSR>0 @95%, edge ≥2× chi phí) → dừng, ghi log, không đi tiếp
4. Đạt ngưỡng → Shadow trading N ngày song song với champion (không đặt lệnh thật)
5. Đạt N≥100 lệnh shadow & ổn định → yêu cầu xác nhận thủ công của ML Lead
6. Canary rollout 10% vốn thật → theo dõi sát → tăng dần lên 100%
7. Suy giảm dưới ngưỡng an toàn bất kỳ lúc nào sau promote → tự động rollback <5 phút + SEV1
8. Model Registry ghi lại toàn bộ lịch sử (kể cả bản bị loại) — quay lại Bước 1 của Phần 05
```
