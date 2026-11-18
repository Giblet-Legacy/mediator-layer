# CHANGELOG — mediator-layer (P17 Mediator)

CHANGELOG.md — build history for P17 Mediator, latest entry at top.

Function:
    Records the Good / Bad / Ugly of every build step for this layer.
    Updated at every sign-off. The format never changes shape, even
    when a section is empty.

## [Unreleased]

### Good

- (none)

### Bad

- (none)

### Ugly

- (none)

## [v1.1.0] — 2026-11-18 — FROZEN

### Good

- Frozen at 1.1.0 (James: "freeze"). No tie to the-full-stack. James: "the
  forge stack was for reference only and not meant to be a layer
  involved in the legacy program." `SPEC_V1_1.md` and `mediator_v1_1.py`
  over the frozen mediator.py: no `--foundation`, no governance read
  from it, `inherits` given or null, and discovery skips a
  `the-full-stack` folder. Classification is v1's own code, re-exported.
  v1 is never patched.
- `test_mediator_v1_1.py` (5 tests, run red first) and
  `test_mediator_at_v1_1.py`: the 1.0.0 suite with test 12 (agreement with
  master_mediator) replaced by a no-reach check. The 1.0.0 suite is kept
  byte-identical in `archive/1.0.0/`, and `pytest.ini` skips it. 18/18.

- Named for the version it ships (roadmap NAMING.md): built as
  mediator_v2.py / SPEC_V2.md / test_mediator_v2.py, renamed before the
  freeze to mediator_v1_1.py / SPEC_V1_1.md / test_mediator_v1_1.py; the
  carried 1.0.0 suite is test_mediator_at_v1_1.py. Capsule test added. 19/19.

### Bad

- The sealed `sc/p17-mediator-v1.sc.json` still inherits forge-stack
  governance-v6, and SPEC.md 1.0.0 still calls the-full-stack "the
  foundation". Both are signed history and stay as they are. `sc/p17-mediator-v2.sc.json`
  (pins SPEC_V1_1.md and SPEC.md, supersedes v1, inherits null) is
  unsigned until James seals it with ../forge-time/seal_capsule.py.
- With `inherits` null, mediator_v1_1 builds through v1's checks using a stand-in
  id that it then clears. It works, but it is a seam to remember.

### Ugly

- (none)

## [v1.0.0] — 2026-11-14 — FROZEN

### Good

- Frozen at 1.0.0 on James's sign-off ("yes freeze 16 and 17"). Tests
  13/13 on the laptop; run on the S24 by James ("tested on y phone ok").
- `sc/p17-mediator-v1.sc.json` sealed by James on the laptop (P3 Freeze v2, document_sha256
  df00ef972592c5a3…); verified under P3 against its key_id before commit.
- `mediator.py`, `SPEC.md` 1.0.0, `test_mediator.py` (13 tests, run
  red first): the foundation's Master Mediator as primitive layer P17.
  Discovery (read-only), classification (five tiers, never across
  declaration types), unsigned spine-update proposals for Fact fields,
  and a `scan` command. Timestamps and scp_ids through P16.
- The foundation's three gaps are fixed from the start: three
  consumers need 30 days for Fact (M1); `inherits` is required and
  checked, or read from the foundation's governance nothing supersedes
  (M2); loading survives a file that changes after discovery (M3).
- Agrees with the foundation's fixed master_mediator on its real
  digests (ccemk2, keystone_gate: 5 digests, 60 fields, same tiers).
- `sc/p17-mediator-v1.sc.json`: the layer's primitive capsule, pinning
  SPEC.md; unsigned until James seals it.
- Built on James's delegation ("fix all add as primitive capsule and
  intigrate as repo and layer"; "P17 mediator-layer").

### Bad

- The capsule test pinned `"signature": null`, so sealing the capsule
  made it fail. It now requires the seal: P3 must accept the capsule
  under its own key_id (P1 `did_key_decode`), and a changed capsule fails.
- No consumer in this workspace exports a digest yet, so `scan` here
  finds nothing. Producing digests (the Cockpit, the Legacy, the
  Weaver, SCP Substrate) is the next step (NOTES Q2).

### Ugly

- (none)
