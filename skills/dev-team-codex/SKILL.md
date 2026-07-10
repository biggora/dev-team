---
name: dev-team-codex
description: >
  This skill should be used when the user asks to use "dev-team", "/dev-team",
  "/dev-team-node", "/dev-team-python", "/ask-backend", "/ask-frontend",
  "/ask-reviewer", or wants a coordinator that dispatches specialist agents with
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
- Preserve the repository's inline review pattern: code outputs should be reviewed by `code-reviewer`; document outputs should be reviewed by `doc-reviewer`.

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
3. Choose the relevant specialist prompts from `agents/`.
4. For multi-slice work, maintain `docs/progress.md` (goal, acceptance criterion IDs, task table with evidence summaries, decisions) and re-read it plus `docs/prd.md` before each dispatch round.
5. Dispatch independent specialists in parallel when scopes do not overlap. The test directory belongs to the tester — implementation agents must not touch test files.
6. After each document-producing agent, run `doc-reviewer`.
7. After each code-producing agent, run `code-reviewer`.
8. **Evidence gate**: a specialist report claiming DONE without an `Evidence` field (fresh command output, or file:line citations for read-only work), or with failing output in Evidence, is treated as DONE_WITH_CONCERNS — re-dispatch demanding verification.
9. If a reviewer reports concerns, re-dispatch the original specialist with the findings. Maximum 2 rework dispatches per artifact per gate; after 3 identical failures change strategy once or escalate to the user.
10. Integrate results and report the final outcome succinctly, including which acceptance criteria were verified with evidence.

## Direct specialist mode

If the user invokes a Claude-style shortcut name, map it directly:

- `/ask-prd` -> `agents/product-analyst.md`
- `/ask-architect` -> `agents/architect.md`
- `/ask-planner` -> `agents/planner.md`
- `/ask-designer` -> `agents/ui-ux-designer.md`
- `/ask-frontend` -> `agents/frontend-dev.md`
- `/ask-backend` -> `agents/backend-dev.md`
- `/ask-implementor` -> `agents/implementor.md`
- `/ask-tester` -> `agents/tester.md`
- `/ask-reviewer` -> `agents/code-reviewer.md`
- `/ask-doc-reviewer` -> `agents/doc-reviewer.md`

## Important constraints

- Do not claim that Codex exposes `/dev-team` or `/ask-*` as native slash commands.
- Present them as compatibility aliases that this skill interprets.
- Keep the main thread focused on orchestration, collection, and final reporting.
- Use the repository's report protocol from the selected agent file.
- When the user asks for the Codex adaptation itself, update the Codex-facing files first: this skill, `.codex-plugin/plugin.json`, and Codex sections in `README.md`.
