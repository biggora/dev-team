---
name: dev-team-codex
description: >
  In Codex only, run dev-team coordinator workflows and ask-* specialist shortcuts
  through Codex subagents, including dev-team handoff and resume. Use when the user
  asks to work with dev-team or its commands. Not for Claude Code, which uses the
  native workflows, or for ordinary plugin maintenance without a workflow request.
---

# dev-team for Codex

Translate the selected shared workflow into the tools exposed by the current Codex host. This is an execution adapter, not a second workflow definition.

## Enter once, resolve the installed package

1. Check the actual host context. **Only activate this adapter in Codex.** If loaded accidentally in Claude Code, defer to the selected native coordinator or shortcut using Claude's native skill mechanism; do not apply the Codex translation below or request Codex tools.
2. Resolve `PLUGIN_ROOT` from the actual loaded path of this file: two directories above `skills/dev-team-codex/SKILL.md`. Resolve `PROJECT_ROOT` from the user's working project. Never assume the plugin lives in the project or use the current directory to locate plugin templates. If a required template is missing, report `BLOCKED` with its resolved path and the need for a complete plugin installation; do not substitute another installed version.
3. Preserve the original user request and the selected entrypoint. Treat `$ARGUMENTS` in shared templates as that request's task text, without waiting for Claude expansion or passing the literal placeholder to specialists.
4. Mark this invocation **adapter active** in the task context, then read the selected workflow below from the same `PLUGIN_ROOT` as a **template**. Its Codex entry block is bypassed while the adapter is active. Apply this to subsequent workflow transitions too; never invoke the adapter recursively. Clear this marker when the workflow ends.

All plugin paths below are relative to `PLUGIN_ROOT`; project artifacts such as `docs/progress.md`, `docs/handoff.md`, `docs/prd.md`, and `docs/use-cases.md` are relative to `PROJECT_ROOT`. Resolve references relative to the plugin skill that owns them. Read only the selected workflow and resources needed by the current step.

## Select the canonical workflow

Accept an explicit skill invocation, a slash-style compatibility alias, or a natural-language request for the same workflow. These aliases do not register native Codex slash commands. An unqualified request for dev-team selects the universal coordinator, whose stack detection remains authoritative.

| Requested entry | Workflow template |
|---|---|
| dev-team | `skills/dev-team/SKILL.md` |
| dev-team-node | `skills/dev-team-node/SKILL.md` |
| dev-team-python | `skills/dev-team-python/SKILL.md` |
| /ask-prd | `skills/ask-prd/SKILL.md` |
| /ask-architect | `skills/ask-architect/SKILL.md` |
| /ask-planner | `skills/ask-planner/SKILL.md` |
| /ask-designer | `skills/ask-designer/SKILL.md` |
| /ask-frontend | `skills/ask-frontend/SKILL.md` |
| /ask-backend | `skills/ask-backend/SKILL.md` |
| /ask-implementor | `skills/ask-implementor/SKILL.md` |
| /ask-devops | `skills/ask-devops/SKILL.md` |
| /ask-tester | `skills/ask-tester/SKILL.md` |
| /ask-reviewer | `skills/ask-reviewer/SKILL.md` |
| /ask-doc-reviewer | `skills/ask-doc-reviewer/SKILL.md` |
| handoff | `skills/handoff/SKILL.md` |
| resume | `skills/resume/SKILL.md` |

The selected workflow is the source of truth for phases, triage, role selection, state, gates, and retry limits. Preserve its proportional coordinator debate versus the mandatory document gates of `/ask-prd` and `/ask-planner`, including the joint PRD/use-case catalogue review. Do not create a separate gate for `docs/use-cases.md` or a progress ledger where the shortcut forbids one.

Use the canonical Evidence and status rules, including acceptance of recorded **out-of-scope** failures without needless re-dispatch. Required in-scope proof remains mandatory. Keep local-stack requirements, ownership, demo checkpoints, idempotency and circuit-breakers unchanged. On resume, follow the continuity template and authoritative project ledger; retain completed artifacts, run counter, and pending attempts instead of restarting the pipeline.

## Translate tools, not roles

Read the actual tool schema before calling it; names and capabilities vary by host. Translate Claude `Read`, `Glob`, `Grep`, and `Bash` to the available file/search/shell tools without expanding the coordinator's source-reading scope. Translate a Claude `Agent` dispatch as follows:

1. Resolve its `dev-team:<role>` to `PLUGIN_ROOT/agents/<role>.md`. Read that prompt and preserve its body and structured report protocol. Claude frontmatter `model`, `color`, and `tools` is metadata, not Codex call parameters or an enforced permission boundary. Inherit the host's model settings; do not translate Claude model names into Codex overrides.
2. Build a self-contained message with the role instructions, complete user task, `PROJECT_ROOT`, relevant absolute plugin resource paths, allowed writable scope (or **read-only; no writes**), Evidence scope, stack/version facts, input inventory, needed prior outputs, constraints, and the selected workflow's required report reminder. Include applicable decisions and current attempt context. The specialist cannot infer them from coordinator history.
3. Where the advertised schema is the collaboration interface, call:

   ```text
   spawn_agent(task_name="<unique_role_task>", message="<complete dispatch>", fork_turns="none")
   ```

   Use a task name permitted by that schema. Explicit `fork_turns="none"` prevents inheritance of coordinator conversation history; shared filesystem access is separate. A legacy `agent_type` argument is allowed only if the actual schema advertises it and its documented context controls support isolated dispatch. Never guess an agent type or an isolation parameter. If independent delegation, context isolation, or a required lifecycle operation is unavailable, report `BLOCKED` naming the missing capability. Do not replace a required specialist with inline coordinator work.

## Lifecycle and review evidence

- Use `list_agents` and the host's advertised capacity to respect available slots. Dispatch independent, non-overlapping scopes in parallel when capacity permits; otherwise queue them. Capacity pressure does not justify omitting review or reusing a running agent for unrelated work.
- Collect final reports delivered by the host. `wait_agent` waits for mailbox updates; it is not itself a specialist report. Inspect the delivered report and fresh Evidence before advancing a gate. Use supported legacy equivalents only when their actual schema and semantics provide the same operation.
- Use `send_message` for context updates to a running specialist; it does not wake an idle agent. Use `followup_task` for a new attempt by the original specialist, with findings and attempt context; it can wake an idle agent. Count each new work dispatch, including follow-ups, in the existing run counter and scope/role retry budget. A status message or wait is not a new run. Preserve the workflow's limits rather than resetting them with a new agent ID.
- Use `interrupt_agent` when a running task must stop; reconcile completed reports and actual workspace changes before retrying. An interruption is not completion. After session loss, recover from the canonical continuity state; if the old agent is unavailable, dispatch a replacement only for the recorded unfinished attempt, with the reason and counter update.
- Before each read-only review, capture a project file inventory and content hashes, including tracked and untracked files and index/worktree status; compare with the same snapshot after review. Use file metadata/hashing tools without loading source contents into coordinator context. Preserve existing dirty work. Avoid overlapping writers during this check; if unrelated concurrent changes prevent attribution, record that limitation and repeat the review on a stable snapshot before claiming nonmutation. Any unexpected write fails the read-only check and must be reported, not silently reverted. Instructions and snapshots verify behavior; they do not establish an enforced sandbox.

Return the selected workflow's final report with actual Evidence and explicit UNVERIFIED limitations. Do not claim that a prompt template registers a native named Codex agent or that static package checks prove live orchestration.
