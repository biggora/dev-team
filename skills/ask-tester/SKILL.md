---
name: ask-tester
description: "Dispatches the tester agent to write and run tests: unit, integration, and end-to-end."
argument-hint: what to test and which files to cover
disable-model-invocation: true
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
   - **State the mode**: Mode A ("derive failing acceptance tests from the PRD criteria before implementation — expected-red") when tests are wanted ahead of code; Mode B ("run the full suite, extend coverage, update docs/test-plan.md") when verifying existing code. Default to Mode B
   - Include stack-specific phrases matching the detected stack to trigger skill injection
   - Include the report reminder (below)

3. **Present the result** — show the agent's structured report to the user

## Report Reminder (include in agent prompt)

The agent's own prompt mandates the structured report protocol (Status, Files changed, Summary, Evidence, Criteria...). Add this single line to the dispatch:

"Reminder: Status DONE requires the Evidence field with fresh command output (or citations for read-only work); failing checks forbid DONE."

When presenting the result, flag any DONE report lacking Evidence as unverified.
