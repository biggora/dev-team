---
name: resume
description: "Resume a previously interrupted dev-team session from its handoff state. Use when the user says 'resume', 'continue', 'pick up where we left off', or wants to continue dev-team work from a prior session."
argument-hint: optional focus override for the resumed session
---

# Session Resume

Resume a dev-team workflow from a prior session's handoff state.

## Process

1. **Locate handoff state** (check in order):
   a. `docs/handoff.md` — dedicated handoff document (most context)
   b. `docs/progress.md` — progress ledger (always authoritative)
   c. `docs/prd.md`, `docs/use-cases.md`, `docs/plan.md` — artifacts indicating prior work
   If none exist, report that no prior session state was found and offer to start fresh with `/dev-team`.

2. **Reconstruct coordinator state**:
   - Read `docs/handoff.md` for resume point, pending actions, environment, debate state
   - Read `docs/progress.md` for authoritative task table, AC-IDs, decisions, open questions
   - Read any artifacts listed in handoff to verify they exist and match expected state
   - Run `git log --oneline -10` and `git status` to check for changes since handoff

3. **Validate consistency**:
   - Verify artifact files match handoff's claimed state (file exists, PRD has expected AC-IDs)
   - If `docs/handoff.md` and `docs/progress.md` disagree, trust `docs/progress.md`
   - If files were modified since handoff (git log shows newer commits), note the divergence

4. **Re-verify the local stack** (skip if the ledger records `Local stack: N/A`):
   - Run `docker compose ps` and confirm every service reports healthy
   - If the stack is down, run `docker compose up -d --wait`, then re-check
   - Do this before resuming any slice or dispatching any verification — if the stack cannot be brought up, report that to the user before continuing rather than letting agents fall back to mocks

5. **Present resume plan to user**:
   - "Resuming from Phase [N], [step]. Last completed: [X]. Next action: [Y]."
   - List any pending user decisions from the handoff
   - Ask for confirmation before proceeding

6. **Resume the coordinator workflow**:
   - Apply the idempotency guard: check the ledger for completed artifacts, skip them
   - Continue from the exact next action specified in the handoff
   - Delete `docs/handoff.md` after successful resume (it's a one-time snapshot)
   - Invoke the appropriate coordinator skill (`/dev-team`, `/dev-team-node`, or `/dev-team-python`) with the reconstructed context

## Edge Cases

- **No handoff but progress.md exists**: reconstruct from the task table — find the last DONE entry, determine the next logical step
- **Stale handoff (code changed since)**: warn the user, show relevant git diff, ask whether to proceed or re-assess
- **Mid-debate resume**: re-read the artifact and unresolved CH-* IDs; re-dispatch from the pending action
- **User wants to change direction**: if $ARGUMENTS override the next action, update the ledger accordingly
- **Micro profile (no docs/progress.md)**: if only code artifacts exist with no ledger, offer to start fresh or ask the user to describe where they left off
