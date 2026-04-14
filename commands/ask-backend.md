---
description: Запустить backend-dev для реализации серверной части
argument-hint: Описание задачи — API, модели, сервисы, middleware
---

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
   - Instruct to "Use the superpowers skill framework to discover and apply relevant skills."
   - Include stack-specific phrases matching the detected stack to trigger skill injection (e.g., "nestjs", "django", "fastapi", "typescript", "postgresql")
   - Include the report protocol (below)

3. **Present the result** — show the agent's structured report to the user

## Report Protocol (include in agent prompt)

```
End your response with a structured report:

Status: DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT

Files changed: [list of files created or modified]
Summary: [what was done, key decisions made]
Tests: [tests written or run, and their results]
Concerns: [only if DONE_WITH_CONCERNS — what worries you]
Blocked on: [only if BLOCKED — what prevents completion]
Questions: [only if NEEDS_CONTEXT — what information is needed]
```
