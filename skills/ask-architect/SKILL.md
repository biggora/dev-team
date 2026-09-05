---
name: ask-architect
description: "Dispatches the architect agent to design system architecture: components, interfaces, data flow, and technical decisions."
argument-hint: system or feature to design
disable-model-invocation: true
---

<!-- codex-entry:start -->
In Codex only: if the dev-team-codex adapter is not already active, load `../dev-team-codex/SKILL.md` relative to this installed skill, preserving this skill's name as the selected entrypoint and the original user task. Let the adapter execute this workflow as a template. If the adapter is already active, bypass this block. In Claude Code, ignore this block and continue with the native workflow below.
<!-- codex-entry:end -->

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
   - Instruct to "Explore at least two architectural alternatives before committing; state why the chosen one wins."
   - Include stack-specific phrases matching the detected stack to trigger skill injection
   - Include the report reminder (below)

3. **Present the result** — show the agent's structured report to the user

## Report Reminder (include in agent prompt)

The agent's own prompt mandates the structured report protocol (Status, Files changed, Summary, Evidence, Criteria...). Add this single line to the dispatch:

"Reminder: Status DONE requires the Evidence field with fresh command output (or citations for read-only work); failing checks forbid DONE."

When presenting the result, flag any DONE report lacking Evidence as unverified.
