---
name: ask-devops
description: "Dispatches the devops-engineer agent for local containerized infrastructure — docker-compose, dev Dockerfile, service emulators, seed data — and for CI/CD once the local-proof gate has passed."
argument-hint: infrastructure task — docker-compose services, emulators, seed data, or CI/CD (local proof must be green first)
disable-model-invocation: true
---

<!-- codex-entry:start -->
In Codex only: if the dev-team-codex adapter is not already active, load `../dev-team-codex/SKILL.md` relative to this installed skill, preserving this skill's name as the selected entrypoint and the original user task. Let the adapter execute this workflow as a template. If the adapter is already active, bypass this block. In Claude Code, ignore this block and continue with the native workflow below.
<!-- codex-entry:end -->

# Direct Agent Dispatch: devops-engineer

You dispatch the **devops-engineer** agent directly with the user's task. You do NOT write any compose, Dockerfile, or pipeline yourself — you gather context, launch the agent, and present the result.

## Task

$ARGUMENTS

## Actions

1. **Gather project context** (read-only):
   - Run `git status` to understand current state
   - Use `Glob("**/docker-compose*.y*ml")` and `Glob("**/Dockerfile*")` to detect an existing stack
   - Use `Glob("**/.env*")` to detect existing environment templates
   - Use `Glob("**/package.json")` and `Glob("**/pyproject.toml")` to detect stack and exact versions
   - Use `Glob("docs/*.md")` to check for architecture, progress ledger, and PRD
   - If a compose file exists, run `docker compose ps` and pass the current stack state to the agent

2. **Dispatch agent** using the Agent tool:
   - `subagent_type: "dev-team:devops-engineer"`
   - Include the full task from `$ARGUMENTS`
   - Include the detected stack, **exact dependency versions**, and the services already defined in the existing compose file (or "none")
   - If `docs/architecture.md` exists: instruct to "Read docs/architecture.md, section 'Local runtime topology'"
   - If `docs/progress.md` exists: instruct to "Read the infrastructure inventory and local-stack proof rows in docs/progress.md"
   - **For CI/CD tasks**: instruct to "First confirm the local-proof gate in docs/progress.md: local stack healthy from clean, every AC-ID verified against it, full suite (unit + integration + e2e) green, demo accepted. If any is missing, report BLOCKED naming the missing evidence instead of writing the pipeline."
   - **Required reading**: turn the sources above into a `Required reading` block, one line each as `<path> → <what to extract>` (e.g. `docs/architecture.md → Local runtime topology`, `docs/progress.md → infrastructure inventory`); the agent must account for every line in its `Context:` report field (`review-contract` skill).
   - Include the phrases `docker compose`, `containerized dependencies`, `local stack`, and `health check` so the `local-stack` skill is surfaced
   - Include the report reminder (below)

3. **Present the result** — show the agent's structured report to the user. Flag any DONE whose Evidence lacks the clean-state sequence `docker compose down -v` → `docker compose up -d --wait` → `docker compose ps` with every service healthy as unverified.

4. **If a follow-up fix is requested**: findings and rework follow the `review-contract` skill — `RV-<scope>-NNN` IDs with class `must-fix-now` (blocks, consumes the 2-round rework budget), `fix-in-slice`, or `backlog`; re-dispatch with the complete finding list and require exactly one disposition per ID (`accepted_and_fixed`, `rejected_with_evidence` with citation, or `needs_decision`).

## Report Reminder (include in agent prompt)

The agent's own prompt mandates the structured report protocol (Status, Files changed, Summary, Evidence, Criteria...). Add this single line to the dispatch:

"Reminder: Status DONE requires the Evidence field with fresh command output (or citations for read-only work); failing checks forbid DONE."

When presenting the result, flag any DONE report lacking Evidence as unverified.
