"""
mediator.py — P17 Mediator: field maturity from consumer digests, and spine-update proposals

Function:
    Implements SPEC.md 1.0.0, the foundation's Master Mediator
    (JamesTheGiblet/the-full-stack master_mediator/) as a primitive
    layer of this stack, with its three fixes from the start: three
    consumers need 30 days for Fact (M1), a proposal's inherits is
    given or read from the foundation, never hardcoded (M2), and loading
    survives a file that changes after discovery (M3). It reads digest
    capsules, classifies each field's maturity, and writes unsigned
    proposals for Fact fields. It never signs, merges or edits a layer:
    the owner decides through HAL and makes any change by hand.

Public API:
    1. find_digest_paths(root, pattern) -> list[str]
    2. load_digests(root, pattern) -> list[dict]
    3. extract_observations(digests, now=None) -> list[FieldObservation]
    4. classify(observations) -> list[MaturityFinding]
    5. current_governance(foundation_root) -> str
    6. build_proposal(finding, inherits, created=None) -> dict
    7. export_proposal(finding, out_dir, inherits) -> str
    8. main(argv=None) -> int
    DIGEST_SPECS, TIER_*, FieldObservation, MaturityFinding

Layer:    P17 — Mediator
Depends:  P16 Time (forge_time)
Spec:     SPEC.md 1.0.0
Version:  1.0.0
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)
"""

import argparse
import json
import os
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Tuple

_HERE = os.path.dirname(os.path.abspath(__file__))
_P16 = os.path.join(os.path.dirname(_HERE), "forge-time")
if _P16 not in sys.path:
    sys.path.insert(0, _P16)

import forge_time  # noqa: E402

DEFAULT_PATTERN = "*/sc/*.sc.json"  # this workspace: each repo a sibling with its own sc/
DIGEST_SPECS = {
    "usage_digest": {"list_key": "fields", "key_fields": ("namespace", "lens"), "count_field": "observation_count"},
    "chronoscribe_digest": {"list_key": "event_types", "key_fields": ("event_type",),
                            "count_field": "observation_count"},
    "leighton_digest": {"list_key": "entities", "key_fields": ("entity_id",), "count_field": "observation_count"},
    "hal_digest": {"list_key": "seals", "key_fields": ("entity_class", "tier"), "count_field": "seal_count"},
    "primitive_digest": {"list_key": "fields", "key_fields": ("field_path",), "count_field": "observation_count"},
}
TIER_HYPOTHESIS, TIER_EXPERIMENTAL, TIER_CANDIDATE = "Hypothesis", "Experimental", "Candidate"
TIER_EMERGENT, TIER_FACT = "Emergent", "Fact"


@dataclass(frozen=True)
class FieldObservation:
    consumer: str
    declaration_type: str
    field_key: Tuple[str, ...]
    observation_count: int
    age_days: float


@dataclass(frozen=True)
class MaturityFinding:
    declaration_type: str
    field_key: Tuple[str, ...]
    tier: str
    consumers: List[str]
    total_observation_count: int
    max_age_days: float


# ---------------------------------------------------------------------------
# 9. _digest_type
#    The declaration type if data is a digest, else None.
# ---------------------------------------------------------------------------
def _digest_type(data):
    decl = data.get("declaration") if isinstance(data, dict) else None
    t = decl.get("type") if isinstance(decl, dict) else None
    return t if isinstance(t, str) and t.endswith("_digest") else None


# ---------------------------------------------------------------------------
# 10. _read_json
#     Parsed JSON, or None for a file that is missing, unreadable or
#     malformed.
# ---------------------------------------------------------------------------
def _read_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError, UnicodeDecodeError):
        return None


# ---------------------------------------------------------------------------
# 1. find_digest_paths
#    SPEC §3. Read-only.
# ---------------------------------------------------------------------------
def find_digest_paths(root, pattern=DEFAULT_PATTERN):
    return sorted(str(p) for p in Path(root).glob(pattern) if _digest_type(_read_json(p)))


# ---------------------------------------------------------------------------
# 2. load_digests
#    SPEC §3: each file read once; one that changed after discovery is
#    skipped (M3).
# ---------------------------------------------------------------------------
def load_digests(root, pattern=DEFAULT_PATTERN):
    digests = []
    for path in find_digest_paths(root, pattern):
        data = _read_json(path)
        if _digest_type(data):
            data["_source_path"] = str(path)
            digests.append(data)
    return digests


# ---------------------------------------------------------------------------
# 11. _age_days
#     Days since first_seen; missing or malformed is 0, so a bad
#     timestamp never raises a tier.
# ---------------------------------------------------------------------------
def _age_days(first_seen, now):
    try:
        then = forge_time.parse_iso_utc(first_seen)
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, (now - then).total_seconds() / 86400.0)


# ---------------------------------------------------------------------------
# 3. extract_observations
#    SPEC §4: known types only; malformed entries skipped.
# ---------------------------------------------------------------------------
def extract_observations(digests, now=None):
    now = now or datetime.now(timezone.utc)
    out = []
    for digest in digests:
        decl = digest.get("declaration") or {}
        spec = DIGEST_SPECS.get(decl.get("type"))
        if spec is None:
            continue
        consumer = decl.get("consumer") or "unknown"
        for entry in decl.get(spec["list_key"]) or []:
            try:
                key = tuple(str(entry[k]) for k in spec["key_fields"])
                count = int(entry.get(spec["count_field"], 0))
            except (KeyError, TypeError, ValueError, AttributeError):
                continue
            out.append(FieldObservation(consumer=str(consumer), declaration_type=decl["type"], field_key=key,
                                        observation_count=count, age_days=_age_days(entry.get("first_seen"), now)))
    return out


# ---------------------------------------------------------------------------
# 12. _tier
#     SPEC §4's table, the first rule that holds (M1: three consumers
#     need 30 days).
# ---------------------------------------------------------------------------
def _tier(n_consumers, total, age):
    if (n_consumers >= 3 and age >= 30) or (n_consumers >= 2 and age >= 90):
        return TIER_FACT
    if n_consumers >= 2 and age >= 30:
        return TIER_EMERGENT
    if total >= 100 and age >= 30:
        return TIER_CANDIDATE
    if total >= 10 and age >= 7:
        return TIER_EXPERIMENTAL
    return TIER_HYPOTHESIS


# ---------------------------------------------------------------------------
# 4. classify
#    Grouped by (declaration_type, field_key), never across types.
# ---------------------------------------------------------------------------
def classify(observations):
    groups = {}
    for o in observations:
        groups.setdefault((o.declaration_type, o.field_key), []).append(o)
    found = []
    for (decl_type, key), group in groups.items():
        consumers = sorted({o.consumer for o in group})
        total = sum(o.observation_count for o in group)
        age = max(o.age_days for o in group)
        found.append(MaturityFinding(declaration_type=decl_type, field_key=key, tier=_tier(len(consumers), total, age),
                                     consumers=consumers, total_observation_count=total,
                                     max_age_days=round(age, 2)))
    return found


# ---------------------------------------------------------------------------
# 5. current_governance
#    SPEC §5: the foundation's governance capsule nothing supersedes.
# ---------------------------------------------------------------------------
def current_governance(foundation_root):
    ids, superseded = {}, set()
    for p in Path(foundation_root).glob("sc/forge-stack-governance-v*.sc.json"):
        data = _read_json(p)
        scp_id = data.get("scp_id") if isinstance(data, dict) else None
        if not forge_time.is_ratified_scp_id(scp_id):
            continue
        ids[scp_id] = int(scp_id.rsplit("-v", 1)[1])
        sup = (data.get("declaration") or {}).get("supersedes")
        if isinstance(sup, str):
            superseded.add(sup)
    live = [i for i in ids if i not in superseded] or list(ids)
    if not live:
        raise FileNotFoundError(f"no governance capsule under {Path(foundation_root) / 'sc'}")
    return max(live, key=ids.get)


# ---------------------------------------------------------------------------
# 13. _slug
# ---------------------------------------------------------------------------
def _slug(part):
    return "".join(c if c.isalnum() and c.isascii() else "-" for c in str(part).lower()).strip("-") or "field"


# ---------------------------------------------------------------------------
# 6. build_proposal
#    SPEC §5: Fact only; inherits required and ratified (M2); unsigned.
# ---------------------------------------------------------------------------
def build_proposal(finding, inherits, created=None):
    if finding.tier != TIER_FACT:
        raise ValueError(f"only a Fact finding warrants a spine-update proposal, got {finding.tier!r}")
    if not forge_time.is_ratified_scp_id(inherits):
        raise ValueError(f"inherits must be a ratified scp_id (the governance in force): {inherits!r}")
    key_slug = "-".join(_slug(p) for p in finding.field_key)
    scp_id = f"forge-stack/mediator/spine-update-{_slug(finding.declaration_type)}-{key_slug}-v1"
    if not forge_time.is_ratified_scp_id(scp_id):
        raise ValueError(f"generated scp_id is not ratified: {scp_id!r}")
    return {
        "scp_id": scp_id,
        "scp_version": "1.2.0",
        "created": created or forge_time.utc_now(),
        "inherits": inherits,
        "declaration": {
            "type": "spine_update_proposal",
            "intent": (f"Promote {finding.declaration_type}'s field {list(finding.field_key)!r} to the spine: "
                       f"seen by {len(finding.consumers)} consumers ({', '.join(finding.consumers)}) for "
                       f"{finding.max_age_days:.0f} days, {finding.total_observation_count} observations."),
            "evidence": {
                "declaration_type": finding.declaration_type,
                "field_key": list(finding.field_key),
                "consumers": list(finding.consumers),
                "total_observation_count": finding.total_observation_count,
                "max_age_days": finding.max_age_days,
                "tier": finding.tier,
            },
            "affected_spine_files": [
                "P13 DataCube faces, if this field is a new namespace or face",
                "the SCP spec, if this changes the ratified capsule schema",
            ],
        },
        "licence": "MSL-1.0",
        "signature": None,
    }


# ---------------------------------------------------------------------------
# 7. export_proposal
#    Atomic, LF; returns the path.
# ---------------------------------------------------------------------------
def export_proposal(finding, out_dir, inherits):
    capsule = build_proposal(finding, inherits)
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, capsule["scp_id"].rsplit("/", 1)[-1] + ".sc.json")
    fd, tmp = tempfile.mkstemp(prefix=".proposal.", suffix=".tmp", dir=out_dir)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as f:
            f.write(json.dumps(capsule, indent=2, ensure_ascii=False) + "\n")
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    return path


# ---------------------------------------------------------------------------
# 8. main
#    SPEC §6.
# ---------------------------------------------------------------------------
def main(argv=None):
    workspace = os.path.dirname(_HERE)
    p = argparse.ArgumentParser(prog="mediator.py", description="P17 Mediator: field maturity and spine proposals.")
    sp = p.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("scan", help="discover digests, classify, report")
    s.add_argument("--root", default=workspace)
    s.add_argument("--pattern", default=DEFAULT_PATTERN)
    s.add_argument("--propose", action="store_true", help="export a proposal for each Fact finding")
    s.add_argument("--out", help="folder for proposals (with --propose)")
    s.add_argument("--inherits", help="the governance in force (scp_id)")
    s.add_argument("--foundation", default=os.path.join(workspace, "the-full-stack"))
    args = p.parse_args(argv)

    inherits = None
    if args.propose:
        if not args.out:
            print("--propose needs --out", file=sys.stderr)
            return 2
        try:
            inherits = args.inherits or current_governance(args.foundation)
        except FileNotFoundError as e:
            print(f"no governance in force: {e}; give --inherits or --foundation", file=sys.stderr)
            return 2
        if not forge_time.is_ratified_scp_id(inherits):
            print(f"--inherits is not a ratified scp_id: {inherits!r}", file=sys.stderr)
            return 2

    digests = load_digests(args.root, args.pattern)
    if not digests:
        print(f"no digests found under {args.root} ({args.pattern})")
        return 0
    findings = classify(extract_observations(digests))
    print(f"{len(digests)} digest(s), {len(findings)} field(s)")
    for f in sorted(findings, key=lambda f: (f.declaration_type, f.field_key)):
        print(f"{f.declaration_type}  {'/'.join(f.field_key)}  {f.tier}  consumers: {', '.join(f.consumers)}  "
              f"count {f.total_observation_count}  oldest {f.max_age_days:.0f} d")
    if args.propose:
        for f in findings:
            if f.tier == TIER_FACT:
                print(f"proposal: {export_proposal(f, args.out, inherits)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
