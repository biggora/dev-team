---
name: ask-frontend
description: "Dispatches the frontend-dev agent to build UI: components, pages, forms, styles, and client-side logic."
argument-hint: UI task — components, pages, styles
disable-model-invocation: true
---

<!-- codex-entry:start -->
In Codex only: if the dev-team-codex adapter is not already active, load `../dev-team-codex/SKILL.md` relative to this installed skill, preserving this skill's name as the selected entrypoint and the original user task. Let the adapter execute this workflow as a template. If the adapter is already active, bypass this block. In Claude Code, ignore this block and continue with the native workflow below.
<!-- codex-entry:end -->

# Direct Agent Dispatch: frontend-dev

You dispatch the **frontend-dev** agent directly with the user's task. You do NOT implement anything yourself — you gather context, launch the agent, and present the result.

## Task

$ARGUMENTS

## Actions

1. **Gather project context** (read-only):
   - Run `git status` to understand current state
   - Use `Glob("**/package.json")` to detect frontend stack and exact dependency versions
   - Use `Glob("**/tsconfig*.json")` to detect TypeScript config
   - Use `Glob("docs/*.md")` to check for existing PRD, architecture, or design docs

2. **Dispatch agent** using the Agent tool:
   - `subagent_type: "dev-team:frontend-dev"`
   - Include the full task from `$ARGUMENTS`
   - Include detected project structure, stack, and **exact dependency versions** from package.json
   - If `docs/prd.md` exists: instruct to "Read docs/prd.md for requirements and acceptance criteria"
   - If `docs/design.md` exists: instruct to "Read docs/design.md for the design specification (color palette, wireframes, user flows)"
   - If `docs/architecture.md` exists: instruct to "Read docs/architecture.md for the architecture blueprint"
   - Include stack-specific phrases matching the detected stack to trigger skill injection (e.g., "next.js", "react", "tailwindcss", "typescript")
   - Remind the agent to "run build, lint, and tests before reporting, and browser-verify the primary user flow when a dev server can be started"
   - Include the report reminder (below)

3. **Present the result** — show the agent's structured report to the user

## Report Reminder (include in agent prompt)

The agent's own prompt mandates the structured report protocol (Status, Files changed, Summary, Evidence, Criteria...). Add this single line to the dispatch:

"Reminder: Status DONE requires the Evidence field with fresh command output (or citations for read-only work); failing checks forbid DONE."

When presenting the result, flag any DONE report lacking Evidence as unverified.
