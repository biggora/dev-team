---
name: dev-team-codex
description: >
  This skill should be used when the user asks to use "dev-team", "/dev-team",
  "/dev-team-node", "/dev-team-python", "/ask-backend", "/ask-frontend",
  "/ask-prd", "/ask-planner", "/ask-reviewer", or wants a coordinator that dispatches specialist agents with
  inline quality gates inside Codex.
---

# dev-team for Codex

Use this skill as the Codex-native bridge for the repository's coordinator + specialists architecture.

## What Codex can and cannot do

- Codex plugins bundle `skills`, `apps`, and `mcpServers`.
- Codex plugins do **not** expose Claude-style slash commands.
- Codex plugins do **not** register markdown agents from `agents/` as native named agent types.

Because of that, treat the repository's coordinator skills (`skills/dev-team*/SKILL.md`, `skills/ask-*/SKILL.md`) and `agents/*.md` files as **prompt templates** and execute the workflow with Codex tools.

## Default operating mode

- If the user asked for `dev-team` or a coordinator workflow, act as the lightweight coordinator.
- If the user asked for a direct specialist such as `/ask-backend`, `/ask-frontend`, or `/ask-reviewer`, run the matching specialist flow directly.
- Prefer delegation for substantial work. Use `spawn_agent` with `worker` or `explorer` agents rather than doing all implementation in the root thread.
- Preserve inline gates: code outputs use `code-reviewer`; ordinary documents use `doc-reviewer`; every PRD and plan uses creator → `adversarial-reviewer` debate → `doc-reviewer`.

## File mapping

- Coordinator workflow source: `skills/dev-team/SKILL.md`
- Stack variants: `skills/dev-team-node/SKILL.md`, `skills/dev-team-python/SKILL.md`
- Direct specialist flows: `skills/ask-*/SKILL.md`
- Specialist prompts: `agents/*.md`

Read only the files needed for the current task. Do not bulk-read the whole plugin.

## How to dispatch specialists in Codex

When a repository instruction says to use a named agent such as `dev-team:backend-dev`, adapt it like this:

1. Read the corresponding prompt file from `agents/<name>.md`.
2. Extract the agent instructions and preserve the report protocol.
3. Wrap the prompt as delegated work:

```text
Your task is to perform the following. Follow the instructions below exactly.

<agent-instructions>
[filled contents from agents/<name>.md]
</agent-instructions>

<task-context>
[full user task, scope boundaries, stack/version context, outputs from prior agents]
</task-context>

Execute this now. Output ONLY the structured response following the required report format.
```

4. Spawn a Codex sub-agent with `spawn_agent(agent_type="worker", message=...)`.
5. If the task is exploration-only, prefer `agent_type="explorer"`.

## Coordinator workflow in Codex

For `dev-team` requests:

1. Analyze the task and decide whether multi-agent orchestration is warranted.
2. Detect the stack with lightweight inspection first.
3. Inventory user-provided inputs (briefs, prototypes, mockups, brand assets, existing docs) and pass the path list — or "none" — to document agents; they read the inputs themselves.
4. Choose the relevant specialist prompts from `agents/`.
5. For multi-slice work, maintain `docs/progress.md` (goal, acceptance criterion IDs, task table with evidence summaries, decisions, open questions with triggers) and re-read it plus `docs/prd.md` before each dispatch round.
6. **OQ gate**: before each slice, obtain the user's answers to open questions tagged for that slice (or an explicit "proceed with MVP interpretation") and record them in `docs/progress.md`; an unanswered triggered question blocks the slice.
7. Dispatch independent specialists in parallel when scopes do not overlap. The test directory belongs to the tester — implementation agents must not touch test files.
8. For each PRD or plan, run the mandatory lifecycle below before downstream use. For other documents, run `doc-reviewer` directly.
9. After each code-producing agent, run `code-reviewer`.
10. **Evidence gate**: a specialist report claiming DONE without an `Evidence` field (fresh command output, or file:line citations for read-only work), or with failing output in Evidence, is treated as DONE_WITH_CONCERNS — re-dispatch demanding verification.
11. **DoD gate and demo checkpoint**: do not start the next slice until the current slice's acceptance tests pass, review is DONE, and the user saw a demo of the increment. Deviations require an explicit user decision with a debt-closure slice. Doc-affecting code changes update the owning doc in the same slice (docs-code sync).
12. If a reviewer reports concerns, re-dispatch the original specialist with the findings. Maximum 2 rework dispatches per artifact per gate; after 3 identical failures change strategy once or escalate to the user.
13. Integrate results and report the final outcome succinctly, including which acceptance criteria were verified with evidence.

### Mandatory PRD/plan lifecycle

1. Spawn the creator for a versioned artifact.
2. Spawn internal read-only `adversarial-reviewer` with `Pass: initial`. Use `CH-PRD-*` IDs for PRDs and `CH-PLAN-*` IDs for plans. The initial pass may return only `CONSENSUS` or `REVISE` and consumes no cycle.
3. On `REVISE`, re-spawn the creator with every unresolved ID and require `accepted_and_fixed`, `rejected_with_evidence`, or `needs_decision` per ID, then re-spawn the challenger. Each revision + recheck consumes one of cycles 1–3; IDs remain stable, rechecks may assign new IDs only for defects introduced by the revision, and cycle 4 is forbidden.
4. Challenger `CONSENSUS` requires verified fixes, evidence-backed rejections, no unresolved IDs or `needs_decision`, and mitigation, verification, or explicit acceptance for every residual risk. Then run full ordinary doc-review. On concerns, re-spawn creator and reviewer, maximum 2 ordinary reworks.
5. After an unresolved third recheck, the challenger returns `ARBITRATION_REQUIRED`. Spawn doc-reviewer with the artifact and complete ledger to arbitrate all unresolved IDs and perform the full review together. A successful result needs no additional ordinary review.
6. If arbitration returns `NEEDS_CONTEXT`, ask the user. For a non-material answer, re-spawn creator to update and doc-reviewer to verify without restarting debate. Only a material change to goals, acceptance criteria, architecture assumptions, slice boundaries, or constraints increments the version and restarts the initial pass.
7. Block downstream consumers until consensus + successful ordinary review, or successful arbitration/full review.

Each spawn gets the original request; artifact type/path/version; initial pass or cycle/max; complete mode-specific ledger; dispositions/evidence; verdict; unresolved IDs; related documents/decisions; scope; stack/version context; output format; and evidence reminder. Coordinators store only artifact/version, cycle, verdict, and unresolved IDs in `docs/progress.md`; do not create a challenge file.

## Direct specialist mode

If the user invokes a Claude-style shortcut name, map it directly:

- `/ask-prd` -> run the PRD mini-orchestrator: `product-analyst` → mandatory lifecycle → `doc-reviewer`
- `/ask-architect` -> `agents/architect.md`
- `/ask-planner` -> run the plan mini-orchestrator: `planner` → mandatory lifecycle → `doc-reviewer`
- `/ask-designer` -> `agents/ui-ux-designer.md`
- `/ask-frontend` -> `agents/frontend-dev.md`
- `/ask-backend` -> `agents/backend-dev.md`
- `/ask-implementor` -> `agents/implementor.md`
- `/ask-tester` -> `agents/tester.md`
- `/ask-reviewer` -> `agents/code-reviewer.md`
- `/ask-doc-reviewer` -> `agents/doc-reviewer.md`

The `/ask-prd` and `/ask-planner` mini-orchestrators use the same IDs, dispositions, verdicts, cycle limits, arbitration, material-change restart, payload, and independent ordinary-review rules, but keep state in the task context and create neither `docs/progress.md` nor challenge files.

## Important constraints

- Do not claim that Codex exposes `/dev-team` or `/ask-*` as native slash commands.
- Present them as compatibility aliases that this skill interprets.
- Keep the main thread focused on orchestration, collection, and final reporting.
- Use the repository's report protocol from the selected agent file.
- When the user asks for the Codex adaptation itself, update the Codex-facing files first: this skill, `.codex-plugin/plugin.json`, and Codex sections in `README.md`.
