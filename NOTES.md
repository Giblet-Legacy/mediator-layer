# NOTES — mediator-layer (P17 Mediator)

NOTES.md — open questions, divergences and decisions for P17 Mediator.

Function:
    Records open questions, divergences from the foundation and
    decisions for P17. Owner: James.

## Open questions

- **Q1 — Sign off P17 at 1.0.0?** Built and green on the laptop
  (13/13). Not yet run on the S24. Raised 2026-11-14. Owner: James.
- **Q2 — Which consumers here export digests, and what do they
  report?** None do yet. Candidates: the Cockpit (claims by subject and
  face: usage_digest), the ledger (event kinds: chronoscribe_digest),
  HAL seals (hal_digest). Each is a consumer layer, not a P17 change.
  Raised 2026-11-14. Owner: James.
- **Q3 — Should the Legacy show the tiers and waiting proposals?** A
  panel would read P17's scan; approval stays with HAL. Raised
  2026-11-14. Owner: James.

## Divergences — from the foundation (master_mediator/)

- None in behaviour. P17 and the fixed foundation (CHANGELOG 6.1) give
  the same tiers on the same digests (tested). Differences of shape:
  one module, `inherits` required rather than defaulted, a
  `--pattern` for this workspace's layout, and P16 for time.

## Decisions

- Three consumers need 30 days for Fact (the time Emergent needs);
  two need 90. Decided by the VS Code AI on James's delegation
  (2026-11-14, "fix all"); the same rule is in the foundation's 6.1.
