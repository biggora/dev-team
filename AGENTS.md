# dev-team Plugin

## Architecture

This plugin implements a "coordinator + specialists" architecture with inline quality gates:

- `/dev-team` — universal coordinator that auto-detects the stack
- `/dev-team-node` — Node.js/TypeScript coordinator (Next.js, NestJS, Vite, Express)
- `/dev-team-python` — Python coordinator (Django, Flask, FastAPI)
- Specialist agents operate with isolated contexts — they do not inherit the coordinator's session
- Skills are surfaced by their descriptions; dispatch prompts include stack phrases to help agents pick the relevant ones
- The coordinator does NOT read project source files — only git status, Glob, and Grep for structure analysis
- **Every artifact is reviewed inline**: doc-reviewer after each document, code-reviewer after each code agent
- **Proportional adversarial debate**: in the Full profile, debate depth is gated by artifact complexity — Light (<5 AC-IDs) skips debate, Standard (5–15) allows 1 cycle, Deep (15+) uses the full 3-cycle budget; Micro and Standard profiles run zero debate cycles. Architecture and design reviews are conditional on novelty. Downstream agents see only consensus or arbitrated documents
- **Pipeline profiles (Phase 0 triage)**: every task is scored (size, novelty, clarity, reversibility, parallelizability; 0–2 each) and assigned Micro (≤~3 files: implement + 1 review), Standard (thin delta brief + slices + tester + 1 review, no debate), or Full (complete pipeline). Lean is the default; greenfield is always Full; skipped phases carry a recorded reason
- **Documentation adequacy**: an authoritative user spec or existing code pattern is never re-derived — documents reference it and add only a thin delta brief; a Phase 0 prior-art scan biases toward translating existing in-repo patterns
- **Blocking-questions gate + ground truth**: externally grounded facts (endpoints, hosts, contracts, IDs) and irreversible decisions halt for one batched user question or are verified against the authoritative source before encoding; only reversible internal defaults may proceed-and-log. Mid-task info patches the brief (append, don't re-gate); only a genuine goal/scope pivot restarts debate
- **Idempotency + circuit-breaker**: the ledger records profile, rationale, and a run counter; completed/locked artifacts are never re-dispatched without an invalidation reason. Circuit-breaker thresholds: Micro/Standard 8 runs, Full 40 runs; per-slice sub-breaker at 6 implementation dispatches
- **Review-and-rework pattern**: if reviewer finds concerns → original agent is re-dispatched with findings; re-dispatch limit of 3 per scope+role with attempt context passed to the agent
- **Scope-proportional evidence**: DONE requires fresh verification output; failures outside the agent's dispatched scope are accepted as DONE (not re-dispatched) with failures recorded in the ledger
- **Session continuity**: `/handoff` saves session state to `docs/handoff.md`; `/resume` reconstructs coordinator state and continues from where the previous session stopped
- **Vertical slices**: the planner decomposes by end-to-end user paths (tracer bullet first), not by layers
- **Tester-first per slice**: tester writes failing acceptance tests (Mode A) before implementation, then verifies green and extends coverage (Mode B) after
- **Progress ledger**: the coordinator maintains `docs/progress.md` (goal, AC-IDs, task table with evidence, decisions, open questions with triggers) and re-reads it at every phase start — the file, not conversation memory, is the source of truth
- **Input inventory**: user-provided inputs (briefs, prototypes, mockups, brand assets, existing docs) are collected in Phase 1 and are normative; requirements without a source are marked `invented — requires user confirmation` and need the user's answer before dependent work. Where no inputs exist, the decisions they would cover come from the user, not from agents' invention
- **Use cases per role**: actors are stable `ROLE-###` IDs in the PRD. With two or more `human` roles the product-analyst also writes `docs/use-cases.md` — use cases grouped by role plus a role × use-case permission matrix whose every `denied` cell cites a denial AC-ID; with one role they stay in the PRD and no file is created, and Micro never produces them. The catalogue is part of the PRD gate, not a separate artifact: one debate, one doc-review, no extra dispatch
- **OQ gate**: open questions carry `Confirm before:` triggers; before slice N the coordinator asks the user every question tagged for it (one batch) or records an explicit MVP waiver — an unanswered triggered question blocks the slice
- **DoD gate + demo checkpoint**: slice N+1 starts only after slice N's acceptance tests pass, code review is DONE, and the user has seen a demo of the increment; deviations are explicit user decisions with a debt-closure slice
- **Docs-code sync**: a code change that alters requirements, design, or plan updates the owning document in the same slice
- **Local-stack gate**: a project with external runtime dependencies (database, cache, message broker or queue, SMTP, object storage, search engine, identity provider, third-party HTTP API) must have them running locally in version-pinned containers with health checks before slice 1 starts and for every verification afterwards; `devops-engineer` owns that stack. A dependency whose real service cannot run locally gets a containerized emulator (`stripe-mock`, `localstack`, `wiremock`, `mailpit`); if no emulator exists the coordinator halts for one batched user question and the affected AC stays UNVERIFIED until an explicit user waiver is recorded. Evidence produced against a mock, stub, or in-memory substitute for a dependency that has a container equivalent is not local evidence; a project with genuinely no external dependencies records `Local stack: N/A — <reason>`. The pipeline profile never exempts a task from this gate, and when a compose file already covers the whole inventory the gate is satisfied by evidence, not by a dispatch
- **CI/CD last**: CI/CD work (CI pipelines, deployment configs/images, publish/release) is never part of scaffolding or intermediate slices — it is planned only as the final subtask, owned by `devops-engineer`, and dispatched only after the local-proof gate passes: the local-stack gate is satisfied, every AC-ID verified with fresh evidence produced against the running stack, the full test suite (unit + integration + e2e) green, and the final demo checkpoint accepted by the user. The pipeline encodes only checks already proven green locally, against the same pinned images. Local dev tooling (`docker-compose.yml`, dev Dockerfile, seed and reset scripts, git hooks, lint config) is not CI/CD and comes earlier by design

## Available Agents

The plugin exposes 12 agents. `adversarial-reviewer` is internal and has no public shortcut.

| Agent | Role | Tools | Model | Color |
|-------|------|-------|-------|-------|
| product-analyst | Formalizes requirements into PRD | Read, Write, Grep, Glob | opus | cyan |
| adversarial-reviewer | Challenges PRDs and plans; never edits artifacts | Read, Grep, Glob | opus | red |
| architect | Designs system architecture and blueprints | Read, Write, Grep, Glob | opus | blue |
| planner | Decomposes tasks into vertical slices | Read, Write, Grep, Glob | opus | cyan |
| ui-ux-designer | Designs UI/UX: flows, layouts, specs | Read, Write, Grep, Glob | sonnet | magenta |
| frontend-dev | Builds UI: components, pages, styles, a11y | Read, Write, Edit, Grep, Glob, Bash | sonnet | magenta |
| backend-dev | Builds API: endpoints, models, services, auth | Read, Write, Edit, Grep, Glob, Bash | sonnet | green |
| implementor | General fallback: scripts, config, utilities | Read, Write, Edit, Grep, Glob, Bash | sonnet | green |
| devops-engineer | Local containerized stack (docker-compose, emulators, seed) and CI/CD after the local-proof gate | Read, Write, Edit, Grep, Glob, Bash | sonnet | yellow |
| tester | Writes and runs tests (Mode A red / Mode B green) | Read, Write, Edit, Grep, Glob, Bash | sonnet | yellow |
| code-reviewer | Reviews code for quality and bugs | Read, Grep, Glob | opus | red |
| doc-reviewer | Reviews documentation for quality and completeness | Read, Grep, Glob | opus | cyan |

## Shortcut Commands (Direct Agent Dispatch)

Use `ask-*` commands for focused workflows that bypass the full coordinator. Most shortcuts dispatch one specialist; `/ask-prd` and `/ask-planner` run creator → adversarial debate → arbitration when needed → ordinary doc-review:

| Command | Agent | Use case |
|---------|-------|----------|
| `/ask-prd` | product-analyst + review agents | Create PRD through debate and final doc-review |
| `/ask-architect` | architect | Design system architecture |
| `/ask-planner` | planner + review agents | Create slice plan through debate and final doc-review |
| `/ask-designer` | ui-ux-designer | Design UI/UX flows and layouts |
| `/ask-frontend` | frontend-dev | Build UI components, pages, styles |
| `/ask-backend` | backend-dev | Build API, models, services |
| `/ask-implementor` | implementor | Scripts, config, utilities |
| `/ask-devops` | devops-engineer | Local stack: docker-compose, emulators, seed data; CI/CD after local proof |
| `/ask-tester` | tester | Write and run tests |
| `/ask-reviewer` | code-reviewer | Review code for quality and bugs |
| `/ask-doc-reviewer` | doc-reviewer | Review documentation quality |
| `/handoff` | coordinator | Save dev-team session state for resumption |
| `/resume` | coordinator | Resume previously interrupted dev-team session |

**When to use shortcuts vs coordinator:**
- `/ask-*` — focused tasks with clear scope; PRD and plan shortcuts still enforce their multi-agent document gates (`/ask-prd` and `/ask-planner` always run the full document gate — profile-independent by design)
- `/dev-team` — complex tasks requiring multiple agents, decomposition, and coordination

## Report Protocol

Every agent MUST end its response with a structured report:

```
Status: DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT

Files changed: [files created or modified, or "none"]
Summary: [what was done, key decisions made]
Evidence: [every verification command run JUST NOW: command → exit code → key output lines. Read-only agents cite file:line for every claim instead. Results from memory do not count.]
Criteria: [each acceptance criterion in scope from docs/prd.md with PASS/FAIL and the Evidence line that proves it — or "N/A: no PRD"]
Concerns: [only if DONE_WITH_CONCERNS — what worries you]
Blocked on: [only if BLOCKED — what prevents completion]
Questions: [only if NEEDS_CONTEXT — what information is needed]
```

Report rules (canonical copy: `templates/agent-template.md`):
- **DONE requires Evidence.** No fresh command output (or citations) → the agent may not report DONE.
- **Red means not DONE.** Any failing test, build, or lint in Evidence → BLOCKED or DONE_WITH_CONCERNS, never DONE.
- **Scope-aware red.** If the dispatch defines an Evidence scope, failures outside that scope are reported in Concerns as "out-of-scope" and do not block DONE.
- **Fix-or-abstain.** "No change was needed" is a valid outcome backed by evidence; invented changes and unverified fixes are not.

**Status handling by coordinator:**

| Status | Coordinator Action |
|--------|-------------------|
| DONE (with Evidence, all green or out-of-scope only) | Record in docs/progress.md, proceed to next phase |
| DONE without Evidence | Treat as DONE_WITH_CONCERNS — re-dispatch demanding verification |
| DONE with in-scope failures | Treat as DONE_WITH_CONCERNS — re-dispatch (max 3 per scope+role) |
| DONE_WITH_CONCERNS | Read concerns, decide if action needed. If yes — re-dispatch. If no — note for final report |
| BLOCKED | Provide missing info, re-dispatch agent |
| NEEDS_CONTEXT | Answer questions or ask user, re-dispatch |

**Independent limits**: PRD/plan debate allows at most 3 creator-response/challenger-recheck cycles. The subsequent ordinary doc-review keeps its separate limit of 2 rework dispatches. Other artifact gates allow 2 reworks. If the same ordinary-review failure signature appears 3 times, change strategy once or escalate with the attempt history. Never loop.

## Inline Review Workflow

Every artifact produced in Phase 2 goes through an inline gate before the next agent consumes it. For PRDs and plans, `adversarial-reviewer` attacks assumptions and failure scenarios; `doc-reviewer` then validates completeness, consistency, and actionability. After debate cycle 3, `doc-reviewer` first arbitrates unresolved `CH-*` items and escalates product intent or unavailable evidence to the user.

| Artifact | Creator | Reviewer | On concerns |
|----------|---------|----------|-------------|
| PRD (+ use cases) | product-analyst | adversarial-reviewer, then doc-reviewer | Debate up to 3 cycles; ordinary review up to 2 reworks; the use-case catalogue rides the same dispatches |
| Architecture | architect | doc-reviewer | Re-dispatch architect |
| Design spec | ui-ux-designer | doc-reviewer | Re-dispatch ui-ux-designer |
| Execution plan | planner | adversarial-reviewer, then doc-reviewer | Debate up to 3 cycles; ordinary review up to 2 reworks |
| Local stack (compose, env, seed) | devops-engineer | code-reviewer | Re-dispatch devops-engineer |
| Scaffold code | implementor | code-reviewer | Re-dispatch implementor |
| Backend code | backend-dev | code-reviewer | Re-dispatch backend-dev |
| Frontend code | frontend-dev | code-reviewer | Re-dispatch frontend-dev |
| Test code | tester | code-reviewer | Re-dispatch tester |

Phase 4 performs a criteria coverage check (every AC-ID must have passing evidence or be listed UNVERIFIED) plus a final cross-cutting review (code-reviewer for cross-module consistency + doc-reviewer for cross-document consistency) when multiple agents were dispatched. ACs naming real external integrations are UNVERIFIED with mock-only evidence.

See `specs/workflow.md` for full mermaid diagrams.

## Dispatch Rules (for coordinator)

- **Check the ledger before every dispatch** (idempotency guard) and increment the run counter; respect the 8-run circuit-breaker for Micro/Standard
- Include the **full task description** — agents cannot see coordinator context
- Specify **scope boundaries** — which files/directories can be changed; the test directory belongs to the tester
- Infrastructure files (`docker-compose*.yml`, `Dockerfile*`, `.env.example`, `.dockerignore`, seed and reset scripts) are **devops-engineer's exclusive writable scope** — no other agent may edit them in any dispatch, parallel or not
- **Never dispatch CI/CD to implementor** — CI pipelines, deployment configs, and release tooling go to devops-engineer, and only after the local-proof gate passes
- Include **context** about what other agents have done
- Pass the **input inventory** (paths of user-provided briefs, prototypes, brand assets — or "none") to product-analyst and ui-ux-designer; document agents read the inputs, the coordinator does not
- For products with more than one kind of user: instruct product-analyst to define `ROLE-###` actors and a role × use-case permission matrix, and paste the matrix rows for the current slice into backend-dev and frontend-dev prompts — a `denied` cell is behavior to implement, and agents do not read documents you did not name
- For PRD/plan debate, include the original request, artifact path and version, cycle number, unresolved `CH-*`, latest dispositions/evidence, and related documents; store only cycle, verdict, and unresolved IDs in `docs/progress.md`
- Add the **report reminder line** to every dispatch: "Reminder: Status DONE requires the Evidence field with fresh command output; failing checks forbid DONE" (the full protocol lives in each agent's own prompt)
- Independent tasks → **multiple Agent tool calls in one message** (parallel dispatch); parallel agents must never share writable files
- Include **stack-specific phrases** in prompts (e.g., "typescript", "nestjs", "django") to help agents pick relevant skills — critical for greenfield projects where no files exist yet
- For architect on greenfield: explicitly instruct to "Read references/architecture-patterns.md" from the matching stack skill
- For metric-optimization tasks: dispatch implementor instructed to apply the **autoresearch** skill (immutable evaluator, atomic mutations, keep/discard by metric)
- For UI tasks: name the aesthetic explicitly so ui-ux-designer and frontend-dev pick the same **design-styles** preset

## Agent Guidelines

- Work only within your specified scope boundaries
- Follow the coding conventions of the project you are working in
- Always end with the structured report, Evidence included
- Implementation agents never touch test files; the tester never touches source files
- Implementation agents verify against the running local stack — never substitute a mock, stub, or in-memory fake for a dependency that has a container in `docker-compose.yml`
- If blocked, report `BLOCKED` with clear description rather than guessing
- If missing context, report `NEEDS_CONTEXT` with specific questions

## Adding New Agents

1. Copy `templates/agent-template.md` to `agents/<agent-name>.md`
2. Fill in frontmatter: name, description (with `<example>` blocks), model, color, tools
3. Write the system prompt: role, responsibilities, process, output format
4. Include the report protocol (with Evidence/Criteria fields and report rules) at the end of the system prompt — copy it from the template verbatim
5. Restart Codex — agent is auto-discovered

## Adding New Skills

1. Copy `templates/skill-template/` directory to `skills/<skill-name>/`
2. Edit `SKILL.md`: set name and a specific trigger description (the description is the only triggering mechanism)
3. Write skill content (keep under 2000 words)
4. Put detailed docs in `references/` subdirectory
5. Restart Codex — skill is auto-discovered
