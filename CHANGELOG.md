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
