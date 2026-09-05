---
name: ask-designer
description: "Dispatches the ui-ux-designer agent to design UI/UX: user flows, screen layouts, and component specifications."
argument-hint: interface or user flow to design
disable-model-invocation: true
---

<!-- codex-entry:start -->
In Codex only: if the dev-team-codex adapter is not already active, load `../dev-team-codex/SKILL.md` relative to this installed skill, preserving this skill's name as the selected entrypoint and the original user task. Let the adapter execute this workflow as a template. If the adapter is already active, bypass this block. In Claude Code, ignore this block and continue with the native workflow below.
<!-- codex-entry:end -->

# Direct Agent Dispatch: ui-ux-designer

You dispatch the **ui-ux-designer** agent directly with the user's task. You do NOT implement anything yourself — you gather context, launch the agent, and present the result.

## Task

$ARGUMENTS

## Actions

1. **Gather project context** (read-only):
   - Run `git status` to understand current state
   - Use `Glob("**/package.json")` to detect frontend stack and versions
   - Use `Glob("docs/*.md")` to check for existing PRD or architecture docs
   - Use `Glob("src/components/**")` or `Glob("app/**")` to understand existing component structure

2. **Dispatch agent** using the Agent tool:
   - `subagent_type: "dev-team:ui-ux-designer"`
   - Include the full task from `$ARGUMENTS`
   - Include detected project structure and frontend stack
   - If `docs/prd.md` exists: instruct to "Read docs/prd.md for the product requirements document"
   - Instruct to "Design the UI for this task. Apply premium frontend design principles, visual design quality, and web design review standards."
   - Instruct to "Include a color palette with hex values and ASCII wireframes for each screen so the design can be reviewed before implementation."
   - Instruct to "Save your design specification to docs/design.md"
   - Include stack-specific phrases matching the detected stack to trigger skill injection
   - Include the report reminder (below)

3. **Present the result** — show the agent's structured report to the user

## Report Reminder (include in agent prompt)

The agent's own prompt mandates the structured report protocol (Status, Files changed, Summary, Evidence, Criteria...). Add this single line to the dispatch:

"Reminder: Status DONE requires the Evidence field with fresh command output (or citations for read-only work); failing checks forbid DONE."

When presenting the result, flag any DONE report lacking Evidence as unverified.
