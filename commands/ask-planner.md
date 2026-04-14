---
description: Запустить planner для декомпозиции задачи и создания плана
argument-hint: Описание задачи для декомпозиции на подзадачи
---

# Direct Agent Dispatch: planner

You dispatch the **planner** agent directly with the user's task. You do NOT implement anything yourself — you gather context, launch the agent, and present the result.

## Task

$ARGUMENTS

## Actions

1. **Gather project context** (read-only):
   - Run `git status` to understand current state
   - Use `Glob("**/package.json")` and `Glob("**/pyproject.toml")` to detect stack and versions
   - Use `Glob("docs/*.md")` to check for existing PRD, architecture docs, or design specs

2. **Dispatch agent** using the Agent tool:
   - `subagent_type: "dev-team:planner"`
   - Include the full task from `$ARGUMENTS`
   - Include detected project structure, stack, and dependency versions
   - If `docs/prd.md` exists: instruct to "Read docs/prd.md for the product requirements document"
   - If `docs/architecture.md` exists: instruct to "Read docs/architecture.md for the architecture blueprint"
   - Instruct to "Apply brainstorming before decomposition. Use writing-plans for structured execution plans."
   - Include stack-specific phrases matching the detected stack to trigger skill injection
   - Include the report protocol (below)

3. **Present the result** — show the agent's structured report to the user

## Report Protocol (include in agent prompt)

```
End your response with a structured report:

Status: DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT

Files changed: [list of files created or modified]
Summary: [what was done, key decisions made]
Tests: N/A
Concerns: [only if DONE_WITH_CONCERNS — what worries you]
Blocked on: [only if BLOCKED — what prevents completion]
Questions: [only if NEEDS_CONTEXT — what information is needed]
```
