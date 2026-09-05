---
name: ask-backend
description: "Dispatches the backend-dev agent to implement server-side code: API endpoints, data models, services, and middleware."
argument-hint: task description — API, models, services, middleware
disable-model-invocation: true
---

<!-- codex-entry:start -->
In Codex only: if the dev-team-codex adapter is not already active, load `../dev-team-codex/SKILL.md` relative to this installed skill, preserving this skill's name as the selected entrypoint and the original user task. Let the adapter execute this workflow as a template. If the adapter is already active, bypass this block. In Claude Code, ignore this block and continue with the native workflow below.
<!-- codex-entry:end -->

# Direct Agent Dispatch: backend-dev

You dispatch the **backend-dev** agent directly with the user's task. You do NOT implement anything yourself — you gather context, launch the agent, and present the result.

## Task

$ARGUMENTS

## Actions

1. **Gather project context** (read-only):
   - Run `git status` to understand current state
   - Use `Glob("**/package.json")` and `Glob("**/pyproject.toml")` to detect stack and exact dependency versions
   - Use `Glob("**/tsconfig*.json")` to detect TypeScript config
   - Use `Glob("docs/*.md")` to check for existing PRD or architecture docs

2. **Dispatch agent** using the Agent tool:
   - `subagent_type: "dev-team:backend-dev"`
   - Include the full task from `$ARGUMENTS`
   - Include detected project structure, stack, and **exact dependency versions**
   - If `docs/prd.md` exists: instruct to "Read docs/prd.md for requirements and acceptance criteria"
   - If `docs/architecture.md` exists: instruct to "Read docs/architecture.md for the architecture blueprint"
   - Include stack-specific phrases matching the detected stack to trigger skill injection (e.g., "nestjs", "django", "fastapi", "typescript", "postgresql")
   - Include the report reminder (below)

3. **Present the result** — show the agent's structured report to the user

## Report Reminder (include in agent prompt)

The agent's own prompt mandates the structured report protocol (Status, Files changed, Summary, Evidence, Criteria...). Add this single line to the dispatch:

"Reminder: Status DONE requires the Evidence field with fresh command output (or citations for read-only work); failing checks forbid DONE."

When presenting the result, flag any DONE report lacking Evidence as unverified.
