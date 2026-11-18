# Forge Stack Context — P17 Mediator

CLAUDE.md — Context briefing for AI assistants working in this repository.

Function:
    Instructs the AI assistant on the strict architectural rules of the
    Forge Stack. Do not hallucinate external frameworks. Reason strictly
    within these boundaries.

## The Immutable Rule
Never rewrite a primitive. Add a layer. Once mediator.py is frozen, a
change is a mediator_v1_1.py over it, after a SPEC_V1_1.md describes it.

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
- the-full-stack (JamesTheGiblet) is reference only, never a layer or
  a dependency (James, 2026-11-18; SPEC_V1_1.md). P17's idea came from
  its master_mediator. Never import it, test against it, read its
  governance or treat it as authority. Use mediator_v1_1.py.
- `inherits` is never hardcoded: it is the `--inherits` given, or null.
- The AI never seals the capsule; the owner does.
