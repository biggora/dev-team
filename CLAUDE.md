# dev-team Plugin

## Architecture

This plugin implements a "coordinator + specialists" architecture:

- `/dev-team` — universal coordinator that auto-detects the stack
- `/dev-team-node` — Node.js/TypeScript coordinator (Next.js, NestJS, Vite, Express)
- `/dev-team-python` — Python coordinator (Django, Flask, FastAPI)
- Specialist agents operate with isolated contexts — they do not inherit the coordinator's session
- Skills are injected dynamically based on file patterns, not loaded globally
- The coordinator does NOT read project source files — only git status, Glob, and Grep for structure analysis

## Available Agents

| Agent | Role | Tools | Color |
|-------|------|-------|-------|
| implementor | Writes and modifies code | Read, Write, Edit, Grep, Glob, Bash | green |
| code-reviewer | Reviews code (read-only) | Read, Grep, Glob | red |
| tester | Writes and runs tests | Read, Write, Edit, Grep, Glob, Bash | yellow |

## Report Protocol

Every agent MUST end its response with a structured report:

```
Status: DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT

Files changed: [list of files created or modified]
Summary: [what was done, key decisions made]
Tests: [tests written or run, and their results]
Concerns: [only if DONE_WITH_CONCERNS — what worries you]
Blocked on: [only if BLOCKED — what prevents completion]
Questions: [only if NEEDS_CONTEXT — what information is needed]
```

**Status handling by coordinator:**

| Status | Coordinator Action |
|--------|-------------------|
| DONE | Proceed to next phase |
| DONE_WITH_CONCERNS | Evaluate concerns, decide if action needed |
| BLOCKED | Provide missing info, re-dispatch agent |
| NEEDS_CONTEXT | Answer questions or ask user, re-dispatch |

## Dispatch Rules (for coordinator)

- Include the **full task description** — agents cannot see coordinator context
- Specify **scope boundaries** — which files/directories can be changed
- Include **context** about what other agents have done
- Always include the **report protocol template** in the agent prompt
- Independent tasks → **multiple Agent tool calls in one message** (parallel dispatch)

## Agent Guidelines

- Work only within your specified scope boundaries
- Follow the coding conventions of the project you are working in
- Always end with the structured report
- If blocked, report `BLOCKED` with clear description rather than guessing
- If missing context, report `NEEDS_CONTEXT` with specific questions

## Adding New Agents

1. Copy `agents/_template.md` to `agents/<agent-name>.md`
2. Fill in frontmatter: name, description (with `<example>` blocks), model, color, tools
3. Write the system prompt: role, responsibilities, process, output format
4. Include the report protocol at the end of the system prompt
5. Restart Claude Code — agent is auto-discovered

## Adding New Skills

1. Copy `skills/_template/` directory to `skills/<skill-name>/`
2. Edit `SKILL.md`: set name, description, metadata (pathPatterns, promptSignals)
3. Write skill content (keep under 2000 words)
4. Put detailed docs in `references/` subdirectory
5. Restart Claude Code — skill is auto-discovered
