# Data Model: Prod-Paper Harden

## KillSwitchState

| Field | Type | Notes |
|---|---|---|
| engaged | bool | true when any protective level is active |
| level | enum L1\|L2\|L3\|L4 | highest active level; null/omitted when not engaged |
| reason | string | operator reason |
| updated_at | datetime | |
| updated_by | uuid? | operator id |
| confirmed | bool | request-only for L2+ |
| trace_id | string | audit correlation |

### Level semantics (paper staging)

| Level | Effect (paper) |
|---|---|
| L1 | Block new entries |
| L2 | L1 + block strategy activate / tighten (document in module docs) |
| L3 | L2 + cancel open paper orders (internal) |
| L4 | L3 + flatten paper positions via internal matcher |

## ReconciliationRun

| Field | Type | Notes |
|---|---|---|
| id | uuid | |
| started_at / finished_at | datetime | |
| status | ok \| mismatch \| error | |
| positions_compared | int | |
| diffs_count | int | |
| trace_id | string | |

## ReconciliationDiff

| Field | Type | Notes |
|---|---|---|
| symbol | string | |
| field | string | e.g. quantity, avg_price |
| ledger_value | number/string | |
| adapter_value | number/string | |

## Alert (existing)

Reuse `Alert` schema. New codes (string `code` field — no schema break):

- `RECON_MISMATCH`
- `RECON_ERROR`
- `KILL_SWITCH_L2_PLUS` (optional)

## PaperOpsTracker (docs)

Markdown/YAML checklist: criteria id, target days, recorded_days, last_reviewed, notes. Not a trading entity.
