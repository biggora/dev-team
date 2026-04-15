# dev-team Plugin

## Architecture

This plugin implements a "coordinator + specialists" architecture with inline quality gates:

- `/dev-team` — universal coordinator that auto-detects the stack
- `/dev-team-node` — Node.js/TypeScript coordinator (Next.js, NestJS, Vite, Express)
- `/dev-team-python` — Python coordinator (Django, Flask, FastAPI)
- Specialist agents operate with isolated contexts — they do not inherit the coordinator's session
- Skills are injected dynamically based on file patterns, not loaded globally
- The coordinator does NOT read project source files — only git status, Glob, and Grep for structure analysis
- **Every artifact is reviewed inline**: doc-reviewer after each document, code-reviewer after each code agent
- **Review-and-rework pattern**: if reviewer finds concerns → original agent is re-dispatched with findings (max 1 rework to prevent loops)

## Available Agents

| Agent | Role | Tools | Model | Color |
|-------|------|-------|-------|-------|
| product-analyst | Formalizes requirements into PRD | Read, Write, Grep, Glob | opus | cyan |
| architect | Designs system architecture and blueprints | Read, Write, Grep, Glob | opus | blue |
| planner | Decomposes tasks, creates execution plans | Read, Write, Grep, Glob | opus | cyan |
| ui-ux-designer | Designs UI/UX: flows, layouts, specs | Read, Write, Grep, Glob | sonnet | magenta |
| frontend-dev | Builds UI: components, pages, styles, a11y | Read, Write, Edit, Grep, Glob, Bash | sonnet | magenta |
| backend-dev | Builds API: endpoints, models, services, auth | Read, Write, Edit, Grep, Glob, Bash | sonnet | green |
| implementor | General fallback: scripts, config, utilities | Read, Write, Edit, Grep, Glob, Bash | sonnet | green |
| tester | Writes and runs tests | Read, Write, Edit, Grep, Glob, Bash | sonnet | yellow |
| code-reviewer | Reviews code for quality and bugs | Read, Grep, Glob | sonnet | red |
| doc-reviewer | Reviews documentation for quality and completeness | Read, Grep, Glob | sonnet | cyan |

## Shortcut Commands (Direct Agent Dispatch)

Use `ask-*` commands to dispatch a specific agent directly, bypassing the coordinator:

| Command | Agent | Use case |
|---------|-------|----------|
| `/ask-prd` | product-analyst | Create PRD, formalize requirements |
| `/ask-architect` | architect | Design system architecture |
| `/ask-planner` | planner | Decompose task into subtasks |
| `/ask-designer` | ui-ux-designer | Design UI/UX flows and layouts |
| `/ask-frontend` | frontend-dev | Build UI components, pages, styles |
| `/ask-backend` | backend-dev | Build API, models, services |
| `/ask-implementor` | implementor | Scripts, config, CI/CD, utilities |
| `/ask-tester` | tester | Write and run tests |
| `/ask-reviewer` | code-reviewer | Review code for quality and bugs |
| `/ask-doc-reviewer` | doc-reviewer | Review documentation quality |

**When to use shortcuts vs coordinator:**
- `/ask-*` — single-agent tasks with clear scope (e.g., "write a PRD", "review this code")
- `/dev-team` — complex tasks requiring multiple agents, decomposition, and coordination

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
| DONE_WITH_CONCERNS | Re-dispatch original agent with findings to fix (max 1 rework) |
| BLOCKED | Provide missing info, re-dispatch agent (max 2 attempts) |
| NEEDS_CONTEXT | Answer questions or ask user, re-dispatch |

## Inline Review Workflow

Every artifact produced in Phase 2 goes through an inline review gate before the next agent consumes it:

| Artifact | Creator | Reviewer | On concerns |
|----------|---------|----------|-------------|
| PRD | product-analyst | doc-reviewer | Re-dispatch product-analyst |
| Architecture | architect | doc-reviewer | Re-dispatch architect |
| Design spec | ui-ux-designer | doc-reviewer | Re-dispatch ui-ux-designer |
| Execution plan | planner | doc-reviewer | Re-dispatch planner |
| Scaffold code | implementor | code-reviewer | Re-dispatch implementor |
| Backend code | backend-dev | code-reviewer | Re-dispatch backend-dev |
| Frontend code | frontend-dev | code-reviewer | Re-dispatch frontend-dev |
| Test code | tester | code-reviewer | Re-dispatch tester |

Phase 4 performs a final cross-cutting review (code-reviewer for cross-module consistency + doc-reviewer for cross-document consistency) only when multiple agents were dispatched.

See `specs/workflow.md` for full mermaid diagrams.

## Dispatch Rules (for coordinator)

- Include the **full task description** — agents cannot see coordinator context
- Specify **scope boundaries** — which files/directories can be changed
- Include **context** about what other agents have done
- Always include the **report protocol template** in the agent prompt
- Independent tasks → **multiple Agent tool calls in one message** (parallel dispatch)
- Include **stack-specific phrases** in prompts (e.g., "typescript", "nestjs", "django") to trigger skill injection via promptSignals — critical for greenfield projects where no files exist yet
- For architect on greenfield: explicitly instruct to "Read references/architecture-patterns.md"

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
