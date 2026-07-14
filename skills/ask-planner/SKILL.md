---
name: ask-planner
description: Runs a planner, adversarial-reviewer, and doc-reviewer mini-orchestration to produce a debated and reviewed vertical-slice plan.
argument-hint: task to decompose into subtasks
disable-model-invocation: true
---

# Plan Mini-Orchestrator

You orchestrate `planner` → adversarial debate → `doc-reviewer`. You do not implement or review the plan yourself.

## Task

$ARGUMENTS

## Actions

1. **Gather project context** (read-only):
   - Run `git status` to understand current state
   - Use `Glob("**/package.json")` and `Glob("**/pyproject.toml")` to detect stack and versions
   - Use `Glob("docs/*.md")` to check for existing PRD, architecture docs, or design specs

2. **Dispatch creator** using the Agent tool:
   - `subagent_type: "dev-team:planner"`
   - Include the full task from `$ARGUMENTS`
   - Include detected project structure, stack, and dependency versions
   - If `docs/prd.md` exists: instruct to "Read docs/prd.md for the product requirements document"
   - If `docs/architecture.md` exists: instruct to "Read docs/architecture.md for the architecture blueprint"
   - Instruct to "Explore at least two decomposition alternatives before committing; decompose by vertical slices with a tracer bullet first."
   - Instruct: "Carry PRD OQ triggers into the slice entries they gate; state the DoD gate (tests + review + demo) between slices; add an integration-enablement slice when the PRD names real external integrations."
   - Include stack-specific phrases matching the detected stack to trigger skill injection
   - Include the report reminder (below)

3. **Initial challenge**: dispatch internal read-only `dev-team:adversarial-reviewer` with `Mode: plan` and `Pass: initial`. It assigns stable `CH-PLAN-*` IDs and may return only `CONSENSUS` or `REVISE`. This pass consumes no debate cycle.
4. **Debate cycles 1–3**: on `REVISE`, re-dispatch planner with every unresolved ID and require `accepted_and_fixed`, `rejected_with_evidence`, or `needs_decision` per ID; then re-dispatch the challenger. Each revision + recheck consumes one cycle. IDs remain stable; rechecks may assign new IDs only for defects introduced by the revision. Cycle 4 is forbidden. Full consensus requires verified fixes, evidence-backed rejections, no `needs_decision`, and mitigation, verification, or explicit acceptance for every residual risk.
5. **Ordinary review or arbitration**:
   - On challenger `CONSENSUS` with no unresolved IDs, dispatch `dev-team:doc-reviewer` for a full plan review. On concerns, re-dispatch planner and then doc-reviewer, maximum 2 ordinary reworks.
   - After an unresolved third recheck, the challenger returns `ARBITRATION_REQUIRED`; dispatch doc-reviewer with the complete plan and ledger to arbitrate all items and perform the full review together. A successful result needs no additional ordinary review.
   - On arbitration `NEEDS_CONTEXT`, ask the user. A non-material answer is applied by planner and verified by doc-reviewer without restarting debate; a change to goals, acceptance criteria, architecture assumptions, slice boundaries, or constraints is material, increments the artifact version, and restarts at the initial pass.
6. **Present the result** only after consensus + successful ordinary review, or successful arbitration/full review. Surface the OQ-IDs gating slice 1 to the user before presenting the plan as final. Keep state in orchestration context; create neither `docs/progress.md` nor a challenge file.

Every dispatch includes the original request, artifact path/version, initial pass or cycle/max, complete stable ledger, dispositions/evidence, verdict, unresolved IDs, related documents, scope, stack/version context, output format, and report reminder.

## Report Reminder (include in agent prompt)

The agent's own prompt mandates the structured report protocol (Status, Files changed, Summary, Evidence, Criteria...). Add this single line to the dispatch:

"Reminder: Status DONE requires the Evidence field with fresh command output (or citations for read-only work); failing checks forbid DONE."

When presenting the result, flag any DONE report lacking Evidence as unverified.
