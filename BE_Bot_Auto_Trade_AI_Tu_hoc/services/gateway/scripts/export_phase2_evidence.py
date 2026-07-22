"""Export paper/staging tooling evidence for C-01..C-06 and G-01.

Runs the Phase-2 drill pytest suite, writes JSON + Markdown under
artifacts/phase2-evidence/. Results are tooling-only — NEVER gate Pass.

Usage (from gateway service root):
  python scripts/export_phase2_evidence.py
"""

from __future__ import annotations

import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

GATEWAY_ROOT = Path(__file__).resolve().parents[1]
SUITE = "tests/test_phase2_staging_drills.py"
OUT_DIR = GATEWAY_ROOT / "artifacts" / "phase2-evidence"

# Map pytest test function → chaos / game-day ID
DRILL_MAP: dict[str, dict[str, str]] = {
    "test_C01_policy_unknown_no_blind_double_submit_documented": {
        "id": "C-01",
        "title": "No blind double submit (paper analogue of timeout/UNKNOWN)",
        "human_followup": "Re-run UNKNOWN FSM against staging venue ack drop",
    },
    "test_C02_risk_down_zero_new_entries": {
        "id": "C-02",
        "title": "Risk down → 0 new entries",
        "human_followup": "Inject real Risk dependency failure on staging host",
    },
    "test_C03_credentials_required_fail_closed": {
        "id": "C-03",
        "title": "No credentials → fail-closed (Vault-down analogue)",
        "human_followup": "Vault-down drill on staging secrets path",
    },
    "test_C04_sync_path_still_risk_checks_when_active": {
        "id": "C-04",
        "title": "Sync risk-check before fill (Kafka N/A monolith)",
        "human_followup": "If bus added later: prove risk still sync under bus-down",
    },
    "test_C05_stale_fixture_and_l1_blocks_entries": {
        "id": "C-05",
        "title": "Stale market fixture + L1 blocks entries",
        "human_followup": "Staging feed silence SLA + FE stale UX check",
    },
    "test_C06_l2_without_confirm_rejected": {
        "id": "C-06",
        "title": "L2 without confirm rejected (SoD-style)",
        "human_followup": "Dual-control actors on staging SoD path",
    },
    "test_G01_l3_cancels_open_orders_under_30s": {
        "id": "G-01",
        "title": "L3 cancel open orders ≤30s (paper)",
        "human_followup": "Game-day flatten on staging host with timer evidence",
    },
}


def _run_pytest(junit_path: Path) -> int:
    junit_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        SUITE,
        "-q",
        f"--junitxml={junit_path}",
    ]
    print("Running:", " ".join(cmd))
    return subprocess.call(cmd, cwd=GATEWAY_ROOT)


def _parse_junit(junit_path: Path) -> list[dict]:
    tree = ET.parse(junit_path)
    root = tree.getroot()
    # pytest may wrap as testsuites/testsuite or single testsuite
    cases = root.findall(".//testcase")
    rows: list[dict] = []
    for case in cases:
        name = case.get("name") or ""
        meta = DRILL_MAP.get(name)
        if meta is None:
            continue
        failed = case.find("failure") is not None or case.find("error") is not None
        skipped = case.find("skipped") is not None
        if skipped:
            status = "skipped"
        elif failed:
            status = "tooling_FAIL"
        else:
            status = "tooling_PASS"
        rows.append(
            {
                "id": meta["id"],
                "title": meta["title"],
                "test": name,
                "status": status,
                "gate_pass": False,
                "human_followup": meta["human_followup"],
                "time_s": case.get("time"),
            }
        )
    # Stable order C-01.. then G-01
    order = {f"C-0{i}": i for i in range(1, 7)}
    order["G-01"] = 7
    rows.sort(key=lambda r: order.get(r["id"], 99))
    return rows


def _write_pack(rows: list[dict], junit_path: Path) -> tuple[Path, Path]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    pack = {
        "schema": "phase2-tooling-evidence/v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "environment": "paper-gateway-testclient",
        "suite": SUITE,
        "disclaimer": (
            "tooling_PASS is NOT release-gates Pass. "
            "Owner/SRE/Risk must sign chaos-checklist and phase2-signoff."
        ),
        "release_gates_auto_tick": False,
        "drills": rows,
        "junitxml": str(junit_path.relative_to(GATEWAY_ROOT)).replace("\\", "/"),
        "summary": {
            "expected": len(DRILL_MAP),
            "reported": len(rows),
            "tooling_pass": sum(1 for r in rows if r["status"] == "tooling_PASS"),
            "tooling_fail": sum(1 for r in rows if r["status"] == "tooling_FAIL"),
            "gate_pass_count": 0,
        },
    }
    json_path = OUT_DIR / f"evidence-{ts}.json"
    latest_json = OUT_DIR / "evidence-latest.json"
    md_path = OUT_DIR / f"evidence-{ts}.md"
    latest_md = OUT_DIR / "evidence-latest.md"

    text = json.dumps(pack, indent=2, ensure_ascii=False) + "\n"
    json_path.write_text(text, encoding="utf-8")
    latest_json.write_text(text, encoding="utf-8")

    lines = [
        "# Phase-2 tooling evidence pack",
        "",
        f"- Generated (UTC): `{pack['generated_at_utc']}`",
        f"- Environment: `{pack['environment']}`",
        f"- Suite: `{SUITE}`",
        "",
        f"**{pack['disclaimer']}**",
        "",
        "| ID | Status | gate_pass | Test | Human follow-up |",
        "|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['id']} | {r['status']} | `{r['gate_pass']}` | "
            f"`{r['test']}` | {r['human_followup']} |"
        )
    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- tooling_PASS: **{pack['summary']['tooling_pass']}** / {pack['summary']['expected']}",
            f"- tooling_FAIL: **{pack['summary']['tooling_fail']}**",
            f"- gate_pass (auto): **0** (forbidden)",
            "",
            "Next: follow docs/shared/phase2-staging-runbook.md (repo root).",
            "",
        ]
    )
    md = "\n".join(lines)
    md_path.write_text(md, encoding="utf-8")
    latest_md.write_text(md, encoding="utf-8")
    return latest_json, latest_md


def main() -> int:
    junit_path = OUT_DIR / "junit-drills.xml"
    rc = _run_pytest(junit_path)
    if not junit_path.exists():
        print("ERROR: junitxml not produced", file=sys.stderr)
        return 2
    rows = _parse_junit(junit_path)
    missing = set(DRILL_MAP) - {r["test"] for r in rows}
    if missing:
        print("WARN: missing mapped tests in junit:", sorted(missing))
    latest_json, latest_md = _write_pack(rows, junit_path)
    print(f"Wrote {latest_json}")
    print(f"Wrote {latest_md}")
    summary_fail = sum(1 for r in rows if r["status"] == "tooling_FAIL")
    if rc != 0 or summary_fail:
        print("RESULT: tooling evidence incomplete (pytest or drill FAIL)")
        return rc or 1
    print("RESULT: tooling evidence export OK (not gate Pass)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
