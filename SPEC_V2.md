# SPEC V2 — mediator-layer (P17 Mediator), changes over SPEC 1.0.0

SPEC_V2.md — what mediator_v2.py changes over the signed SPEC 1.0.0 and the frozen mediator.py.

Function:
    SPEC.md (1.0.0) is pinned by sha256 in the sealed
    sc/p17-mediator-v1.sc.json and is never edited, and mediator.py is
    frozen. This file states only what v2 changes. Where it is silent,
    SPEC.md 1.0.0 applies unchanged.

Layer:    P17 — Mediator
Depends:  SPEC.md 1.0.0, mediator.py 1.0.0, P16 Time
Version:  SPEC 2.0.0 (layer 1.1.0)
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)

---

## 1. Why

James, 2026-11-18: "the forge stack was for reference only and not
meant to be a layer involved in the legacy program." SPEC 1.0.0 called
the-full-stack "the foundation". It read the governance in force from
the-full-stack's `sc/` and made an agreement test against its
`master_mediator` mandatory. Both go. The Master Mediator is where P17's
idea came from, not something P17 answers to.

## 2. mediator_v2.py

A layer over mediator.py. It imports mediator.py and changes four
things:

- **`find_digest_paths(root, pattern)` and `load_digests(root, pattern)`**
  are v1's, minus any path whose first folder under `root` is
  `the-full-stack`. The default workspace scan never reads it.
- **`build_proposal(finding, inherits=None, created=None)`**: `inherits`
  is optional. If it is given, it must be a ratified scp_id, as in v1
  (M2). If it is not given, it is `null`: no governance from the-full-stack
  stands over a proposal. Everything else is v1's output, byte for byte.
- **`export_proposal(finding, out_dir, inherits=None)`**: v1's atomic
  LF write, using the v2 builder.
- **Command:** `python mediator_v2.py scan [--root DIR] [--pattern P]
  [--propose --out DIR [--inherits ID]]`. There is no `--foundation`,
  and no default governance. `--propose` without `--out` and a
  non-ratified `--inherits` both exit 2 and write nothing.

`current_governance` is not part of v2. It stays in mediator.py as
frozen history.

Unchanged and re-exported: `extract_observations`, `classify`, the
tiers, `FieldObservation`, `MaturityFinding`, `DIGEST_SPECS`,
`DEFAULT_PATTERN`. M1 and M3 hold as in 1.0.0.

## 3. Tests

- `test_mediator_v1_1.py`: the 1.0.0 suite for mediator.py, with test 12
  (agreement with the-full-stack) replaced by
  `test_never_reaches_the_full_stack`. The 1.0.0 file is kept
  byte-identical in `archive/1.0.0/`.
- `test_mediator_v2.py`: discovery skips the-full-stack; inherits given
  or null; export defaults to null; the command without `--foundation`;
  and the shared parts are v1's own objects.

## 4. Capsule

`sc/p17-mediator-v1.sc.json` stays as sealed (its `inherits` of
forge-stack governance is history). A v2 capsule naming this file is
for James to seal when he freezes 1.1.0.

---

## Document control

- **SPEC 2.0.0** — 2026-11-18, by the VS Code AI on James's word ("yes
  in the order you stated", removing the the-full-stack ties). Not
  signed. Layer 1.1.0 is not frozen.
