---
name: ask-doc-reviewer
description: Dispatches the doc-reviewer agent to review documentation for completeness, clarity, and consistency.
argument-hint: which documents to review
disable-model-invocation: true
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
   - Include the report reminder (below)

3. **Present the result** — show the agent's structured report to the user

## Report Reminder (include in agent prompt)

The agent's own prompt mandates the structured report protocol (Status, Files changed, Summary, Evidence, Criteria...). Add this single line to the dispatch:

"Reminder: Status DONE requires the Evidence field with fresh command output (or citations for read-only work); failing checks forbid DONE."

When presenting the result, flag any DONE report lacking Evidence as unverified.
