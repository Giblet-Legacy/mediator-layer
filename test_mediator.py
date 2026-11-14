"""
test_mediator.py — P17 Mediator test suite

Function:
    Executable expression of SPEC.md 1.0.0. Written before mediator.py
    and run red first.

Functions in this file (pytest-collected):
    1.  test_discovery
    2.  test_load_survives_changes_after_discovery
    3.  test_extract_observations
    4.  test_tier_boundaries
    5.  test_three_consumers_need_thirty_days
    6.  test_never_merges_across_types
    7.  test_build_proposal
    8.  test_proposal_needs_a_ratified_inherits
    9.  test_current_governance
    10. test_export_proposal_atomic_lf
    11. test_command
    12. test_agrees_with_the_foundation
    13. test_capsule_pins_spec_and_seals

Helpers:
    14. _digest — write a digest capsule into a fake workspace
    15. _obs    — a FieldObservation

Layer:    P17 — Mediator
Spec:     SPEC.md 1.0.0
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)
"""

import hashlib
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

import forge_time
import mediator as m

HERE = os.path.dirname(os.path.abspath(__file__))
FOUNDATION = os.path.join(os.path.dirname(HERE), "the-full-stack")
NOW = datetime(2026, 11, 14, 18, 0, 0, tzinfo=timezone.utc)


def _ago(days):
    return forge_time.format_iso_utc(NOW - timedelta(days=days))


# 14. _digest
def _digest(root, repo, name, decl):
    folder = os.path.join(str(root), repo, "sc")
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"scp_id": f"x/{repo}-v1", "declaration": decl, "signature": None}, f)
    return path


# 15. _obs
def _obs(consumer, age, count=50, type_="usage_digest", key=("ns", "FACT")):
    return m.FieldObservation(consumer=consumer, declaration_type=type_, field_key=key,
                              observation_count=count, age_days=age)


# 1. test_discovery
def test_discovery(tmp_path):
    a = _digest(tmp_path, "a", "usage.sc.json", {"type": "usage_digest", "consumer": "a", "fields": []})
    _digest(tmp_path, "b", "plain.sc.json", {"type": "primitive_layer"})
    with open(os.path.join(str(tmp_path), "b", "sc", "broken.sc.json"), "w") as f:
        f.write("{ nope")
    c = _digest(tmp_path, "c", "hal.sc.json", {"type": "hal_digest", "consumer": "c", "seals": []})
    assert m.find_digest_paths(str(tmp_path)) == sorted([a, c])
    assert [d["_source_path"] for d in m.load_digests(str(tmp_path))] == sorted([a, c])


# 2. test_load_survives_changes_after_discovery
def test_load_survives_changes_after_discovery(tmp_path, monkeypatch):
    good = _digest(tmp_path, "a", "u.sc.json", {"type": "usage_digest", "consumer": "a"})
    broken = os.path.join(str(tmp_path), "broken.sc.json")
    with open(broken, "w") as f:
        f.write("{ nope")
    no_longer = _digest(tmp_path, "b", "x.sc.json", {"type": "primitive_layer"})
    monkeypatch.setattr(m, "find_digest_paths", lambda root, pattern=None: [good, broken, no_longer,
                                                                            os.path.join(str(tmp_path), "gone")])
    assert [d["_source_path"] for d in m.load_digests(str(tmp_path))] == [good]


# 3. test_extract_observations
def test_extract_observations():
    digests = [
        {"declaration": {"type": "usage_digest", "consumer": "a", "fields": [
            {"namespace": "ns", "lens": "FACT", "observation_count": 12, "first_seen": _ago(10)},
            {"namespace": "ns", "lens": "UNKNOWN", "observation_count": 3, "first_seen": "yesterday"},
            {"lens": "no namespace"}]}},
        {"declaration": {"type": "hal_digest", "fields": [], "seals": [
            {"entity_class": "person", "tier": 3, "seal_count": 5}]}},
        {"declaration": {"type": "something_else_digest", "fields": [{"x": 1}]}},
    ]
    obs = m.extract_observations(digests, now=NOW)
    assert [(o.consumer, o.declaration_type, o.field_key, o.observation_count, round(o.age_days)) for o in obs] == [
        ("a", "usage_digest", ("ns", "FACT"), 12, 10),
        ("a", "usage_digest", ("ns", "UNKNOWN"), 3, 0),
        ("unknown", "hal_digest", ("person", "3"), 5, 0)]


# 4. test_tier_boundaries
def test_tier_boundaries():
    tier = lambda *obs: m.classify(list(obs))[0].tier  # noqa: E731
    assert tier(_obs("a", 6, 10)) == m.TIER_HYPOTHESIS
    assert tier(_obs("a", 7, 9)) == m.TIER_HYPOTHESIS
    assert tier(_obs("a", 7, 10)) == m.TIER_EXPERIMENTAL
    assert tier(_obs("a", 29, 100)) == m.TIER_EXPERIMENTAL
    assert tier(_obs("a", 30, 100)) == m.TIER_CANDIDATE
    assert tier(_obs("a", 29), _obs("b", 29)) == m.TIER_EXPERIMENTAL
    assert tier(_obs("a", 30), _obs("b", 30)) == m.TIER_EMERGENT
    assert tier(_obs("a", 89), _obs("b", 89)) == m.TIER_EMERGENT
    assert tier(_obs("a", 90), _obs("b", 90)) == m.TIER_FACT
    f = m.classify([_obs("a", 40, 20), _obs("b", 95, 30)])[0]
    assert (f.consumers, f.total_observation_count, f.max_age_days) == (["a", "b"], 50, 95.0)


# 5. test_three_consumers_need_thirty_days
def test_three_consumers_need_thirty_days():
    assert m.classify([_obs("a", 0), _obs("b", 0), _obs("c", 0)])[0].tier != m.TIER_FACT
    assert m.classify([_obs("a", 29), _obs("b", 29), _obs("c", 29)])[0].tier != m.TIER_FACT
    assert m.classify([_obs("a", 30), _obs("b", 30), _obs("c", 30)])[0].tier == m.TIER_FACT


# 6. test_never_merges_across_types
def test_never_merges_across_types():
    found = m.classify([_obs("a", 100, 200, "usage_digest", ("same", "key")),
                        _obs("b", 100, 200, "primitive_digest", ("same", "key"))])
    assert len(found) == 2 and all(f.tier != m.TIER_FACT for f in found)


def _fact():
    return m.MaturityFinding(declaration_type="usage_digest", field_key=("domain.trading.btc", "FACT"),
                             tier=m.TIER_FACT, consumers=["a", "b", "c"], total_observation_count=5000,
                             max_age_days=120.0)


# 7. test_build_proposal
def test_build_proposal():
    cap = m.build_proposal(_fact(), "forge-stack/governance-v6", created="2026-11-14T18:00:00Z")
    assert cap["scp_id"] == "forge-stack/mediator/spine-update-usage-digest-domain-trading-btc-fact-v1"
    assert forge_time.is_ratified_scp_id(cap["scp_id"])
    assert (cap["scp_version"], cap["created"], cap["inherits"], cap["licence"], cap["signature"]) == \
        ("1.2.0", "2026-11-14T18:00:00Z", "forge-stack/governance-v6", "MSL-1.0", None)
    d = cap["declaration"]
    assert d["type"] == "spine_update_proposal" and d["evidence"]["tier"] == m.TIER_FACT
    assert d["evidence"]["consumers"] == ["a", "b", "c"] and d["affected_spine_files"]
    assert forge_time.is_iso_utc(m.build_proposal(_fact(), "forge-stack/governance-v6")["created"])
    with pytest.raises(ValueError):
        m.build_proposal(m.MaturityFinding("usage_digest", ("k",), m.TIER_CANDIDATE, ["a"], 200, 40.0),
                         "forge-stack/governance-v6")


# 8. test_proposal_needs_a_ratified_inherits
def test_proposal_needs_a_ratified_inherits():
    for bad in (None, "", "governance v6", "forge-stack/governance-v6\n"):
        with pytest.raises(ValueError):
            m.build_proposal(_fact(), bad)


# 9. test_current_governance
def test_current_governance(tmp_path):
    sc = tmp_path / "sc"
    sc.mkdir()
    with pytest.raises(FileNotFoundError):
        m.current_governance(str(tmp_path))
    for n, sup in ((1, None), (2, "forge-stack/governance-v1"), (3, "forge-stack/governance-v2")):
        decl = {"supersedes": sup} if sup else {}
        (sc / f"forge-stack-governance-v{n}.sc.json").write_text(
            json.dumps({"scp_id": f"forge-stack/governance-v{n}", "declaration": decl}), encoding="utf-8")
    (sc / "forge-stack-governance-v9.sc.json").write_text("{ broken", encoding="utf-8")
    assert m.current_governance(str(tmp_path)) == "forge-stack/governance-v3"


# 10. test_export_proposal_atomic_lf
def test_export_proposal_atomic_lf(tmp_path, monkeypatch):
    path = m.export_proposal(_fact(), str(tmp_path / "out"), "forge-stack/governance-v6")
    assert os.path.basename(path) == "spine-update-usage-digest-domain-trading-btc-fact-v1.sc.json"
    raw = open(path, "rb").read()
    assert b"\r" not in raw and json.loads(raw)["signature"] is None

    def boom(*a, **k):
        raise OSError("disk full")

    monkeypatch.setattr(os, "replace", boom)
    with pytest.raises(OSError):
        m.export_proposal(_fact(), str(tmp_path / "out"), "forge-stack/governance-v6")
    assert open(path, "rb").read() == raw and sorted(os.listdir(tmp_path / "out")) == [os.path.basename(path)]


# 11. test_command
def test_command(tmp_path, capsys):
    ws = tmp_path / "ws"
    entries = [{"namespace": "ns", "lens": "FACT", "observation_count": 40, "first_seen": "2020-01-01T00:00:00Z"}]
    for c in ("a", "b", "c"):
        _digest(ws, c, "usage.sc.json", {"type": "usage_digest", "consumer": c, "fields": entries})
    assert m.main(["scan", "--root", str(ws)]) == 0
    out = capsys.readouterr().out
    assert "usage_digest" in out and "Fact" in out and "a, b, c" in out
    out_dir = tmp_path / "proposals"
    assert m.main(["scan", "--root", str(ws), "--propose", "--out", str(out_dir),
                   "--foundation", str(tmp_path / "nowhere")]) == 2
    assert not out_dir.exists()
    assert m.main(["scan", "--root", str(ws), "--propose", "--out", str(out_dir),
                   "--inherits", "forge-stack/governance-v6"]) == 0
    assert [p.name for p in out_dir.iterdir()] == ["spine-update-usage-digest-ns-fact-v1.sc.json"]
    assert m.main(["scan", "--root", str(tmp_path / "empty")]) == 0


# 12. test_agrees_with_the_foundation
def test_agrees_with_the_foundation():
    if not os.path.isdir(os.path.join(FOUNDATION, "master_mediator")):
        pytest.skip("the-full-stack is not checked out beside this layer")
    sys.path.insert(0, FOUNDATION)
    try:
        from master_mediator import classifier as fc, discovery as fd, proposal as fp
    finally:
        sys.path.remove(FOUNDATION)
    theirs = fc.classify(fc.extract_observations(fd.load_digests(fd.Path(FOUNDATION)), now=NOW))
    ours = m.classify(m.extract_observations(m.load_digests(FOUNDATION, "consumer/**/sc/*.sc.json"), now=NOW))
    key = lambda f: (f.declaration_type, f.field_key, f.tier, tuple(f.consumers), f.total_observation_count)  # noqa
    assert sorted(map(key, ours)) == sorted(map(key, theirs)) and ours
    assert m.current_governance(FOUNDATION) == fp.current_governance(fd.Path(FOUNDATION))


# 13. test_capsule_pins_spec_and_seals
def test_capsule_pins_spec_and_seals(tmp_path):
    with open(os.path.join(HERE, "sc", "p17-mediator-v1.sc.json"), encoding="utf-8") as f:
        capsule = json.load(f)
    with open(os.path.join(HERE, "SPEC.md"), "rb") as f:
        assert capsule["declaration"]["spec_sha256"] == hashlib.sha256(f.read()).hexdigest()
    assert capsule["scp_id"] == "forge-stack/primitive/p17-mediator-v1"
    assert capsule["declaration"]["layer"] == "P17"
    assert forge_time.is_iso_utc(capsule["created"]) and forge_time.is_ratified_scp_id(capsule["inherits"])
    assert m.find_digest_paths(os.path.dirname(HERE), "mediator-layer/sc/*.sc.json") == []
    import seal_capsule
    import freeze_v2
    import envelope_v2
    # Sealed by the owner (2026-11-14): P3 accepts it under its own key_id.
    assert freeze_v2.verify_frozen_capsule(capsule, envelope_v2.did_key_decode(capsule["signature"]["key_id"]))
    capsule = {k: v for k, v in capsule.items() if k not in ("signature", "document_sha256")}
    copy = tmp_path / "c.sc.json"
    copy.write_text(json.dumps(capsule), encoding="utf-8")
    key = Ed25519PrivateKey.generate()
    seal_capsule.seal(str(copy), key)
    assert freeze_v2.verify_frozen_capsule(json.loads(copy.read_text(encoding="utf-8")), key.public_key())
