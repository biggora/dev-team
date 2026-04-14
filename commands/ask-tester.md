---
description: Запустить tester для написания и запуска тестов
argument-hint: Описание задачи — что тестировать, какие файлы покрыть тестами
---

# Direct Agent Dispatch: tester

You dispatch the **tester** agent directly with the user's task. You do NOT implement anything yourself — you gather context, launch the agent, and present the result.

## Task

$ARGUMENTS

## Actions

1. **Gather project context** (read-only):
   - Run `git status` to understand current state
   - Use `Glob("**/package.json")` and `Glob("**/pyproject.toml")` to detect stack, versions, and test framework
   - Use `Glob("**/tsconfig*.json")` to detect TypeScript config
   - Use `Glob("docs/*.md")` to check for existing PRD, design docs, or test plans
   - Use `Glob("**/*.test.*")` or `Glob("**/*.spec.*")` to detect existing test patterns

2. **Dispatch agent** using the Agent tool:
   - `subagent_type: "dev-team:tester"`
   - Include the full task from `$ARGUMENTS`
   - Include detected project structure, stack, **exact dependency versions**, and test framework
   - If `docs/prd.md` exists: instruct to "Read docs/prd.md for acceptance criteria"
   - If `docs/design.md` exists: instruct to "Read docs/design.md for user flows"
   - Instruct to "Create docs/test-plan.md with traceability matrix before writing tests."
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
