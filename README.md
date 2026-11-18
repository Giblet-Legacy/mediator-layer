# mediator-layer — P17 Mediator

README.md — repository purpose and layer contract for P17 Mediator.

Function:
    This repository implements primitive layer P17 of the Forge Stack:
    the Master Mediator, the stack's way to grow on its own without
    changing itself. It reads the digests consumers export, classifies
    how mature each reported field is (Hypothesis → Experimental →
    Candidate → Emergent → Fact), and writes an unsigned spine-update
    proposal for each Fact field. It proposes; the owner decides
    through HAL (P15) and makes any change by hand, as a new layer.

Layer:    P17 — Mediator
Depends:  P16 Time (../forge-time)
Consumed: The owner through HAL; The Legacy (later)
Licence:  MSL-1.0
Author:   James Gilbert (Giblets Forge)
Status:   1.1.0 — frozen 2026-11-18 (SPEC_V1_1.md, mediator_v1_1.py); 1.0.0 frozen 2026-11-14 (SPEC.md), signed off by James

## Use

Since 1.1.0 (2026-11-18, SPEC_V1_1.md) use `mediator_v1_1.py`. the-full-stack
is reference only, so mediator_v1_1 never reads it, has no `--foundation`, and a
proposal's `inherits` is the `--inherits` you give, or `null`:

    python mediator_v1_1.py scan                               # this workspace, skipping the-full-stack
    python mediator_v1_1.py scan --propose --out proposals     # inherits null
    python mediator_v1_1.py scan --propose --out proposals --inherits <ratified scp_id>

The frozen 1.0.0 `mediator.py` (history; its `--foundation` defaults to
../the-full-stack):

    python mediator.py scan                                  # this workspace: */sc/*.sc.json
    python mediator.py scan --root ../the-full-stack --pattern "consumer/**/sc/*.sc.json"
    python mediator.py scan --propose --out proposals        # inherits read from ../the-full-stack
    python mediator.py scan --propose --out proposals --inherits forge-stack/governance-v6

A digest is a `.sc.json` whose `declaration.type` ends `_digest`
(usage, chronoscribe, leighton, hal, primitive; SPEC §2). No consumer
in this workspace exports one yet, so `scan` here reports none; on the
foundation it reads ccemk2's and keystone_gate's.

## Tiers (SPEC §4)

| tier | rule |
|---|---|
| Fact | ≥ 3 consumers and ≥ 30 days, or ≥ 2 consumers and ≥ 90 days |
| Emergent | ≥ 2 consumers and ≥ 30 days |
| Candidate | ≥ 100 observations and ≥ 30 days |
| Experimental | ≥ 10 observations and ≥ 7 days |
| Hypothesis | otherwise |

## The primitive capsule

`sc/p17-mediator-v1.sc.json` declares this layer and pins SPEC.md's
SHA-256. James sealed it on 2026-11-14 (P3 Freeze v2, key_id
`did:key:z6MkkVnQM4mpSND1jMBLDScpuUFF9BJTMoxYykurXQY89pjn`,
the same key as the Legacy ledger). A later capsule is sealed the same way. To seal it with your key:

    python ../forge-time/seal_capsule.py sc/p17-mediator-v1.sc.json

## Tests

    python -m pytest -q

Needs ../forge-time and, for the capsule test, ../envelope-layer,
../sign-layer, ../freeze-layer and ../record-layer. Since 1.1.0 nothing
is checked against the-full-stack's master_mediator; the 1.0.0 suite
that did is kept byte-identical in archive/1.0.0/.
