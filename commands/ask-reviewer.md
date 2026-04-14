---
description: Запустить code-reviewer для ревью кода
argument-hint: Описание задачи — какие файлы или изменения проверить
---

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
   - Include stack-specific phrases matching the detected stack to trigger skill injection (e.g., "typescript 5.x", "next.js 16", "nestjs 11")
   - Include the report protocol (below)

3. **Present the result** — show the agent's structured report to the user

## Report Protocol (include in agent prompt)

```
End your response with a structured report:

Status: DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT

Files changed: N/A (read-only review)
Summary: [what was reviewed, key findings]
Tests: N/A
Concerns: [only if DONE_WITH_CONCERNS — issues found in the code]
Blocked on: [only if BLOCKED — what prevents completion]
Questions: [only if NEEDS_CONTEXT — what information is needed]
```
