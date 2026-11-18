"""
mediator_v1_1.py — P17 Mediator 1.1.0: mediator.py without the-full-stack

Function:
    Implements SPEC_V1_1.md over the frozen mediator.py (SPEC 1.0.0).
    James, 2026-11-18: the-full-stack was for reference only and never a
    layer of the Legacy. So 1.1.0 has no --foundation, reads no governance
    from it, lets a proposal's inherits be given or null, and never
    discovers digests inside a the-full-stack folder. Classification
    and everything else is v1's own code, re-exported unchanged. It
    never signs, merges or edits a layer.

Public API:
    1. find_digest_paths(root, pattern) -> list[str]
    2. load_digests(root, pattern) -> list[dict]
    3. build_proposal(finding, inherits=None, created=None) -> dict
    4. export_proposal(finding, out_dir, inherits=None) -> str
    5. main(argv=None) -> int
    Re-exported from mediator.py: extract_observations, classify,
    FieldObservation, MaturityFinding, DIGEST_SPECS, DEFAULT_PATTERN, TIER_*

Layer:    P17 — Mediator
Depends:  mediator.py 1.0.0, P16 Time (forge_time)
Spec:     SPEC_V1_1.md
Version:  1.1.0
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)
"""

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

import mediator as _v1
from mediator import (  # noqa: F401  (re-exported unchanged)
    DEFAULT_PATTERN, DIGEST_SPECS, TIER_CANDIDATE, TIER_EMERGENT, TIER_EXPERIMENTAL, TIER_FACT,
    TIER_HYPOTHESIS, FieldObservation, MaturityFinding, classify, extract_observations,
)
import forge_time

_EXCLUDED = "the-full-stack"  # reference only (SPEC_V1_1 §1): never read as a consumer


def _excluded(root, path):
    try:
        parts = Path(path).resolve().relative_to(Path(root).resolve()).parts
    except ValueError:
        return False
    return bool(parts) and parts[0] == _EXCLUDED


# ---------------------------------------------------------------------------
# 1. find_digest_paths
#    SPEC_V1_1 §2: v1's, minus anything under root/the-full-stack.
# ---------------------------------------------------------------------------
def find_digest_paths(root, pattern=DEFAULT_PATTERN):
    return [p for p in _v1.find_digest_paths(root, pattern) if not _excluded(root, p)]


# ---------------------------------------------------------------------------
# 2. load_digests
# ---------------------------------------------------------------------------
def load_digests(root, pattern=DEFAULT_PATTERN):
    digests = []
    for path in find_digest_paths(root, pattern):
        data = _v1._read_json(path)
        if _v1._digest_type(data):
            data["_source_path"] = str(path)
            digests.append(data)
    return digests


# ---------------------------------------------------------------------------
# 3. build_proposal
#    SPEC_V1_1 §2: inherits optional; given means ratified (M2); absent means null.
# ---------------------------------------------------------------------------
def build_proposal(finding, inherits=None, created=None):
    if inherits is not None:
        return _v1.build_proposal(finding, inherits, created)
    capsule = _v1.build_proposal(finding, "none-v0", created)  # v1 checks; the stand-in never leaves here
    capsule["inherits"] = None
    return capsule


# ---------------------------------------------------------------------------
# 4. export_proposal
#    The same atomic LF write as v1, with the 1.1.0 builder (v1 is never patched).
# ---------------------------------------------------------------------------
def export_proposal(finding, out_dir, inherits=None):
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
# 5. main
#    SPEC_V1_1 §2: no --foundation, no default governance.
# ---------------------------------------------------------------------------
def main(argv=None):
    workspace = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    p = argparse.ArgumentParser(prog="mediator_v1_1.py", description="P17 Mediator 1.1.0: field maturity and spine proposals.")
    sp = p.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("scan", help="discover digests, classify, report")
    s.add_argument("--root", default=workspace)
    s.add_argument("--pattern", default=DEFAULT_PATTERN)
    s.add_argument("--propose", action="store_true", help="export a proposal for each Fact finding")
    s.add_argument("--out", help="folder for proposals (with --propose)")
    s.add_argument("--inherits", help="a ratified scp_id the proposals inherit (else null)")
    args = p.parse_args(argv)

    if args.propose:
        if not args.out:
            print("--propose needs --out", file=sys.stderr)
            return 2
        if args.inherits is not None and not forge_time.is_ratified_scp_id(args.inherits):
            print(f"--inherits is not a ratified scp_id: {args.inherits!r}", file=sys.stderr)
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
                print(f"proposal: {export_proposal(f, args.out, args.inherits)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
