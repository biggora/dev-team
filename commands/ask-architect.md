---
description: Запустить architect для проектирования архитектуры
argument-hint: Описание системы или фичи для проектирования
---

# Direct Agent Dispatch: architect

You dispatch the **architect** agent directly with the user's task. You do NOT implement anything yourself — you gather context, launch the agent, and present the result.

## Task

$ARGUMENTS

## Actions

1. **Gather project context** (read-only):
   - Run `git status` to understand current state
   - Use `Glob("**/package.json")` and `Glob("**/pyproject.toml")` to detect stack and versions
   - Use `Glob("docs/*.md")` to check for existing PRD or documentation
   - Use `Glob("**/tsconfig*.json")` to detect TypeScript config

2. **Dispatch agent** using the Agent tool:
   - `subagent_type: "dev-team:architect"`
   - Include the full task from `$ARGUMENTS`
   - Include detected project structure, stack, and dependency versions
   - If `docs/prd.md` exists: instruct to "Read docs/prd.md for the product requirements document"
   - Instruct to "Read references/architecture-patterns.md for architecture patterns"
   - Instruct to "Explore at least two architectural alternatives before committing; state why the chosen one wins."
   - Include stack-specific phrases matching the detected stack to trigger skill injection
   - Include the report reminder (below)

3. **Present the result** — show the agent's structured report to the user

## Report Reminder (include in agent prompt)

The agent's own prompt mandates the structured report protocol (Status, Files changed, Summary, Evidence, Criteria...). Add this single line to the dispatch:

"Reminder: Status DONE requires the Evidence field with fresh command output (or citations for read-only work); failing checks forbid DONE."

When presenting the result, flag any DONE report lacking Evidence as unverified.
