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
- **Conditional adversarial debate**: in the Full profile, every PRD and execution plan is challenged by the read-only `adversarial-reviewer` before ordinary doc-review; Micro and Standard run zero debate cycles. Downstream agents see only consensus or arbitrated documents
- **Pipeline profiles (Phase 0 triage)**: every task is scored (size, novelty, clarity, reversibility, parallelizability; 0–2 each) and assigned Micro (≤~3 files: implement + 1 review), Standard (thin delta brief + slices + tester + 1 review, no debate), or Full (complete pipeline). Lean is the default; greenfield is always Full; skipped phases carry a recorded reason
- **Documentation adequacy**: an authoritative user spec or existing code pattern is never re-derived — documents reference it and add only a thin delta brief; a Phase 0 prior-art scan biases toward translating existing in-repo patterns
- **Blocking-questions gate + ground truth**: externally grounded facts (endpoints, hosts, contracts, IDs) and irreversible decisions halt for one batched user question or are verified against the authoritative source before encoding; only reversible internal defaults may proceed-and-log. Mid-task info patches the brief (append, don't re-gate); only a genuine goal/scope pivot restarts debate
- **Idempotency + circuit-breaker**: the ledger records profile, rationale, and a run counter; completed/locked artifacts are never re-dispatched without an invalidation reason, and a Micro/Standard task past 8 agent runs auto-escalates to the user
- **Review-and-rework pattern**: if reviewer finds concerns → original agent is re-dispatched with findings
- **Evidence gate**: DONE is only accepted with fresh verification output (see Report Protocol)
- **Vertical slices**: the planner decomposes by end-to-end user paths (tracer bullet first), not by layers
- **Tester-first per slice**: tester writes failing acceptance tests (Mode A) before implementation, then verifies green and extends coverage (Mode B) after
- **Progress ledger**: the coordinator maintains `docs/progress.md` (goal, AC-IDs, task table with evidence, decisions, open questions with triggers) and re-reads it at every phase start — the file, not conversation memory, is the source of truth
- **Input inventory**: user-provided inputs (briefs, prototypes, mockups, brand assets, existing docs) are collected in Phase 1 and are normative; requirements without a source are marked `invented — requires user confirmation` and need the user's answer before dependent work. Where no inputs exist, the decisions they would cover come from the user, not from agents' invention
- **OQ gate**: open questions carry `Confirm before:` triggers; before slice N the coordinator asks the user every question tagged for it (one batch) or records an explicit MVP waiver — an unanswered triggered question blocks the slice
- **DoD gate + demo checkpoint**: slice N+1 starts only after slice N's acceptance tests pass, code review is DONE, and the user has seen a demo of the increment; deviations are explicit user decisions with a debt-closure slice
- **Docs-code sync**: a code change that alters requirements, design, or plan updates the owning document in the same slice

## Available Agents

The plugin exposes 11 agents. `adversarial-reviewer` is internal and has no public shortcut.

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
| `/ask-implementor` | implementor | Scripts, config, CI/CD, utilities |
| `/ask-tester` | tester | Write and run tests |
| `/ask-reviewer` | code-reviewer | Review code for quality and bugs |
| `/ask-doc-reviewer` | doc-reviewer | Review documentation quality |

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
- **Fix-or-abstain.** "No change was needed" is a valid outcome backed by evidence; invented changes and unverified fixes are not.

**Status handling by coordinator:**

| Status | Coordinator Action |
|--------|-------------------|
| DONE (with Evidence) | Record in docs/progress.md, proceed to next phase |
| DONE without Evidence | Treat as DONE_WITH_CONCERNS — re-dispatch demanding verification |
| DONE_WITH_CONCERNS | Re-dispatch original agent with findings to fix |
| BLOCKED | Provide missing info, re-dispatch agent |
| NEEDS_CONTEXT | Answer questions or ask user, re-dispatch |

**Independent limits**: PRD/plan debate allows at most 3 creator-response/challenger-recheck cycles. The subsequent ordinary doc-review keeps its separate limit of 2 rework dispatches. Other artifact gates allow 2 reworks. If the same ordinary-review failure signature appears 3 times, change strategy once or escalate with the attempt history. Never loop.

## Inline Review Workflow

Every artifact produced in Phase 2 goes through an inline gate before the next agent consumes it. For PRDs and plans, `adversarial-reviewer` attacks assumptions and failure scenarios; `doc-reviewer` then validates completeness, consistency, and actionability. After debate cycle 3, `doc-reviewer` first arbitrates unresolved `CH-*` items and escalates product intent or unavailable evidence to the user.

| Artifact | Creator | Reviewer | On concerns |
|----------|---------|----------|-------------|
| PRD | product-analyst | adversarial-reviewer, then doc-reviewer | Debate up to 3 cycles; ordinary review up to 2 reworks |
| Architecture | architect | doc-reviewer | Re-dispatch architect |
| Design spec | ui-ux-designer | doc-reviewer | Re-dispatch ui-ux-designer |
| Execution plan | planner | adversarial-reviewer, then doc-reviewer | Debate up to 3 cycles; ordinary review up to 2 reworks |
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
- Include **context** about what other agents have done
- Pass the **input inventory** (paths of user-provided briefs, prototypes, brand assets — or "none") to product-analyst and ui-ux-designer; document agents read the inputs, the coordinator does not
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
