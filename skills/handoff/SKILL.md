---
name: handoff
description: "Generate a session-continuity document for resuming dev-team work in a new session. Use when the user says 'handoff', 'save progress', 'session summary', 'wrap up for now', 'continue later', or wants to preserve current dev-team state."
argument-hint: optional notes for the next session
---

# Session Handoff

Generate a compact session-continuity document that enables a new session to resume this dev-team workflow from exactly where it stopped.

## Process

1. **Read the progress ledger**: Read `docs/progress.md` for current task state (goal, AC-IDs, task table, decisions, open questions, session state)
2. **Read active artifacts**: Check which docs/ files exist and their state:
   - `docs/prd.md` — exists? debate state?
   - `docs/architecture.md` — exists? reviewed?
   - `docs/design.md` — exists? reviewed?
   - `docs/plan.md` — exists? debate state?
   - `docs/test-plan.md` — exists?
3. **Capture session state** from conversation context:
   - Current phase (0–5) and sub-step
   - Current slice number (if in implementation)
   - Debate state (if mid-debate: cycle, unresolved CH-* IDs, pending action)
   - Re-dispatch attempt counts per scope
   - Pending dispatches (what was about to happen next)
   - User decisions made verbally but not yet in docs
4. **Capture environment**:
   - Detected stack and versions
   - Profile (Micro/Standard/Full) and triage score
   - Run counter
   - Aesthetic/design-style choice (if UI work)
   - Input inventory paths
5. **Write `docs/handoff.md`** using the format below
6. **Update `docs/progress.md`** session state section if it exists

## Handoff Document Format

Write `docs/handoff.md`:

```
# Session Handoff

Generated: [timestamp]
Task: [one-line goal from progress.md]
Profile: [Micro/Standard/Full] | Score: [N] | Runs: [N/threshold]

## Resume Point

Phase: [0–5] | Step: [specific step]
Slice: [N of M] | Status: [in-progress / between slices / not started]
Next action: [exactly what the coordinator should do next]

## Artifacts

| Artifact | Path | State | Gate |
|----------|------|-------|------|
| PRD | docs/prd.md | [draft/debated/reviewed/final/absent] | [debate cycle N / consensus / reviewed / N/A] |
| Architecture | docs/architecture.md | ... | ... |
| Design | docs/design.md | ... | ... |
| Plan | docs/plan.md | ... | ... |
| Test Plan | docs/test-plan.md | ... | ... |
| Progress | docs/progress.md | current | — |

## Debate State (if mid-debate)

Artifact: [prd/plan]
Cycle: [0–3]
Unresolved: [CH-*-001, CH-*-002, ...]
Last verdict: [CONSENSUS/REVISE/ARBITRATION_REQUIRED]
Pending: [creator revision / challenger recheck / arbitration]

## Environment

Stack: [detected stack and framework]
Versions: [key dependency versions]
Design aesthetic: [if applicable]
Input inventory: [paths or "none"]

## Pending User Decisions

[OQ-IDs awaiting response, or questions asked but not answered]

## Verbal Decisions Not Yet in Docs

[User decisions from conversation not yet written to docs/]

## Blocked Items

[BLOCKED statuses and their blockers]

## Notes for Next Session

[User's $ARGUMENTS or additional context]
```

## Rules

- Do NOT duplicate information already in `docs/progress.md` — reference it by section
- Do NOT include source code or large diffs — reference file paths
- The handoff document is a SNAPSHOT, not a replacement for `docs/progress.md`
- If no dev-team work is in progress (no `docs/progress.md`, no task artifacts), report that there is nothing to hand off
- Keep the document concise — a new session should be able to parse it in under 30 seconds
