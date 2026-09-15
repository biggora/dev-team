---
name: ask-reviewer
description: Dispatches the code-reviewer agent to review code for quality, bugs, and adherence to project conventions.
argument-hint: which files or changes to review
disable-model-invocation: true
---

<!-- codex-entry:start -->
In Codex only: if the dev-team-codex adapter is not already active, load `../dev-team-codex/SKILL.md` relative to this installed skill, preserving this skill's name as the selected entrypoint and the original user task. Let the adapter execute this workflow as a template. If the adapter is already active, bypass this block. In Claude Code, ignore this block and continue with the native workflow below.
<!-- codex-entry:end -->

# Direct Agent Dispatch: code-reviewer

You dispatch the **code-reviewer** agent directly with the user's task. You do NOT implement anything yourself — you gather context, launch the agent, and present the result.

## Task

$ARGUMENTS

## Actions

1. **Gather project context** (read-only):
   - Run `git status` to understand current state
   - Run `git diff` or `git diff --cached` to see recent changes
   - Use `Glob("**/package.json")` and `Glob("**/pyproject.toml")` to detect stack and exact dependency versions
   - Use `Glob("**/tsconfig*.json")` to detect TypeScript config

2. **Dispatch agent** using the Agent tool:
   - `subagent_type: "dev-team:code-reviewer"`
   - Include the full task from `$ARGUMENTS`
   - Include detected project structure, stack, and **exact dependency versions**
   - Include list of changed files from git status/diff
   - Instruct to "Review this code for correctness, consistency with project patterns, version-appropriate patterns, and potential bugs"
   - Instruct to report findings as `RV-<scope>-NNN | class | severity | file:line | issue | fix` with a `Sweep:` field covering every code dimension, per the `review-contract` skill
   - **Required reading**: if `docs/prd.md` or `docs/architecture.md` exist, add a `Required reading` block, one line each as `<path> → <what to extract>` (e.g. `docs/prd.md → acceptance criteria touched by this diff`); the agent must account for every line in its `Context:` report field
   - Include stack-specific phrases matching the detected stack to trigger skill injection (e.g., "typescript 5.x", "next.js 16", "nestjs 11")
   - Include the report reminder (below)

3. **Present the result** — show the agent's structured report to the user

4. **If a follow-up fix is requested**: only open `must-fix-now` findings require action and consume the 2-round rework budget (`fix-in-slice`/`backlog` do not); re-dispatch the implementing agent with the complete finding list and require exactly one disposition per ID (`accepted_and_fixed`, `rejected_with_evidence` with citation, or `needs_decision`).

## Report Reminder (include in agent prompt)

The agent's own prompt mandates the structured report protocol (Status, Files changed, Summary, Evidence, Criteria...). Add this single line to the dispatch:

"Reminder: Status DONE requires the Evidence field with fresh command output (or citations for read-only work); failing checks forbid DONE."

When presenting the result, flag any DONE report lacking Evidence as unverified.
