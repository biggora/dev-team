---
description: Запустить ui-ux-designer для проектирования интерфейса
argument-hint: Описание интерфейса или пользовательского потока для проектирования
---

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
