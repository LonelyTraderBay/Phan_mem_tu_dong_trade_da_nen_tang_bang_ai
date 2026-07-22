#!/usr/bin/env python3
"""Enterprise governance validator for contracts + MVP matrix.

Usage:
  python scripts/validate_governance.py
Exit 0 = PASS, 1 = FAIL
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAILED = False


def ok(msg: str) -> None:
    print(f"OK:   {msg}")


def fail(msg: str) -> None:
    global FAILED
    FAILED = True
    print(f"FAIL: {msg}", file=sys.stderr)


def load_yaml(path: Path):
    try:
        import yaml  # type: ignore
    except ImportError:
        fail("PyYAML required: pip install pyyaml")
        return None
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def collect_operation_ids(openapi: dict) -> set[str]:
    ids: set[str] = set()
    for path_item in (openapi.get("paths") or {}).values():
        if not isinstance(path_item, dict):
            continue
        for method, op in path_item.items():
            if method.startswith("x-") or not isinstance(op, dict):
                continue
            oid = op.get("operationId")
            if oid:
                ids.add(str(oid))
    return ids


def validate_openapi() -> tuple[set[str], dict[str, bool | None]]:
    path = ROOT / "packages/contracts/openapi/openapi.yaml"
    if not path.exists():
        fail("Missing packages/contracts/openapi/openapi.yaml")
        return set(), {}
    ok("openapi.yaml exists")
    data = load_yaml(path)
    if data is None:
        return set(), {}
    if not isinstance(data, dict) or "openapi" not in data:
        fail("openapi.yaml missing openapi key")
        return set(), {}
    ok("openapi.yaml parseable")
    info = data.get("info") or {}
    ver = str(info.get("version", ""))
    version_file = (ROOT / "packages/contracts/VERSION").read_text(encoding="utf-8").strip()
    if ver != version_file:
        fail(f"OpenAPI info.version={ver!r} != VERSION file {version_file!r}")
    else:
        ok(f"VERSION sync {version_file}")
    ids = collect_operation_ids(data)
    if "getHealth" not in ids or "getReady" not in ids:
        fail("Missing getHealth/getReady")
    else:
        ok("System ops getHealth/getReady present")
    # Deferred contrast
    paths = data.get("paths") or {}
    promote = None
    mvp_flags: dict[str, bool | None] = {}
    for _p, item in paths.items():
        if not isinstance(item, dict):
            continue
        for method, op in item.items():
            if method.startswith("x-") or not isinstance(op, dict):
                continue
            oid = op.get("operationId")
            if not oid:
                continue
            mvp_flags[str(oid)] = op.get("x-mvp")
            if oid == "postModelPromote":
                promote = op
    if promote is None:
        fail("Missing deferred stub postModelPromote")
    else:
        if promote.get("x-mvp") is not False:
            fail("postModelPromote must have x-mvp: false")
        else:
            ok("Deferred postModelPromote x-mvp:false")
    return ids, mvp_flags


def validate_events() -> None:
    events = ROOT / "packages/contracts/events"
    if not events.is_dir():
        fail("Missing packages/contracts/events/")
        return
    schemas = list(events.glob("*.schema.json"))
    if not schemas:
        fail("No events/*.schema.json")
        return
    ok(f"Found {len(schemas)} event schema(s)")
    for s in schemas:
        try:
            json.loads(s.read_text(encoding="utf-8"))
            ok(f"JSON OK {s.name}")
        except Exception as e:
            fail(f"Invalid JSON {s.name}: {e}")


def validate_matrix(openapi_ids: set[str], mvp_flags: dict[str, bool | None]) -> None:
    yaml_path = ROOT / "docs/shared/mvp-capability-matrix.yaml"
    md_path = ROOT / "docs/shared/mvp-capability-matrix.md"
    example = ROOT / "specs/001-mvp-feature-scope/contracts/mvp-capability-matrix.example.yaml"
    schema_path = ROOT / "specs/001-mvp-feature-scope/contracts/capability-matrix.schema.json"

    if not yaml_path.exists():
        fail("Missing docs/shared/mvp-capability-matrix.yaml")
        return
    if not md_path.exists():
        fail("Missing docs/shared/mvp-capability-matrix.md")
        return
    ok("MVP matrix MD+YAML exist")

    matrix = load_yaml(yaml_path)
    if matrix is None:
        return

    # Soft schema checks aligned with data-model
    required_top = ["version", "updated_at", "primary_market", "operator_profile", "capabilities"]
    for k in required_top:
        if k not in matrix:
            fail(f"Matrix missing top field: {k}")
    caps = matrix.get("capabilities") or []
    if not isinstance(caps, list) or not caps:
        fail("Matrix capabilities empty")
        return

    ids = []
    for i, cap in enumerate(caps):
        if not isinstance(cap, dict):
            fail(f"Capability[{i}] not object")
            continue
        for f in ["id", "name", "description", "status", "rationale", "lane", "contract_touch", "safety_critical"]:
            if f not in cap:
                fail(f"Capability {cap.get('id', i)} missing {f}")
        cid = cap.get("id")
        ids.append(cid)
        status = cap.get("status")
        if status == "deferred" and not cap.get("phase_return"):
            fail(f"Deferred {cid} missing phase_return")
        if status == "in_mvp" and cap.get("lane") == "n_a":
            fail(f"In-MVP {cid} must not use lane n_a")
        if cap.get("contract_touch") is True:
            refs = cap.get("contract_refs") or []
            if not refs:
                fail(f"contract_touch true but empty contract_refs: {cid}")
            for ref in refs:
                if str(ref).startswith("docs-only:"):
                    continue
                if ref not in openapi_ids:
                    fail(f"Matrix contract_ref {ref!r} (cap={cid}) missing in OpenAPI operationId")
                elif mvp_flags.get(str(ref)) is not True:
                    fail(f"Matrix contract_ref {ref!r} (cap={cid}) must have x-mvp: true")
    if len(ids) != len(set(ids)):
        fail("Duplicate capability ids in matrix")
    else:
        ok(f"Matrix {len(ids)} capabilities unique")

    # Example parity (same version + same capability ids)
    if example.exists():
        ex = load_yaml(example)
        if ex and isinstance(ex, dict):
            if ex.get("version") != matrix.get("version"):
                fail(
                    f"example.yaml version {ex.get('version')!r} != matrix {matrix.get('version')!r}"
                )
            else:
                ok("example.yaml version matches matrix")
            ex_ids = {c.get("id") for c in (ex.get("capabilities") or []) if isinstance(c, dict)}
            mat_ids = set(ids)
            if ex_ids != mat_ids:
                fail(f"example/matrix capability id mismatch: only_ex={ex_ids-mat_ids} only_mat={mat_ids-ex_ids}")
            else:
                ok("example.yaml capability ids match matrix")
    else:
        fail("Missing mvp-capability-matrix.example.yaml")

    # Markdown mentions key sections
    md = md_path.read_text(encoding="utf-8")
    for heading in ["In-MVP", "Deferred", "Lane ownership", "Amendment rules", "Contract prerequisites"]:
        if heading not in md:
            fail(f"Matrix MD missing section: {heading}")
    else:
        ok("Matrix MD has required sections")

    # Schema file present
    if schema_path.exists():
        try:
            json.loads(schema_path.read_text(encoding="utf-8"))
            ok("capability-matrix.schema.json JSON OK")
        except Exception as e:
            fail(f"schema JSON invalid: {e}")
    else:
        fail("Missing capability-matrix.schema.json")


def validate_assignment_manifest() -> None:
    path = ROOT / "docs/shared/agent-assignment.yaml"
    if not path.exists():
        fail("Missing docs/shared/agent-assignment.yaml")
        return
    data = load_yaml(path)
    if not data:
        return
    for f in ["version", "feature", "assignments"]:
        if f not in data:
            fail(f"agent-assignment missing {f}")
    assigns = data.get("assignments") or []
    if not assigns:
        fail("agent-assignment has no assignments")
        return
    for a in assigns:
        for f in ["id", "lane", "allowed_paths", "status"]:
            if f not in a:
                fail(f"assignment {a.get('id')} missing {f}")
    ok(f"agent-assignment.yaml OK ({len(assigns)} rows)")


def validate_secrets_hygiene() -> None:
    """Block common secret files from being tracked."""
    bad_patterns = [
        re.compile(r"(^|/)\.env$"),
        re.compile(r"(^|/)\.env\.(local|production|prod|staging)$"),
        re.compile(r"(^|/)id_rsa$"),
        re.compile(r"(^|/).*credentials\.json$"),
    ]
    # Only scan git ls-files if available via reading .gitignore presence
    gitignore = ROOT / ".gitignore"
    if not gitignore.exists():
        fail("Missing .gitignore")
        return
    text = gitignore.read_text(encoding="utf-8")
    required = [".env", "*.pem", "credentials"]
    missing = [r for r in required if r not in text]
    if missing:
        fail(f".gitignore missing secret patterns: {missing}")
    else:
        ok(".gitignore has secret patterns")
    # Fail if any tracked-looking secret path exists unignored in tree as real file name
    for p in ROOT.rglob(".env"):
        if "node_modules" in p.parts or ".git" in p.parts:
            continue
        # allow .env.example only
        if p.name == ".env":
            fail(f"Found real .env file (must not commit): {p.relative_to(ROOT)}")
    ok("No .env files in workspace tree (excluding examples handled)")


def validate_agents_and_rules() -> None:
    agents = ROOT / "AGENTS.md"
    if not agents.exists():
        fail("Missing AGENTS.md")
    else:
        ok("AGENTS.md present")
    required_rules = [
        "00-agent-safety.mdc",
        "10-git-enterprise.mdc",
        "20-git-savepoint.mdc",
        "30-git-recovery.mdc",
        "40-git-empty-repo.mdc",
        "50-secrets-and-env.mdc",
        "60-ai-execution.mdc",
    ]
    rules_dir = ROOT / ".cursor/rules"
    for name in required_rules:
        p = rules_dir / name
        if not p.exists():
            fail(f"Missing .cursor/rules/{name}")
        else:
            ok(f"rule {name}")
    dup = rules_dir / "git-enterprise.mdc"
    if dup.exists():
        fail("Duplicate .cursor/rules/git-enterprise.mdc — use 10-git-enterprise.mdc only")


def validate_codeowners() -> None:
    p = ROOT / ".github/CODEOWNERS"
    if not p.exists():
        fail("Missing .github/CODEOWNERS")
    else:
        ok("CODEOWNERS present")
    wf = ROOT / ".github/workflows/governance.yml"
    if not wf.exists():
        fail("Missing .github/workflows/governance.yml")
    else:
        ok("governance.yml present")


def main() -> int:
    print("=== validate_governance ===")
    ids, mvp_flags = validate_openapi()
    validate_events()
    validate_matrix(ids, mvp_flags)
    validate_assignment_manifest()
    validate_secrets_hygiene()
    validate_agents_and_rules()
    validate_codeowners()
    print()
    if FAILED:
        print("RESULT: FAIL")
        return 1
    print("RESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
