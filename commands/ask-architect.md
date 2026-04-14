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
   - Instruct to "Apply brainstorming to explore design alternatives. Use writing-plans for structured implementation blueprints."
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
