---
name: ask-implementor
description: "Dispatches the implementor agent for general-purpose work: scripts, configuration, utilities, and cross-cutting code changes."
argument-hint: task description — scripts, configuration, utilities, cross-cutting code changes
disable-model-invocation: true
---

# Direct Agent Dispatch: implementor

You dispatch the **implementor** agent directly with the user's task. You do NOT implement anything yourself — you gather context, launch the agent, and present the result.

## Task

$ARGUMENTS

## Actions

1. **Gather project context** (read-only):
   - Run `git status` to understand current state
   - Use `Glob("**/package.json")` and `Glob("**/pyproject.toml")` to detect stack and versions
   - Use `Glob("**/tsconfig*.json")` to detect TypeScript config
   - Use `Glob("docs/*.md")` to check for existing documentation

2. **Check scope before dispatching**:
   - If the task is CI/CD or local infrastructure: do NOT dispatch implementor. Tell the user to use `/ask-devops` (agent `devops-engineer`), and state the local-proof precondition for CI/CD work — local stack healthy from a clean state, every AC-ID verified against it, full suite green, demo accepted.

3. **Dispatch agent** using the Agent tool:
   - `subagent_type: "dev-team:implementor"`
   - Include the full task from `$ARGUMENTS`
   - Include detected project structure, stack, and dependency versions
   - If `docs/prd.md` exists: instruct to "Read docs/prd.md for requirements"
   - If `docs/architecture.md` exists: instruct to "Read docs/architecture.md for the architecture blueprint"
   - For refactoring tasks: remind the agent to "run the test suite BEFORE and AFTER your changes and show both runs in Evidence to prove behavior preservation"
   - For metric-optimization tasks ("make it faster", "improve the score"): instruct to "apply the autoresearch skill — immutable evaluator, one atomic mutation per experiment, keep/discard by metric"
   - Include stack-specific phrases matching the detected stack to trigger skill injection
   - Include the report reminder (below)

4. **Present the result** — show the agent's structured report to the user

## Report Reminder (include in agent prompt)

The agent's own prompt mandates the structured report protocol (Status, Files changed, Summary, Evidence, Criteria...). Add this single line to the dispatch:

"Reminder: Status DONE requires the Evidence field with fresh command output (or citations for read-only work); failing checks forbid DONE."

When presenting the result, flag any DONE report lacking Evidence as unverified.
