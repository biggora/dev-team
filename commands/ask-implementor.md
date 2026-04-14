---
description: Запустить implementor для скриптов, конфигов и утилит
argument-hint: Описание задачи — скрипты, конфигурация, CI/CD, утилиты
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
   - Instruct to "Use the superpowers skill framework to discover and apply relevant skills."
   - Include stack-specific phrases matching the detected stack to trigger skill injection
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
