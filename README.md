# dev-team

Claude Code plugin that orchestrates a team of specialized AI agents for full-cycle software development — from requirements to tested, reviewed code.

The coordinator (`/dev-team`) decomposes tasks, dispatches specialist agents with isolated contexts, and enforces inline quality gates: every document is reviewed by `doc-reviewer`, every piece of code is reviewed by `code-reviewer`, and artifacts with concerns are automatically sent back for rework (max 1 rework cycle to prevent loops).

Skills are injected dynamically based on file patterns, not loaded globally. This repository also includes Codex plugin metadata.

## Installation

### In Codex

This repository now includes the standard Codex plugin manifest at `.codex-plugin/plugin.json` and a repo-local marketplace entry at `.agents/plugins/marketplace.json`.

If you use this repository as a local Codex plugin source, Codex can discover `dev-team` directly from the repo.

### From GitHub (recommended)

```bash
# Step 1: Add marketplace
/plugin marketplace add biggora/dev-team
# or
/plugin marketplace add https://github.com/biggora/dev-team

# Step 2: Install (globally by default)
/plugin install dev-team@dev-team

# OR install per-project (shared with team via .claude/settings.json)
/plugin install dev-team@dev-team --scope project
```

### From local directory

```bash
# Step 1: Add local marketplace
/plugin marketplace add /path/to/dev-team

# Step 2: Install (globally by default)
/plugin install dev-team@dev-team

# OR install per-project
/plugin install dev-team@dev-team --scope project
```

### Development mode (session only)

```bash
claude --plugin-dir /path/to/dev-team
```

## Usage

### Coordinators (multi-agent orchestration)

```bash
# Universal coordinator (auto-detects stack):
/dev-team Implement authentication system with JWT and OAuth2

# Stack-specific coordinators:
/dev-team-node Add API endpoint with NestJS controller and service
/dev-team-python Create Django model with DRF serializer and viewset

# Greenfield architecture (works with empty projects):
/dev-team-node Design a marketplace backend with NestJS
/dev-team-python Design a SaaS platform with Django

# The coordinator automatically:
# 1. Analyzes the task (detects greenfield vs existing project)
# 2. Dispatches agents with inline quality gates:
#    - Each document → doc-reviewer → rework if needed
#    - Each code change → code-reviewer → rework if needed
# 3. Dispatches implementor/tester (parallel when independent)
# 4. Final cross-cutting review (multi-agent tasks)
# 5. Reports summary to user
```

### Shortcut Commands (direct agent dispatch)

Use `ask-*` commands to dispatch a specific agent directly, bypassing the coordinator. Ideal for single-agent tasks with clear scope.

```bash
# Requirements & planning:
/ask-prd Create PRD for a task management system with auth and dashboards
/ask-architect Design architecture for marketplace — NestJS + PostgreSQL + Next.js
/ask-planner Decompose migration from REST to GraphQL

# Design:
/ask-designer Design onboarding flow for mobile-first SaaS

# Implementation:
/ask-frontend Build responsive user registration form with validation
/ask-backend Implement JWT authentication with role-based access control
/ask-implementor Set up GitHub Actions CI/CD pipeline

# Quality:
/ask-tester Write tests for src/auth/ module
/ask-reviewer Review recent changes for security and code quality
/ask-doc-reviewer Review docs/prd.md for completeness and clarity
```

| Command | Agent | Model |
|---------|-------|-------|
| `/ask-prd` | product-analyst | opus |
| `/ask-architect` | architect | opus |
| `/ask-planner` | planner | opus |
| `/ask-designer` | ui-ux-designer | sonnet |
| `/ask-frontend` | frontend-dev | sonnet |
| `/ask-backend` | backend-dev | sonnet |
| `/ask-implementor` | implementor | sonnet |
| `/ask-tester` | tester | sonnet |
| `/ask-reviewer` | code-reviewer | sonnet |
| `/ask-doc-reviewer` | doc-reviewer | sonnet |

## Architecture

```
Coordinators (multi-agent)          Shortcuts (single-agent)
├── /dev-team                       ├── /ask-prd
├── /dev-team-node                  ├── /ask-architect
└── /dev-team-python                ├── /ask-planner
    |                               ├── /ask-designer
    +-- product-analyst  (opus)     ├── /ask-frontend
    +-- architect        (opus)     ├── /ask-backend
    +-- planner          (opus)     ├── /ask-implementor
    +-- ui-ux-designer   (sonnet)   ├── /ask-tester
    +-- frontend-dev     (sonnet)   ├── /ask-reviewer
    +-- backend-dev      (sonnet)   └── /ask-doc-reviewer
    +-- implementor      (sonnet)
    +-- tester           (sonnet)
    +-- code-reviewer    (sonnet)   ← inline after every code agent
    +-- doc-reviewer     (sonnet)   ← inline after every doc agent
```

**Context isolation**: each agent gets a clean context and does not inherit the coordinator's session. The coordinator includes the full task description, scope boundaries, and report protocol in every dispatch.

**Dynamic skill injection**: skills are injected into agents based on file patterns (`pathPatterns`), command patterns (`bashPatterns`), import detection (`importPatterns`), and prompt signals (`promptSignals`) — not loaded globally.

**Inline quality gates**: every artifact goes through a review-and-rework cycle. Documents are reviewed by `doc-reviewer`, code by `code-reviewer`. If concerns are found, the original agent is re-dispatched with findings (max 1 rework). See `specs/workflow.md` for full mermaid diagrams.

## Plugin Structure

```
dev-team/
├── .codex-plugin/
│   └── plugin.json              # Codex plugin manifest
├── .claude-plugin/
│   ├── marketplace.json         # Marketplace metadata
│   └── plugin.json              # Plugin manifest
├── .agents/
│   └── plugins/
│       └── marketplace.json     # Repo-local Codex marketplace entry
├── commands/
│   ├── dev-team.md              # Universal coordinator (auto-detect)
│   ├── dev-team-node.md         # Node.js coordinator
│   ├── dev-team-python.md       # Python coordinator
│   ├── ask-prd.md               # Direct: product-analyst
│   ├── ask-architect.md         # Direct: architect
│   ├── ask-planner.md           # Direct: planner
│   ├── ask-designer.md          # Direct: ui-ux-designer
│   ├── ask-frontend.md          # Direct: frontend-dev
│   ├── ask-backend.md           # Direct: backend-dev
│   ├── ask-implementor.md       # Direct: implementor
│   ├── ask-tester.md            # Direct: tester
│   ├── ask-reviewer.md          # Direct: code-reviewer
│   └── ask-doc-reviewer.md      # Direct: doc-reviewer
├── agents/
│   ├── _template.md             # Template for creating new agents
│   ├── product-analyst.md       # PRD creator (cyan, opus)
│   ├── architect.md             # System designer (blue, opus)
│   ├── planner.md               # Task decomposer (cyan, opus)
│   ├── ui-ux-designer.md        # UI/UX designer (magenta, read-only)
│   ├── frontend-dev.md          # UI developer (magenta, full tools)
│   ├── backend-dev.md           # API developer (green, full tools)
│   ├── implementor.md           # General fallback (green, full tools)
│   ├── tester.md                # Test writer & runner (yellow, full tools)
│   ├── code-reviewer.md         # Code reviewer (red, read-only)
│   └── doc-reviewer.md          # Doc reviewer (cyan, read-only)
├── skills/
│   ├── nodejs-stack/
│   │   ├── SKILL.md             # Node.js/TS patterns & conventions
│   │   └── references/
│   │       └── architecture-patterns.md  # NestJS, Next.js, monorepo
│   ├── python-stack/
│   │   ├── SKILL.md             # Python patterns & conventions
│   │   └── references/
│   │       └── architecture-patterns.md  # Django, Flask, FastAPI
│   └── _template/
│       ├── SKILL.md             # Skill template with metadata example
│       └── references/
│           └── _template.md     # Reference file template
├── CLAUDE.md                    # Plugin instructions
└── specs/
    ├── dev-team-architecture.md # Architecture specification
    └── workflow.md              # Workflow mermaid diagrams
```

## Coordinator Workflow

| Phase | Goal | Details |
|-------|------|---------|
| 1. Analysis | Understand the task | Detect stack, determine specialists, decompose into subtasks |
| 2. Dispatch | Launch agents with inline review | Each doc → doc-reviewer, each code → code-reviewer. Rework on concerns (max 1x) |
| 3. Collection | Process results | Handle DONE / BLOCKED / NEEDS_CONTEXT statuses (max 2 re-dispatches) |
| 4. Final Review | Cross-cutting review | Cross-module code consistency + cross-document consistency (if multi-agent) |
| 5. Report | Summary | Files changed, tests, review findings, concerns, next steps |

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

**Available agents:**

| Agent | Role | Tools | Model | Color |
|-------|------|-------|-------|-------|
| product-analyst | Requirements analysis, PRD | Read, Write, Grep, Glob | opus | cyan |
| architect | System design, blueprints | Read, Write, Grep, Glob | opus | blue |
| planner | Task decomposition, execution plans | Read, Write, Grep, Glob | opus | cyan |
| ui-ux-designer | UI/UX: user flows, layouts, specs | Read, Write, Grep, Glob | sonnet | magenta |
| frontend-dev | UI: components, pages, styles, a11y | Read, Write, Edit, Grep, Glob, Bash | sonnet | magenta |
| backend-dev | API: endpoints, models, services, auth | Read, Write, Edit, Grep, Glob, Bash | sonnet | green |
| implementor | General fallback: scripts, config, utils | Read, Write, Edit, Grep, Glob, Bash | sonnet | green |
| tester | Test writing and execution | Read, Write, Edit, Grep, Glob, Bash | sonnet | yellow |
| code-reviewer | Code quality review (inline after every code agent) | Read, Grep, Glob | opus | red |
| doc-reviewer | Doc quality review (inline after every doc agent) | Read, Grep, Glob | opus | cyan |

## Adding a New Skill

1. Copy `skills/_template/` to `skills/<skill-name>/`
2. Edit `SKILL.md`: set `name`, `description`, `metadata` (pathPatterns, promptSignals)
3. Write skill content (keep under 2000 words)
4. Put detailed documentation in `references/`
5. Restart Claude Code — the skill is auto-discovered

## Adding a New Stack

To add support for a new technology stack (e.g., Go, Rust, Java):

1. Create `commands/dev-team-<stack>.md` — copy from an existing stack coordinator, adapt detection patterns, greenfield detection, and stack-specific dispatch phrases
2. Create `skills/<stack>-stack/SKILL.md` — add `pathPatterns`, `importPatterns`, `promptSignals` for the stack's file types
3. Create `skills/<stack>-stack/references/architecture-patterns.md` — stack-specific architecture patterns for the architect agent
4. Update `commands/dev-team.md` to list the new stack coordinator

## Verification

| Check | How | Expected |
|-------|-----|----------|
| Plugin installed | Type `/dev-team` | Command available |
| Stack commands | Type `/dev-team-node` or `/dev-team-python` | Stack coordinators available |
| Shortcut commands | Type `/ask-prd` | 10 shortcut commands available |
| Agents available | Claude suggests agents | 10 agents: product-analyst, architect, planner, ui-ux-designer, frontend-dev, backend-dev, implementor, tester, code-reviewer, doc-reviewer |
| Tools isolation | Dispatch code-reviewer | Write/Edit unavailable |
| Skill injection | Agent reads `.ts` file | nodejs-stack skill injected |
| Coordinator isolation | `/dev-team` doesn't see skills | Clean coordinator context |

For debugging: `claude --debug` shows skill injection and hook activity.

## License

MIT
