---
description: Запустить product-analyst для создания PRD
argument-hint: Описание продукта или фичи для формализации требований
---

# Direct Agent Dispatch: product-analyst

You dispatch the **product-analyst** agent directly with the user's task. You do NOT implement anything yourself — you gather context, launch the agent, and present the result.

## Task

$ARGUMENTS

## Actions

1. **Gather project context** (read-only):
   - Run `git status` to understand current state
   - Use `Glob("**/package.json")` and `Glob("**/pyproject.toml")` to detect stack
   - Use `Glob("docs/*.md")` to check for existing documentation

2. **Dispatch agent** using the Agent tool:
   - `subagent_type: "dev-team:product-analyst"`
   - Include the full task from `$ARGUMENTS`
   - Include detected project structure and stack
   - If existing project: instruct to "Read the codebase to understand current state and derive requirements"
   - Instruct to "Formalize the requirements into a PRD. Save to docs/prd.md"
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
