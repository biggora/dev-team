---
name: ask-doc-reviewer
description: Dispatches the doc-reviewer agent to review documentation for completeness, clarity, and consistency.
argument-hint: which documents to review
disable-model-invocation: true
---

<!-- codex-entry:start -->
In Codex only: if the dev-team-codex adapter is not already active, load `../dev-team-codex/SKILL.md` relative to this installed skill, preserving this skill's name as the selected entrypoint and the original user task. Let the adapter execute this workflow as a template. If the adapter is already active, bypass this block. In Claude Code, ignore this block and continue with the native workflow below.
<!-- codex-entry:end -->

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
   - Instruct to report findings as `RV-<scope>-NNN | class | severity | doc§section | issue | fix` with a `Sweep:` field covering every document dimension, per the `review-contract` skill
   - **Required reading**: build a `Required reading` block from the discovered docs, one line each as `<path> → <what to extract>` (e.g. `docs/prd.md → AC-IDs this review scope covers`); the agent must account for every line in its `Context:` report field
   - Include the report reminder (below)

3. **Present the result** — show the agent's structured report to the user

4. **If a follow-up fix is requested**: only open `must-fix-now` findings require action and consume the 2-round rework budget (`fix-in-slice`/`backlog` do not); re-dispatch the document's author with the complete finding list and require exactly one disposition per ID (`accepted_and_fixed`, `rejected_with_evidence` with citation, or `needs_decision`).

## Report Reminder (include in agent prompt)

The agent's own prompt mandates the structured report protocol (Status, Files changed, Summary, Evidence, Criteria...). Add this single line to the dispatch:

"Reminder: Status DONE requires the Evidence field with fresh command output (or citations for read-only work); failing checks forbid DONE."

When presenting the result, flag any DONE report lacking Evidence as unverified.
