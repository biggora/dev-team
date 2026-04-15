---
description: Запустить doc-reviewer для ревью документации
argument-hint: Описание задачи — какие документы проверить
---

# Direct Agent Dispatch: doc-reviewer

You dispatch the **doc-reviewer** agent directly with the user's task. You do NOT implement anything yourself — you gather context, launch the agent, and present the result.

## Task

$ARGUMENTS

## Actions

1. **Gather project context** (read-only):
   - Use `Glob("docs/*.md")` to find all project documentation
   - Use `Glob("docs/**/*.md")` to find nested documentation
   - Run `git status` to understand current state

2. **Dispatch agent** using the Agent tool:
   - `subagent_type: "dev-team:doc-reviewer"`
   - Include the full task from `$ARGUMENTS`
   - Include list of discovered documentation files
   - Instruct to "Review the specified documentation for completeness, clarity, consistency, actionability, and technical accuracy"
   - If multiple docs exist, instruct to "Check cross-document consistency between all docs/ files"
   - Include the report protocol (below)

3. **Present the result** — show the agent's structured report to the user

## Report Protocol (include in agent prompt)

```
End your response with a structured report:

Status: DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT

Files changed: N/A (read-only review)
Summary: [what was reviewed, key findings]
Tests: N/A
Concerns: [only if DONE_WITH_CONCERNS — issues found in the documentation]
Blocked on: [only if BLOCKED — what prevents completion]
Questions: [only if NEEDS_CONTEXT — what information is needed]
```
