"""
test_mediator_v2.py — P17 Mediator v2 test suite

Function:
    Executable expression of SPEC_V2.md. Written before mediator_v2.py
    and run red first. v2 is mediator.py without the-full-stack: no
    --foundation, no governance read from it, a proposal's inherits is
    given or null, and discovery never reads a the-full-stack folder.

Functions in this file (pytest-collected):
    1. test_discovery_skips_the_full_stack
    2. test_proposal_inherits_given_or_null
    3. test_export_proposal_defaults_to_null
    4. test_command_without_foundation
    5. test_unchanged_from_v1

Helpers:
    6. _digest — write a digest capsule into a fake workspace
    7. _fact   — a Fact finding

Layer:    P17 — Mediator
Spec:     SPEC_V2.md (over SPEC.md 1.0.0)
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)
"""

import json
import os

import pytest

import mediator as m
import mediator_v2 as m2

ENTRIES = [{"namespace": "ns", "lens": "FACT", "observation_count": 40, "first_seen": "2020-01-01T00:00:00Z"}]


# 6. _digest
def _digest(root, repo, consumer):
    folder = os.path.join(str(root), repo, "sc")
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, "usage.sc.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"scp_id": f"x/{repo}-v1", "signature": None,
                   "declaration": {"type": "usage_digest", "consumer": consumer, "fields": ENTRIES}}, f)
    return path


# 7. _fact
def _fact():
    return m.MaturityFinding("usage_digest", ("ns", "FACT"), m.TIER_FACT, ["a", "b", "c"], 120, 40.0)


# 1. test_discovery_skips_the_full_stack
def test_discovery_skips_the_full_stack(tmp_path):
    keep = [_digest(tmp_path, r, r) for r in ("a", "b")]
    _digest(tmp_path, "the-full-stack", "zz-reference")
    assert m2.find_digest_paths(str(tmp_path)) == sorted(keep)
    assert [d["declaration"]["consumer"] for d in m2.load_digests(str(tmp_path))] == ["a", "b"]
    assert len(m.find_digest_paths(str(tmp_path))) == 3  # v1 is unchanged


# 2. test_proposal_inherits_given_or_null
def test_proposal_inherits_given_or_null():
    cap = m2.build_proposal(_fact(), created="2026-11-18T09:00:00Z")
    assert cap["inherits"] is None
    v1 = m.build_proposal(_fact(), "forge-stack/governance-v6", created="2026-11-18T09:00:00Z")
    assert {k: v for k, v in cap.items() if k != "inherits"} == {k: v for k, v in v1.items() if k != "inherits"}
    assert m2.build_proposal(_fact(), "legacy/charter-v1")["inherits"] == "legacy/charter-v1"
    for bad in ("", "governance v6", "legacy/charter-v1\n"):
        with pytest.raises(ValueError):
            m2.build_proposal(_fact(), bad)
    with pytest.raises(ValueError):
        m2.build_proposal(m.MaturityFinding("usage_digest", ("k",), m.TIER_CANDIDATE, ["a"], 200, 40.0))


# 3. test_export_proposal_defaults_to_null
def test_export_proposal_defaults_to_null(tmp_path):
    path = m2.export_proposal(_fact(), str(tmp_path))
    with open(path, "rb") as f:
        raw = f.read()
    assert b"\r\n" not in raw and json.loads(raw)["inherits"] is None


# 4. test_command_without_foundation
def test_command_without_foundation(tmp_path, capsys):
    ws = tmp_path / "ws"
    for c in ("a", "b", "c"):
        _digest(ws, c, c)
    _digest(ws, "the-full-stack", "zz-reference")
    out_dir = tmp_path / "proposals"
    assert m2.main(["scan", "--root", str(ws), "--propose", "--out", str(out_dir)]) == 0
    out = capsys.readouterr().out
    assert "3 digest(s)" in out and "zz-reference" not in out
    [p] = list(out_dir.iterdir())
    assert json.loads(p.read_text(encoding="utf-8"))["inherits"] is None
    assert m2.main(["scan", "--root", str(ws), "--propose", "--out", str(tmp_path / "x"),
                    "--inherits", "not ratified"]) == 2
    assert not (tmp_path / "x").exists()
    with pytest.raises(SystemExit):
        m2.main(["scan", "--root", str(ws), "--foundation", str(ws)])
    assert m2.main(["scan", "--root", str(ws), "--propose"]) == 2


# 5. test_unchanged_from_v1
def test_unchanged_from_v1():
    for name in ("extract_observations", "classify", "FieldObservation", "MaturityFinding",
                 "TIER_FACT", "DEFAULT_PATTERN"):
        assert getattr(m2, name) is getattr(m, name), name
    assert not hasattr(m2, "current_governance")
