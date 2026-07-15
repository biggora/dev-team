---
name: ask-implementor
description: "Dispatches the implementor agent for general-purpose work: scripts, configuration, utilities, and CI/CD (only after local verification is green)."
argument-hint: task description — scripts, configuration, utilities, CI/CD (local checks must be green first)
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

2. **Dispatch agent** using the Agent tool:
   - `subagent_type: "dev-team:implementor"`
   - Include the full task from `$ARGUMENTS`
   - Include detected project structure, stack, and dependency versions
   - If `docs/prd.md` exists: instruct to "Read docs/prd.md for requirements"
   - If `docs/architecture.md` exists: instruct to "Read docs/architecture.md for the architecture blueprint"
   - For refactoring tasks: remind the agent to "run the test suite BEFORE and AFTER your changes and show both runs in Evidence to prove behavior preservation"
   - For CI/CD tasks (pipelines, deployment configs, publish/release): instruct the agent to "First run the project's local proving commands (build, lint, test) yourself. If any is red, report BLOCKED with the failing output instead of writing the pipeline — CI/CD comes only after the application is proven working locally. The pipeline must encode only checks proven green locally; show both the local green run and the pipeline config in Evidence"
   - For metric-optimization tasks ("make it faster", "improve the score"): instruct to "apply the autoresearch skill — immutable evaluator, one atomic mutation per experiment, keep/discard by metric"
   - Include stack-specific phrases matching the detected stack to trigger skill injection
   - Include the report reminder (below)

3. **Present the result** — show the agent's structured report to the user

## Report Reminder (include in agent prompt)

The agent's own prompt mandates the structured report protocol (Status, Files changed, Summary, Evidence, Criteria...). Add this single line to the dispatch:

"Reminder: Status DONE requires the Evidence field with fresh command output (or citations for read-only work); failing checks forbid DONE."

When presenting the result, flag any DONE report lacking Evidence as unverified.
