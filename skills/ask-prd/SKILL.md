---
name: ask-prd
description: Runs a product-analyst, adversarial-reviewer, and doc-reviewer mini-orchestration to produce a debated and reviewed PRD.
argument-hint: product or feature to formalize requirements for
disable-model-invocation: true
---

# PRD Mini-Orchestrator

You orchestrate `product-analyst` → adversarial debate → `doc-reviewer`. You do not implement or review the PRD yourself.

## Task

$ARGUMENTS

## Actions

1. **Gather project context** (read-only):
   - Run `git status` to understand current state
   - Use `Glob("**/package.json")` and `Glob("**/pyproject.toml")` to detect stack
   - Use `Glob("docs/*.md")` to check for existing documentation

2. **Dispatch creator** using the Agent tool:
   - `subagent_type: "dev-team:product-analyst"`
   - Include the full task from `$ARGUMENTS`
   - Include detected project structure and stack
   - If existing project: instruct to "Read the codebase to understand current state and derive requirements"
   - Instruct to "Formalize the requirements into a PRD. Save to docs/prd.md"
   - Include stack-specific phrases matching the detected stack to trigger skill injection
   - Include the report reminder (below)

3. **Initial challenge**: dispatch internal read-only `dev-team:adversarial-reviewer` with `Mode: prd` and `Pass: initial`. It assigns stable `CH-PRD-*` IDs and may return only `CONSENSUS` or `REVISE`. This pass consumes no debate cycle.
4. **Debate cycles 1–3**: on `REVISE`, re-dispatch product-analyst with every unresolved ID and require `accepted_and_fixed`, `rejected_with_evidence`, or `needs_decision` per ID; then re-dispatch the challenger. Each revision + recheck consumes one cycle. IDs remain stable; rechecks may assign new IDs only for defects introduced by the revision. Cycle 4 is forbidden. Full consensus requires verified fixes, evidence-backed rejections, no `needs_decision`, and mitigation, verification, or explicit acceptance for every residual risk.
5. **Ordinary review or arbitration**:
   - On challenger `CONSENSUS` with no unresolved IDs, dispatch `dev-team:doc-reviewer` for a full PRD review. On concerns, re-dispatch product-analyst and then doc-reviewer, maximum 2 ordinary reworks.
   - After an unresolved third recheck, the challenger returns `ARBITRATION_REQUIRED`; dispatch doc-reviewer with the complete PRD and ledger to arbitrate all items and perform the full review together. A successful result needs no additional ordinary review.
   - On arbitration `NEEDS_CONTEXT`, ask the user. A non-material answer is applied by product-analyst and verified by doc-reviewer without restarting debate; a change to goals, acceptance criteria, architecture assumptions, slice boundaries, or constraints is material, increments the artifact version, and restarts at the initial pass.
6. **Present the result** only after consensus + successful ordinary review, or successful arbitration/full review. Keep state in orchestration context; create neither `docs/progress.md` nor a challenge file.

Every dispatch includes the original request, artifact path/version, initial pass or cycle/max, complete stable ledger, dispositions/evidence, verdict, unresolved IDs, related documents, scope, stack/version context, output format, and report reminder.

## Report Reminder (include in agent prompt)

The agent's own prompt mandates the structured report protocol (Status, Files changed, Summary, Evidence, Criteria...). Add this single line to the dispatch:

"Reminder: Status DONE requires the Evidence field with fresh command output (or citations for read-only work); failing checks forbid DONE."

When presenting the result, flag any DONE report lacking Evidence as unverified.
