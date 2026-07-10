---
name: ask-prd
description: Dispatches the product-analyst agent to formalize requirements into a PRD with user stories and acceptance criteria.
argument-hint: product or feature to formalize requirements for
disable-model-invocation: true
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
   - Include the report reminder (below)

3. **Present the result** — show the agent's structured report to the user

## Report Reminder (include in agent prompt)

The agent's own prompt mandates the structured report protocol (Status, Files changed, Summary, Evidence, Criteria...). Add this single line to the dispatch:

"Reminder: Status DONE requires the Evidence field with fresh command output (or citations for read-only work); failing checks forbid DONE."

When presenting the result, flag any DONE report lacking Evidence as unverified.
