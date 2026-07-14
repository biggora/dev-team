# dev-team

Plugin toolkit for orchestrating a team of specialized AI agents for full-cycle software development — from requirements to tested, reviewed code.

The coordinator (`/dev-team`) decomposes tasks into vertical slices, dispatches 11 specialist agents with isolated contexts, and enforces inline quality gates. A Phase 0 triage assigns each task a pipeline profile — Micro, Standard, or Full; lean is the default. In the Full profile every PRD and execution plan passes an adversarial debate before ordinary `doc-reviewer` review; code always passes `code-reviewer` review.

Every agent report must carry an `Evidence` field — fresh command output proving the work (a bare "DONE" is never trusted). The tester writes failing acceptance tests before implementation (Mode A) and verifies green after (Mode B); implementation agents are forbidden from touching test files. The coordinator tracks state in `docs/progress.md`.

Skills are surfaced by their descriptions and follow the cross-platform [Agent Skills](https://agentskills.io) standard, so the same skill set installs into Claude Code, Codex CLI, GitHub Copilot CLI, and Gemini CLI.

## Installation

### In Claude Code

#### From GitHub (recommended)

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

#### From local directory

```bash
# Step 1: Add local marketplace
/plugin marketplace add /path/to/dev-team

# Step 2: Install (globally by default)
/plugin install dev-team@dev-team

# OR install per-project
/plugin install dev-team@dev-team --scope project
```

#### Development mode (session only)

```bash
claude --plugin-dir /path/to/dev-team
```

Verify: type `/dev-team` — the coordinator should be available. Manifests can be checked with `claude plugin validate /path/to/dev-team --strict`.

### In Codex CLI

Codex discovers Agent Skills from `.agents/skills/` (project scope) and `~/.agents/skills/` or `~/.codex/skills/` (user scope). Symlinks are followed.

```bash
git clone https://github.com/biggora/dev-team

# User scope — available in every project:
ln -s "$(pwd)/dev-team/skills" ~/.agents/skills
# or copy selectively:
cp -r dev-team/skills/* ~/.codex/skills/

# Project scope — available in one repository:
mkdir -p .agents && ln -s /path/to/dev-team/skills .agents/skills
```

Codex does **not** register Claude-style slash commands or markdown agents natively. The `dev-team-codex` bridge skill covers that gap — invoke it with natural language:

```text
Use dev-team to plan and implement this feature.
Use dev-team reviewer flow to inspect my recent changes.
Use /ask-backend semantics for this API task.
```

The skill interprets those phrases, reads the bundled coordinator skills and `agents/*.md` prompt files, and dispatches Codex subagents via `spawn_agent`, preserving the inline review gates.

To disable an individual skill without deleting it, add to `~/.codex/config.toml` (restart Codex afterwards):

```toml
[[skills.config]]
path = "/path/to/skill/SKILL.md"
enabled = false
```

### In GitHub Copilot CLI

Copilot discovers Agent Skills from `.github/skills/`, `.claude/skills/`, `.agents/skills/` (project) and `~/.copilot/skills/`, `~/.agents/skills/` (personal).

```bash
# Add the whole skill set from a clone:
git clone https://github.com/biggora/dev-team
copilot skill add /path/to/dev-team/skills

# Or install individual skills straight from GitHub (requires gh >= 2.90):
gh skill install biggora/dev-team dev-team --agent copilot --scope project

# Verify (inside a Copilot session):
/skills list
```

Copilot also reads `AGENTS.md` and `CLAUDE.md` custom instructions automatically when working inside a clone of this repository.

### In Gemini CLI

Gemini CLI (>= 0.26) supports Agent Skills natively. Note: it validates frontmatter strictly — the `---` block must be the very first content of `SKILL.md` (all skills in this repository comply).

```bash
# Install all skills from this repository:
gemini skills install https://github.com/biggora/dev-team --path skills --scope user

# Or per-workspace:
gemini skills install https://github.com/biggora/dev-team --path skills --scope workspace

# Verify:
gemini skills list --all
```

Workspace-scope skills load only in trusted folders (`/trust`, then restart). The repository ships a `GEMINI.md` with the workflow context.

### Portability notes

- All skills use the portable Agent Skills core: `name` + `description` + markdown body. Claude-specific frontmatter (`disable-model-invocation`, `allowed-tools`, `argument-hint`) is silently ignored by other platforms.
- The coordinator skills (`dev-team`, `dev-team-node`, `dev-team-python`, `ask-*`) are user-invoked slash commands in Claude Code; on other platforms they activate by description match or explicit mention.
- Native subagents (`agents/*.md`), inline review gates, and parallel dispatch are fully supported in Claude Code; on other platforms the `dev-team-codex` bridge skill emulates the workflow.

## Usage

### In Claude Code: Coordinators (multi-agent orchestration)

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
# 1. Triages the task and picks a profile (Micro / Standard / Full; greenfield = Full)
# 2. Analyzes the task (detects greenfield vs existing project)
# 3. Dispatches agents with inline quality gates:
#    - PRD and plan (Full profile) → debate → consensus + ordinary review, or combined arbitration/full review
#    - Other documents → doc-reviewer → rework if needed
#    - Each code change → code-reviewer → rework if needed
# 4. Dispatches implementor/tester (parallel when independent)
# 5. Final cross-cutting review (multi-agent tasks)
# 6. Reports summary to user
```

### In Codex CLI

Codex does not provide `/dev-team` or `/ask-*` as real slash commands from this plugin. Use the same names as prompt phrases instead:

```text
Use dev-team to implement authentication with JWT and OAuth2.
Use dev-team-node semantics to add a NestJS controller and service.
Use dev-team-python semantics to create a Django model and DRF serializer.
Use /ask-reviewer semantics to review my recent changes for security and correctness.
```

When those phrases appear, the `dev-team-codex` skill acts as the coordinator bridge:

1. It interprets the requested coordinator or specialist flow.
2. It runs Phase 0 triage and picks the pipeline profile (Micro / Standard / Full).
3. It reads the matching coordinator skills (`skills/dev-team*/SKILL.md`, `skills/ask-*/SKILL.md`) and `agents/*.md` prompts.
4. It dispatches Codex subagents with `spawn_agent`.
5. It preserves the inline `code-reviewer` and `doc-reviewer` gates, plus adversarial PRD/plan debate in the Full profile.
6. It reports back using the same structured report protocol.

### In Claude Code: Shortcut Commands (direct agent dispatch)

Use `ask-*` commands for focused workflows that bypass the full coordinator. Most dispatch one specialist. `/ask-prd` and `/ask-planner` run creator → adversarial debate, then either consensus + ordinary doc-review or combined arbitration/full review.

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
| `/ask-prd` | product-analyst + adversarial-reviewer + doc-reviewer | opus |
| `/ask-architect` | architect | opus |
| `/ask-planner` | planner + adversarial-reviewer + doc-reviewer | opus |
| `/ask-designer` | ui-ux-designer | sonnet |
| `/ask-frontend` | frontend-dev | sonnet |
| `/ask-backend` | backend-dev | sonnet |
| `/ask-implementor` | implementor | sonnet |
| `/ask-tester` | tester | sonnet |
| `/ask-reviewer` | code-reviewer | opus |
| `/ask-doc-reviewer` | doc-reviewer | opus |

## Architecture

```
Coordinators (multi-agent)          Focused shortcuts
├── /dev-team                       ├── /ask-prd
├── /dev-team-node                  ├── /ask-architect
└── /dev-team-python                ├── /ask-planner
    |                               ├── /ask-designer
    +-- product-analyst  (opus)     ├── /ask-frontend
    +-- adversarial-reviewer (opus)  │   (internal; no shortcut)
    +-- architect        (opus)     ├── /ask-backend
    +-- planner          (opus)     ├── /ask-implementor
    +-- ui-ux-designer   (sonnet)   ├── /ask-tester
    +-- frontend-dev     (sonnet)   ├── /ask-reviewer
    +-- backend-dev      (sonnet)   └── /ask-doc-reviewer
    +-- implementor      (sonnet)
    +-- tester           (sonnet)
    +-- code-reviewer    (opus)     ← inline after every code agent
    +-- doc-reviewer     (opus)     ← inline after every doc agent
```

**Context isolation**: each agent gets a clean context and does not inherit the coordinator's session. The coordinator includes the full task description, scope boundaries, and a report reminder in every dispatch (the full protocol lives in each agent's own prompt).

**Skill selection**: skills are surfaced by their descriptions; dispatch prompts include stack-specific phrases ("typescript", "nestjs", "django") to help agents pick the relevant ones.

**Inline quality gates**: In the Full profile, `adversarial-reviewer` attacks assumptions and plausible failure scenarios in every PRD and plan; the creator resolves stable `CH-*` items for at most 3 debate cycles. Consensus proceeds to ordinary `doc-reviewer` review with a separate 2-rework budget. After an unresolved third recheck, `doc-reviewer` arbitrates and performs the full review in one dispatch; successful arbitration needs no second ordinary review. Product intent or unavailable evidence is escalated to the user, then the creator updates and `doc-reviewer` resumes the combined review. Code uses `code-reviewer`. Downstream waits for either successful path. See `specs/workflow.md` for full diagrams.

**Evidence gate**: a DONE report without fresh verification output (command → exit code → key lines) is treated as unverified and sent back. Failing checks forbid DONE. "No change was needed" is a valid, evidence-backed outcome (fix-or-abstain).

**Cost and latency**: process cost is profile-driven. Micro tasks cost ~2–4 agent runs (implement + review); Standard stays within a lean envelope with zero debate cycles; a circuit-breaker stops any Micro/Standard task that exceeds 8 runs and asks the user. In the Full profile, PRD and plan creation require at least one challenger pass and one document review pass: ordinary doc-review on the consensus path, or combined arbitration/full review on the unresolved cycle-3 path. Revisions add creator and challenger dispatches, up to 3 debate cycles; unresolved cycle-3 items may pause for a user decision. Simple documents can reach consensus after the first challenge pass.

## Plugin Structure

```
dev-team/
├── .claude-plugin/
│   ├── marketplace.json         # Claude Code marketplace metadata
│   └── plugin.json              # Claude Code plugin manifest
├── .codex-plugin/
│   └── plugin.json              # Codex plugin manifest
├── .copilot-plugin/
│   ├── marketplace.json         # Copilot CLI marketplace metadata
│   └── plugin.json              # Copilot CLI plugin manifest
├── .agents/
│   └── plugins/
│       └── marketplace.json     # Repo-local Codex marketplace entry
├── agents/                      # 11 specialist subagents (Claude Code native)
│   ├── product-analyst.md       # PRD creator (cyan, opus)
│   ├── adversarial-reviewer.md  # PRD/plan challenger (red, read-only)
│   ├── architect.md             # System designer (blue, opus)
│   ├── planner.md               # Task decomposer (cyan, opus)
│   ├── ui-ux-designer.md        # UI/UX designer (magenta, read-only)
│   ├── frontend-dev.md          # UI developer (magenta, full tools)
│   ├── backend-dev.md           # API developer (green, full tools)
│   ├── implementor.md           # General fallback (green, full tools)
│   ├── tester.md                # Test writer & runner (yellow, full tools)
│   ├── code-reviewer.md         # Code reviewer (red, read-only)
│   └── doc-reviewer.md          # Doc reviewer (cyan, read-only)
├── skills/                      # 40 skills (Agent Skills standard)
│   ├── dev-team/                # /dev-team — universal coordinator (auto-detect)
│   ├── dev-team-node/           # /dev-team-node — Node.js coordinator
│   ├── dev-team-python/         # /dev-team-python — Python coordinator
│   ├── ask-prd/ … ask-doc-reviewer/   # 10 focused workflow shortcuts (/ask-*)
│   ├── dev-team-codex/          # Codex bridge: coordinator + specialists via spawn_agent
│   ├── nodejs-stack/            # Node.js/TS patterns (+ references/architecture-patterns.md)
│   ├── python-stack/            # Python patterns (+ references/architecture-patterns.md)
│   └── …                        # Stack & quality skills: nest/next/vite/tailwindcss best
│                                #   practices, typescript-expert, django-expert, security-review,
│                                #   code-review, postgresql-*, redis-development, shadcn,
│                                #   stripe-best-practices, ui-expert, prd, autoresearch, …
├── templates/
│   ├── agent-template.md        # Template for creating new agents
│   └── skill-template/          # Template for creating new skills
├── AGENTS.md                    # Workflow instructions for Codex / Copilot
├── CLAUDE.md                    # Workflow instructions for Claude Code
├── GEMINI.md                    # Workflow instructions for Gemini CLI
├── skills-lock.json             # Provenance of vendored skills (source + hash)
└── specs/
    ├── dev-team-architecture.md # Architecture specification
    ├── dev-team-optimization-proposals.md # Triage/profile design rationale
    └── workflow.md              # Workflow mermaid diagrams
```

## Coordinator Workflow

| Phase | Goal | Details |
|-------|------|---------|
| 0. Triage | Choose process weight | Score size/novelty/clarity/reversibility/parallelizability (0–2 each); select Micro / Standard / Full; documentation adequacy check, prior-art scan, batched blocking questions for external facts and irreversible decisions |
| 1. Analysis | Understand the task | Detect stack, determine specialists, decompose into vertical slices; create docs/progress.md after user confirms (Standard/Full) |
| 2. Dispatch | Launch agents with inline review | PRD/plan: creator → debate (max 3 cycles) → consensus + ordinary review (max 2 reworks), or combined arbitration/full review after the third unresolved recheck. Other docs go directly to doc-review. Per slice: tester Mode A → implementation → tester Mode B → code-reviewer. |
| 3. Collection | Process results | Evidence gate (DONE without Evidence = unverified), handle DONE / BLOCKED / NEEDS_CONTEXT, update docs/progress.md |
| 4. Final Review | Cross-cutting review | Criteria coverage check (every AC-ID verified or listed UNVERIFIED) + cross-module code consistency + cross-document consistency (if multi-agent) |
| 5. Report | Summary | AC-IDs verified N/M, files changed, test evidence, review findings, concerns, next steps |

## Report Protocol

Every agent ends with a structured report:

```
Status: DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT

Files changed: [files or "none"]
Summary: [what was done]
Evidence: [verification commands run JUST NOW: command → exit code → key output. Read-only agents cite file:line instead]
Criteria: [each acceptance criterion in scope: PASS/FAIL + evidence — or "N/A: no PRD"]
Concerns: [if DONE_WITH_CONCERNS]
Blocked on: [if BLOCKED]
Questions: [if NEEDS_CONTEXT]
```

Rules: **DONE requires Evidence** · **red means not DONE** · **fix-or-abstain** ("no change needed" is a valid, evidence-backed outcome). Canonical copy: `templates/agent-template.md`.

## Adding a New Agent

1. Copy `templates/agent-template.md` to `agents/<agent-name>.md`
2. Fill in frontmatter: `name`, `description` (with `<example>` blocks), `model`, `color`, `tools`
3. Write the system prompt with role, responsibilities, process, and output format
4. Include the report protocol at the end
5. Restart Claude Code — the agent is auto-discovered

**Available agents:**

| Agent | Role | Tools | Model | Color |
|-------|------|-------|-------|-------|
| product-analyst | Requirements analysis, PRD | Read, Write, Grep, Glob | opus | cyan |
| adversarial-reviewer | Read-only PRD/plan challenge in explicit modes | Read, Grep, Glob | opus | red |
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

1. Copy `templates/skill-template/` to `skills/<skill-name>/`
2. Edit `SKILL.md`: set `name` (must equal the folder name — lowercase, digits, hyphens, max 64 chars) and a specific trigger `description` (max 1024 chars; the description is the only triggering mechanism)
3. Write skill content (keep under 2000 words)
4. Put detailed documentation in `references/`
5. Restart Claude Code — the skill is auto-discovered

## Adding a New Stack

To add support for a new technology stack (e.g., Go, Rust, Java):

1. Create `skills/dev-team-<stack>/SKILL.md` — copy `skills/dev-team/SKILL.md` and replace only the frontmatter and the `## Stack Profile` section (detection patterns, greenfield detection, stack-specific dispatch phrases); the rest must stay identical across coordinators (see the SYNC comment at the top)
2. Create `skills/<stack>-stack/SKILL.md` with a trigger description covering the stack's file types and frameworks
3. Create `skills/<stack>-stack/references/architecture-patterns.md` — stack-specific architecture patterns for the architect agent
4. Update the `## Stack Profile` section of `skills/dev-team/SKILL.md` to list the new stack coordinator

## Verification

| Check | How | Expected |
|-------|-----|----------|
| Claude Code plugin | Type `/dev-team` | Command available |
| Manifest validity | `claude plugin validate /path/to/dev-team --strict` | Validation passed |
| Codex skills | Symlink/copy `skills/` into `~/.agents/skills/`, then prompt `Use dev-team ...` | `dev-team-codex` activates and orchestrates |
| Copilot CLI skills | `copilot skill add /path/to/dev-team/skills`, then `/skills list` | dev-team skills listed |
| Gemini CLI skills | `gemini skills install ... --path skills`, then `gemini skills list --all` | Skills listed, no frontmatter warnings |
| Stack commands (Claude Code) | Type `/dev-team-node` or `/dev-team-python` | Stack coordinators available |
| Shortcut commands (Claude Code) | Type `/ask-prd` | 10 shortcut commands available |
| Agents available | Claude suggests agents | 11 agents, including internal read-only adversarial-reviewer |
| Tools isolation | Dispatch code-reviewer | Write/Edit unavailable |
| Challenger isolation | Dispatch adversarial-reviewer in `prd` or `plan` mode | Read/Grep/Glob only; no challenge artifact or public shortcut |
| Skill selection | Dispatch agent with "typescript" phrases | Agent applies nodejs-stack skill |
| Evidence gate | Dispatch implementor on a repo with tests | Report contains Evidence with command + exit code |
| PRD/plan lifecycle | Run `/ask-prd` or `/ask-planner` in Claude Code | Creator, adversarial-reviewer, and doc-reviewer run in order; downstream waits for both gates |

For Codex specifically:

- `dev-team-codex` should trigger when the prompt includes `dev-team`, `/dev-team`, or `/ask-*` phrases.
- The skill should dispatch specialists through `spawn_agent` rather than claiming native slash-command support.

For debugging: `claude --debug` shows plugin loading and agent dispatch activity.

## License

MIT
