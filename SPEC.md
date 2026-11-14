# SPEC — mediator-layer (P17 Mediator)

SPEC.md — the complete layer specification for P17 Mediator.

Function:
    This document is the authoritative specification for primitive
    layer P17 of the Forge Stack: the Master Mediator, the stack's way
    to grow on its own without changing itself. It reads the digests
    consumers export, classifies how mature each field they report is,
    and, for a field that has become Fact, writes an unsigned
    spine-update proposal for HAL and the owner. It proposes; it never
    merges, signs or edits a layer.

Layer:     P17 — Mediator
Depends:   P16 Time (timestamps, scp_id rule)
Consumed:  The Legacy (later), the owner through HAL (P15)
Version:   SPEC 1.0.0
Licence:   MSL-1.0
Author:    James Gilbert (Giblets Forge)

---

## 1. Why P17

James (2026-11-14) shared the foundation's Master Mediator
(JamesTheGiblet/the-full-stack `master_mediator/`, ROADMAP Part II
Phase 20) and asked for it to be fixed and brought into this stack as
a primitive layer with its own repo. The three fixes made in the
foundation (CHANGELOG 6.1, M1–M3) are part of this SPEC from the start.

## 2. Digests

A digest is a `.sc.json` capsule whose `declaration.type` ends in
`_digest`. `DIGEST_SPECS` says where each known type keeps its entries
and how to read them (the foundation's registry, unchanged):

| type | list key | key fields | count field |
|---|---|---|---|
| usage_digest | fields | namespace, lens | observation_count |
| chronoscribe_digest | event_types | event_type | observation_count |
| leighton_digest | entities | entity_id | observation_count |
| hal_digest | seals | entity_class, tier | seal_count |
| primitive_digest | fields | field_path | observation_count |

Each entry may carry `first_seen` (P16 timestamp). A missing or
malformed `first_seen` counts as age 0, so a bad timestamp can never
raise a field's tier.

## 3. Discovery (read-only)

`find_digest_paths(root, pattern="*/sc/*.sc.json")` — every file under
`root` matching `pattern` whose JSON declares a `*_digest` type, sorted.
The default pattern fits this workspace, where each repo is a sibling
with its own `sc/`; the foundation's layout is
`consumer/**/sc/*.sc.json`. Unreadable or malformed files are skipped.

`load_digests(root, pattern=...)` loads each once; a file that
vanishes, breaks or stops being a digest after discovery is skipped
(M3). Each digest gets `_source_path`. Nothing is ever written.

## 4. Classification

`extract_observations(digests, now=None)` flattens every entry of a
known type into `FieldObservation(consumer, declaration_type,
field_key, observation_count, age_days)`; unknown types and malformed
entries are skipped. `consumer` is `declaration.consumer` ("unknown"
if absent).

`classify(observations)` groups by `(declaration_type, field_key)` —
never across types — and gives each group a tier, the first that
holds:

| tier | rule |
|---|---|
| Fact | ≥ 3 consumers and ≥ 30 days, or ≥ 2 consumers and ≥ 90 days |
| Emergent | ≥ 2 consumers and ≥ 30 days |
| Candidate | ≥ 100 observations and ≥ 30 days |
| Experimental | ≥ 10 observations and ≥ 7 days |
| Hypothesis | otherwise |

"Days" is the oldest `first_seen` in the group. Three consumers need
30 days (M1: the foundation's original rule made them Fact on day one).

## 5. Proposals

`build_proposal(finding, inherits, created=None)` — only for a Fact
finding (else ValueError) — returns an unsigned capsule:

- `scp_id`: `forge-stack/mediator/spine-update-<type>-<key>-v1`, each
  part slugged to `a-z0-9-` (anything else becomes `-`), checked with
  P16's `is_ratified_scp_id`;
- `scp_version` "1.2.0"; `created` a P16 timestamp; `inherits` as given
  (must be a ratified scp_id, else ValueError — there is no default,
  M2); `licence` "MSL-1.0"; `signature` null;
- `declaration`: type `spine_update_proposal`, an `intent` sentence,
  the `evidence` (type, key, consumers, total count, oldest age, tier),
  and `affected_spine_files` (P13 DataCube faces and the SCP spec,
  "if" they apply).

`current_governance(foundation_root)` — the foundation's governance in
force: among `sc/forge-stack-governance-vN.sc.json`, the one no other
supersedes (highest N if ambiguous); FileNotFoundError if none.

`export_proposal(finding, out_dir, inherits)` writes
`<out_dir>/<last scp_id segment>.sc.json` atomically, LF, and returns
the path. A human reads it, decides through HAL, and makes any spine
change by hand as a new layer; P17 never applies anything.

## 6. Command

    python mediator.py scan [--root DIR] [--pattern GLOB]
    python mediator.py scan --propose --out DIR [--inherits ID | --foundation DIR]

`scan` prints each finding (type, key, tier, consumers, count, age).
With `--propose`, each Fact finding is exported; `inherits` comes from
`--inherits`, else from `current_governance(--foundation)` (default
`../the-full-stack`), else the command stops with exit 2 and writes
nothing. Exit 0 otherwise, also when there are no digests.

## 7. The primitive capsule

`sc/p17-mediator-v1.sc.json` declares this layer, as P16's does (P16
SPEC §4): scp_id `forge-stack/primitive/p17-mediator-v1`, `inherits`
the governance in force, SPEC.md's SHA-256; committed unsigned, sealed
by the owner with `python ../forge-time/seal_capsule.py
sc/p17-mediator-v1.sc.json`. The layer's own capsule is not a digest,
so P17 never reads it as one.

## 8. Tests (test_mediator.py)

- Discovery: digests found by pattern; non-digests, broken files and
  this layer's own capsule skipped; a file that changes after
  discovery skipped (M3).
- Extraction: each registered type read by its keys; unknown types and
  malformed entries skipped; bad `first_seen` is age 0.
- Classification: every tier boundary; three consumers at 0 and 29
  days are not Fact, at 30 they are (M1); never merges across types.
- Proposals: shape, slugging, unsigned; non-Fact refused; `inherits`
  required and checked (M2); `current_governance` picks the
  unsuperseded capsule; export atomic and LF.
- Command: scan output; `--propose` without a governance stops (2) and
  writes nothing; with `--inherits` writes the proposals.
- Agreement: if `../the-full-stack` is present, P17 classifies the
  foundation's real digests to the same tiers as its fixed
  master_mediator, and `current_governance` agrees.
- The capsule pins this SPEC and seals under P3 v2.

---

## Document control

- **SPEC 1.0.0** — 2026-11-14, by the VS Code AI on James's
  delegation ("fix all add as primitive capsule and intigrate as repo
  and layer"; "P17 mediator-layer").
