# dev-team

Claude Code plugin with a "coordinator + specialists" architecture. The coordinator (`/dev-team`) decomposes tasks and dispatches specialist agents with isolated contexts. Skills are injected dynamically based on file patterns, not loaded globally.

## Installation

```bash
# From local directory:
claude plugins add /path/to/dev-team

# From git repository:
claude plugins add https://github.com/biggora/dev-team
```

## Usage

```bash
# Universal coordinator (auto-detects stack):
/dev-team Implement authentication system with JWT and OAuth2

# Stack-specific coordinators:
/dev-team-node Add API endpoint with NestJS controller and service
/dev-team-python Create Django model with DRF serializer and viewset

# The coordinator automatically:
# 1. Analyzes the task and determines needed specialists
# 2. Decomposes into subtasks with scope boundaries
# 3. Dispatches agents (parallel when independent)
# 4. Collects results and handles BLOCKED/NEEDS_CONTEXT
# 5. Sends for code review (optional)
# 6. Reports summary to user
```

## Architecture

```
Coordinators
├── /dev-team              Universal (auto-detect stack)
├── /dev-team-node         Node.js / TypeScript
└── /dev-team-python       Python
    |
    +-- implementor        Writes code (green, full tools)
    +-- tester             Writes & runs tests (yellow, full tools)
    +-- code-reviewer      Reviews code (red, read-only)
```

**Context isolation**: each agent gets a clean context and does not inherit the coordinator's session. The coordinator includes the full task description, scope boundaries, and report protocol in every dispatch.

**Dynamic skill injection**: skills are injected into agents based on file patterns (`pathPatterns`), command patterns (`bashPatterns`), import detection (`importPatterns`), and prompt signals (`promptSignals`) — not loaded globally.

## Plugin Structure

```
dev-team/
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest
├── commands/
│   ├── dev-team.md              # Universal coordinator (auto-detect)
│   ├── dev-team-node.md         # Node.js coordinator
│   └── dev-team-python.md       # Python coordinator
├── agents/
│   ├── _template.md             # Template for creating new agents
│   ├── implementor.md           # Code writer (green, full tools)
│   ├── tester.md                # Test writer & runner (yellow, full tools)
│   └── code-reviewer.md         # Read-only reviewer (red)
├── skills/
│   ├── nodejs-stack/
│   │   └── SKILL.md             # Node.js/TS patterns & conventions
│   ├── python-stack/
│   │   └── SKILL.md             # Python patterns & conventions
│   └── _template/
│       ├── SKILL.md             # Skill template with metadata example
│       └── references/
│           └── _template.md     # Reference file template
├── CLAUDE.md                    # Plugin instructions
└── specs/
    └── dev-team-architecture.md # Architecture specification
```

## Coordinator Workflow

| Phase | Goal | Details |
|-------|------|---------|
| 1. Analysis | Understand the task | Determine specialists, decompose into subtasks |
| 2. Dispatch | Launch agents | Full context, scope boundaries, report protocol |
| 3. Collection | Process results | Handle DONE / BLOCKED / NEEDS_CONTEXT statuses |
| 4. Review | Code review | Dispatch code-reviewer (optional) |
| 5. Report | Summary | Files changed, tests, concerns, next steps |

## Report Protocol

Every agent ends with a structured report:

```
Status: DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT

Files changed: [list]
Summary: [what was done]
Tests: [tests and results]
Concerns: [if DONE_WITH_CONCERNS]
Blocked on: [if BLOCKED]
Questions: [if NEEDS_CONTEXT]
```

## Adding a New Agent

1. Copy `agents/_template.md` to `agents/<agent-name>.md`
2. Fill in frontmatter: `name`, `description` (with `<example>` blocks), `model`, `color`, `tools`
3. Write the system prompt with role, responsibilities, process, and output format
4. Include the report protocol at the end
5. Restart Claude Code — the agent is auto-discovered

**Role-based tool presets:**

| Role | Tools |
|------|-------|
| Implementor | Read, Write, Edit, Grep, Glob, Bash |
| Reviewer | Read, Grep, Glob |
| Planner | Read, Grep, Glob |
| Tester | Read, Write, Edit, Grep, Glob, Bash |
| Researcher | Read, Grep, Glob, WebSearch, WebFetch |

## Adding a New Skill

1. Copy `skills/_template/` to `skills/<skill-name>/`
2. Edit `SKILL.md`: set `name`, `description`, `metadata` (pathPatterns, promptSignals)
3. Write skill content (keep under 2000 words)
4. Put detailed documentation in `references/`
5. Restart Claude Code — the skill is auto-discovered

## Adding a New Stack

To add support for a new technology stack (e.g., Go, Rust, Java):

1. Create `commands/dev-team-<stack>.md` — copy from an existing stack coordinator, adapt detection patterns and stack-specific instructions
2. Create `skills/<stack>-stack/SKILL.md` — add `pathPatterns`, `importPatterns`, `promptSignals` for the stack's file types
3. Optionally add `references/` with framework-specific patterns
4. Update `commands/dev-team.md` to list the new stack coordinator

## Verification

| Check | How | Expected |
|-------|-----|----------|
| Plugin installed | Type `/dev-team` | Command available |
| Stack commands | Type `/dev-team-node` or `/dev-team-python` | Stack coordinators available |
| Agents available | Claude suggests agents | implementor, tester, code-reviewer in list |
| Tools isolation | Dispatch code-reviewer | Write/Edit unavailable |
| Skill injection | Agent reads `.ts` file | nodejs-stack skill injected |
| Coordinator isolation | `/dev-team` doesn't see skills | Clean coordinator context |

For debugging: `claude --debug` shows skill injection and hook activity.

## License

MIT
