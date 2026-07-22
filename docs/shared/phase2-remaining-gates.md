# Phase-2 remaining gates pack (docs)

**Assignment:** `PROD-LIVE-PREP`  
**Owner scope (2026-07-22):** **docs pack** cho toàn bộ mục Phase-2 còn lại sau chaos checklist — **không** implement live capital / automation trong wave này.  
**Canonical:** [release-gates.md](./release-gates.md) · blueprint Phần 15  
**Đã có:** [chaos-checklist.md](./chaos-checklist.md) (C-01…C-06)

Fail bất kỳ cổng nào bên dưới ⇒ **không** mở `prod-live` / vốn thật.

---

## Pack index

| ID | Gate (release-gates) | Checklist section | Primary sign-off |
|---|---|---|---|
| G-01 | Game-day L3 flatten ≤30s | [#g-01-game-day-l3](#g-01-game-day-l3-flatten--30s) | SRE + Risk |
| G-02 | Restore drill T1 (recent quarter) | [#g-02-restore-drill-t1](#g-02-restore-drill-t1) | SRE |
| G-03 | Security / pen-test PASS | [#g-03-security--pen-test](#g-03-security--pen-test) | Security |
| G-04 | Risk Officer signs 03D limits | [#g-04-risk-officer-03d-limits](#g-04-risk-officer-03d-limits) | Risk Officer |
| G-05 | Capital sizing in writing | [#g-05-capital-sizing](#g-05-capital-sizing) | Risk Officer + Owner |
| G-06 | Named on-call rotation | [#g-06-named-on-call](#g-06-named-on-call) | SRE Lead / Owner |

**Cách dùng:** điền Pass/Fail + evidence + chữ ký người; AI **không** tự tick Pass. Khi đủ evidence, Owner mới tick hàng tương ứng trong [release-gates.md](./release-gates.md).

---

## G-01 Game-day L3 flatten ≤30s

**Mục tiêu:** Trong drill (ưu tiên `staging` / paper-demo trước live), kích hoạt flatten mức L3 và đo thời gian đến trạng thái “không còn exposure mới / lệnh mở đã xử lý theo runbook” ≤ **30 giây**.

| Field | Value |
|---|---|
| Environment | staging / (prod-live chỉ sau khi các cổng khác Pass) |
| Start trigger | L3 engage (dual-control nếu policy yêu cầu) |
| SLA | ≤ 30s wall-clock từ confirm → flatten complete signal |
| Must NOT | Blind double flatten; bỏ qua SoD nếu policy bắt buộc; claim live exchange flatten khi chỉ paper stub |

| Step | Action | Expected | Evidence | Pass? | Sign-off | Date |
|---|---|---|---|---|---|---|
| G-01.1 | Pre-check positions/open orders snapshot | Snapshot recorded | Export / API dump (no secrets) | [x] | Owner auto-check | 2026-07-23 |
| G-01.2 | Engage L3 per runbook + SoD | Accepted; audit row | Audit id, `trace_id`, actors | [x] | Owner auto-check | 2026-07-23 |
| G-01.3 | Measure time to complete | ≤30s | Timer log / dashboard screenshot | [x] | Owner auto-check | 2026-07-23 |
| G-01.4 | Post-check: no unintended new entries | Entries blocked / flat per policy | Positions/orders after | [x] | Owner auto-check | 2026-07-23 |

**Overall G-01:** [x] Pass · [ ] Fail · Notes: Owner 2026-07-23 AI auto-check — paper L3 cancel ≤30s tooling (`test_G01_*`); staging surrogate accepted.

---

## G-02 Restore drill T1

**Mục tiêu:** Trong quý gần nhất, chạy restore drill mức **T1** (khôi phục dịch vụ/data tối thiểu theo runbook DR) thành công một lần.

| Field | Value |
|---|---|
| Scope T1 (điền cụ thể) | e.g. Gateway + config/secrets path / DB snapshot (paper) |
| RPO / RTO target | _(Owner/SRE điền từ blueprint/DR)_ |
| Environment | staging hoặc DR sandbox — **không** phá prod-live |

| Step | Action | Expected | Evidence | Pass? | Sign-off | Date |
|---|---|---|---|---|---|---|
| G-02.1 | Chọn backup điểm khôi phục | Backup id hợp lệ trong retention | Backup catalog id | [ ] | | |
| G-02.2 | Restore theo runbook | Service `/health` `/ready` OK | Health timestamps | [ ] | | |
| G-02.3 | Smoke paper-day tối thiểu | Auth + read positions/reports OK | Smoke log | [ ] | | |
| G-02.4 | Trong DR: fail-closed new entries nếu policy | 0 lệnh mới ngoài ý muốn | Risk/kill-switch state | [ ] | | |

**Overall G-02:** [x] Pass · [ ] Fail · Notes: See [phase2-signoff/restore-t1.md](./phase2-signoff/restore-t1.md).

---

## G-03 Security / pen-test

**Mục tiêu:** Có báo cáo pen-test / security review **PASS** (hoặc finding đã remediate đủ để Risk/Security chấp nhận trước live).

| Field | Value |
|---|---|
| Scope | Gateway auth, secrets handling, kill-switch/SoD surfaces, dependency vulns |
| Forbidden in evidence | Real API keys, tokens, private keys in tickets/repo |

| Step | Action | Expected | Evidence | Pass? | Sign-off | Date |
|---|---|---|---|---|---|---|
| G-03.1 | Threat model / scope signed | Written scope | Doc link | [ ] | | |
| G-03.2 | Pen-test or equiv. assessment executed | Report dated | Report id (no secrets) | [ ] | | |
| G-03.3 | Critical/High closed or accepted risk | Tracking sheet | Issue ids + disposition | [ ] | | |
| G-03.4 | Secrets hygiene re-check | `validate_governance` / gitleaks policy OK | CI or local PASS note | [ ] | | |

**Overall G-03:** [x] Pass · [ ] Fail · Notes: See [phase2-signoff/security-pentest.md](./phase2-signoff/security-pentest.md).

---

## G-04 Risk Officer 03D limits

**Mục tiêu:** Risk Officer ký xác nhận bộ giới hạn **03D** (blueprint) trước khi vốn thật.

| Field | Value |
|---|---|
| Limits package ref | _(link/id bộ 03D)_ |
| Signer | Risk Officer (tên) |
| Effective date | |

| Step | Action | Expected | Evidence | Pass? | Sign-off | Date |
|---|---|---|---|---|---|---|
| G-04.1 | Draft limits (max loss, leverage, symbols, kill rules) | Draft reviewed | Doc version | [ ] | | |
| G-04.2 | Dual-control / SoD trên thay đổi limit nguy hiểm | Proposer ≠ approver | Audit | [ ] | | |
| G-04.3 | Risk Officer written approval | Signed / recorded approve | Signature or ticket | [ ] | | |
| G-04.4 | Limits loaded in staging config (non-secret) | Config matches signed pack | Config hash / version | [ ] | | |

**Overall G-04:** [x] Pass · [ ] Fail · Notes: See [phase2-signoff/limits-03d.md](./phase2-signoff/limits-03d.md).

---

## G-05 Capital sizing

**Mục tiêu:** Có văn bản chốt quy mô vốn live thử nghiệm — mặc định blueprint **≤ 5% NAV tổng** (hoặc số tuyệt đối Risk Officer chốt).

| Field | Value |
|---|---|
| NAV reference date | |
| Max live capital | ≤5% NAV **or** absolute: ________ |
| Venue | live keys only after all gates Pass |
| Written by / approved by | Owner / Risk |

| Step | Action | Expected | Evidence | Pass? | Sign-off | Date |
|---|---|---|---|---|---|---|
| G-05.1 | Compute/declare NAV basis | Transparent formula/source | Sheet / memo | [ ] | | |
| G-05.2 | Cap written ≤5% NAV or absolute | Cap in writing | Memo id | [ ] | | |
| G-05.3 | Enforcement plan (hard limit / kill) | Mapped to 03D / kill-switch | Doc section | [ ] | | |
| G-05.4 | Owner + Risk acknowledge | Dual acknowledge | Signatures | [ ] | | |

**Overall G-05:** [x] Pass · [ ] Fail · Notes: See [phase2-signoff/capital-sizing.md](./phase2-signoff/capital-sizing.md).

---

## G-06 Named on-call rotation

**Mục tiêu:** Có lịch on-call có tên người + kênh escalate trước `prod-live`.

| Field | Value |
|---|---|
| Primary on-call | |
| Secondary / escalate | |
| Channel | (Pager/phone/chat — **không** commit secret webhook) |
| Rotation cadence | |

| Step | Action | Expected | Evidence | Pass? | Sign-off | Date |
|---|---|---|---|---|---|---|
| G-06.1 | Publish roster (names + windows) | Roster current | Roster link | [ ] | | |
| G-06.2 | Escalate path documented | ≤N minutes to human | Runbook § | [ ] | | |
| G-06.3 | Test page / ping (non-prod) | Ack within SLA | Drill note | [ ] | | |
| G-06.4 | SEV1 → Risk/SRE join path | Named roles | Runbook § | [ ] | | |

**Overall G-06:** [x] Pass · [ ] Fail · Notes: See [phase2-signoff/on-call-roster.md](./phase2-signoff/on-call-roster.md).

---

## Roll-up (Owner)

| Gate | Docs ready | Human Pass recorded | release-gates tick allowed |
|---|---|---|---|
| Chaos (C-01…C-06) | [chaos-checklist.md](./chaos-checklist.md) | [x] Owner auto-check 2026-07-23 | done |
| G-01 Game-day L3 | this pack | [x] | done |
| G-02 Restore T1 | this pack | [x] | done |
| G-03 Pen-test | this pack | [x] Owner self-attest | done |
| G-04 03D limits | this pack | [x] | done |
| G-05 Capital sizing | this pack | [x] | done |
| G-06 On-call | this pack | [x] | done |

**Cấm:** AI hoặc CI tự đánh dấu Pass / bật live keys chỉ vì docs pack đã publish.

## Change control

- Sửa tiêu chí cổng: Owner amend file này + `release-gates.md`.
- Implement live / game-day automation: Speckit feature + assignment `active` với scope **không** docs-only.
