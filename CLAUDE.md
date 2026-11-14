# Forge Stack Context — P17 Mediator

CLAUDE.md — Context briefing for AI assistants working in this repository.

Function:
    Instructs the AI assistant on the strict architectural rules of the
    Forge Stack. Do not hallucinate external frameworks. Reason strictly
    within these boundaries.

## The Immutable Rule
Never rewrite a primitive. Add a layer. Once mediator.py is frozen, a
change is a mediator_v2.py over it, after a SPEC_V2.md describes it.

## Propose, never decide
P17 reads and proposes. It never signs, never merges, never edits a
layer or the foundation. A Fact finding becomes an unsigned proposal;
the owner decides through HAL (P15). Growth stays inside HAL.

## Dual-Device Workflow
We build on an S24 (Termux) and a laptop (VS Code). State is confirmed,
never assumed. Always use LF line endings. Good/Bad/Ugly CHANGELOG,
latest at top. British English (-ise).

## Header Discipline
Every file has a top header paragraph explaining its function. Every
function has a numbered header (e.g. `# 4. classify`).

## P17 Architecture Specifics
- Depends on P16 Time (`forge_time`) for timestamps and the scp_id rule.
- From the foundation's master_mediator (JamesTheGiblet/the-full-stack),
  with hardening 6.1 M1–M3 built in. Keep the two in agreement: the
  agreement test runs P17 and the foundation on the same real digests.
- `inherits` is never hardcoded: given, or read from the foundation's
  sc/ (the governance nothing supersedes).
- The AI never seals the capsule; the owner does.
