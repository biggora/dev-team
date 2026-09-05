# Dev-Team Workflow

## Overview

The dev-team plugin follows a six-phase (Phase 0–5) coordinator + specialists architecture. Documents and code are reviewed inline. In the Full profile, PRDs and execution plans first pass an adversarial debate, then either consensus plus ordinary document review or a combined arbitration/full review after an unresolved third recheck. Other artifacts enter their ordinary review gate immediately after creation.

Core disciplines:
- **Pipeline profiles**: Phase 0 triage scores the task (0–2 on size, novelty, ambiguity, irreversibility, parallelizability) and selects Micro / Standard / Full; lean is default, greenfield is always Full, and every skipped phase records a reason.
- **Blocking questions & ground truth**: externally grounded facts and irreversible decisions halt for one batched user question or are verified against the authoritative source; mid-task info patches the brief without restarting debate (append, don't re-gate).
- **Idempotency & circuit-breaker**: the ledger is the machine-checkable authority — completed/locked artifacts are never re-dispatched without an invalidation reason. Circuit-breaker thresholds: Micro/Standard 8 runs, Full 40 runs (or 3× slices × 5); per-slice sub-breaker at 6 implementation dispatches.
- **Scope-proportional evidence**: every agent report must contain an `Evidence` field with fresh command output (or file:line citations for read-only agents). A DONE without Evidence is treated as DONE_WITH_CONCERNS. Failures outside the agent's dispatched scope are accepted as DONE with the failures recorded — not re-dispatched.
- **Proportional debate**: Full-profile debate depth is gated by artifact complexity — Light (skip debate), Standard (1 cycle max), Deep (full 3-cycle budget). Architecture and design reviews are conditional on novelty.
- **Adversarial planning gate**: `adversarial-reviewer` attacks PRD and plan assumptions, trade-offs, and plausible failure scenarios. The document creator resolves stable `CH-*` challenges; downstream agents receive the document only after consensus plus ordinary review or successful combined arbitration/full review.
- **Separated review duties**: `adversarial-reviewer` performs risk-oriented challenge. `doc-reviewer` checks completeness, consistency, and actionability; after debate cycle 3, it also arbitrates unresolved challenges.
- **Vertical slices**: the planner decomposes into end-to-end user paths (tracer bullet first), mapped to PRD acceptance criterion IDs (AC-001...).
- **Tester-first per slice**: tester Mode A writes failing acceptance tests before implementation; implementation agents make them green (but never touch test files); tester Mode B verifies green and extends coverage.
- **Progress ledger**: the coordinator maintains `docs/progress.md` and re-reads it (plus `docs/prd.md`) at every phase and slice start.
- **Input inventory**: user-provided inputs (briefs, prototypes, mockups, brand assets, existing docs) are collected in Phase 1 and are normative; requirements without a source are marked `invented — requires user confirmation`. Where no inputs exist, the decisions they would cover come from the user.
- **OQ and DoD gates**: open questions tagged "before Slice N" must be answered by the user (or explicitly waived as MVP interpretation) before slice N starts; slice N+1 starts only after slice N passes tests, review, and a user demo checkpoint.
- **Docs-code sync**: a code change that alters requirements, design, or plan updates the owning document in the same slice.
- **Real stack before pipelines (local-stack gate)**: any project with external runtime dependencies (database, cache, broker or queue, SMTP, object storage, search engine, identity provider, third-party HTTP API) must have them running locally in version-pinned containers with health checks — owned by `devops-engineer`, replaced by a containerized emulator where no real service can run locally — before slice 1 starts and for every verification afterwards; evidence produced against a mock, stub, or in-memory substitute for a containerizable dependency is not local evidence, and a project with genuinely no external dependencies records `Local stack: N/A — <reason>`.
- **CI/CD last + local-proof gate**: CI/CD work (CI pipelines, deployment Dockerfiles/images, publish/release, staging/production configs) is never part of scaffolding or ordinary slices — it is planned only as the final subtask, owned by `devops-engineer`, and dispatched only after the local-proof gate passes: the local-stack gate is satisfied (a clean `docker compose down -v` → `docker compose up -d --wait` run is green, or `Local stack: N/A` is recorded with its reason), every in-scope AC-ID has fresh passing evidence produced against that running stack, the full test suite (unit + integration + e2e) is green, and the last slice's demo checkpoint is accepted by the user. The pipeline encodes only checks already proven green locally, against the same pinned images. Local dev tooling (`docker-compose.yml`, dev Dockerfile, seed and reset scripts, git hooks, lint config) is not CI/CD.

Task-type skill routing (Phase 1):
- **Metric optimization** ("make it faster", "improve the score", tune a measurable number) → implementor dispatched with the `autoresearch` skill: immutable evaluator, one atomic mutation per experiment, keep/discard by metric, every attempt logged.
- **UI tasks** → the coordinator names the aesthetic explicitly (e.g., "premium SaaS", "minimalist editorial") so ui-ux-designer and frontend-dev apply the same `design-styles` preset; the aesthetic name is passed through both dispatches.

## Pipeline Profiles (Phase 0)

Before any analysis, the coordinator triages the task: a documentation adequacy check (an authoritative user spec or existing code pattern is never re-derived — downstream documents reference it and add a thin delta brief), a prior-art scan (prefer translating an existing in-repo pattern over designing fresh), and a 0–2 score on five questions (files > 10; novel pattern; no authoritative spec; irreversible/prod-risk; parallelizable). Sum: **0–2 → Micro · 3–5 → Standard · 6+ → Full**. Any non-zero irreversible/prod-risk score forces at least Standard; greenfield is always Full.

| Profile | When | Pipeline |
|---|---|---|
| **Micro** | ≤~3 files, spec clear, pattern exists | one implementation agent + 1 code review. No PRD, architecture, plan, debate, or `docs/progress.md`. |
| **Standard** | modular feature, mostly known territory | thin delta brief (ordinary doc-review only, no debate) → slices → per slice: tester + dev + 1 code review. |
| **Full** | large / greenfield / ambiguous / high-risk | the complete workflow below, including the adversarial debate gate. |

Externally grounded facts (endpoint hosts, config shapes, contracts, real IDs) and irreversible decisions are collected into one batched blocking-questions gate: verified against the authoritative source or asked of the user before any dispatch. Cost circuit-breaker thresholds: **Micro/Standard: 8 runs; Full: 40 runs** (or 3× planned-slices × 5, whichever is lower). A per-slice sub-breaker stops any slice exceeding 6 implementation dispatches.

The local-stack gate is profile-independent: a Micro task that touches a database, queue, mail, or storage dependency is still verified against the containerized stack; only an empty infrastructure inventory exempts it, recorded as `Local stack: N/A — <reason>`. It does not mean an extra dispatch per task: when a `docker-compose*.yml` already covers the whole inventory, the gate is satisfied by evidence — `docker compose up -d --wait` plus `docker compose ps`, recorded — and `devops-engineer` is dispatched only when the stack is missing, incomplete, or unhealthy.

## Gates

| Gate | Scope | Blocks | Satisfied by |
|---|---|---|---|
| local-stack gate (enablement) | project | slice 1 and shared scaffolding | devops-engineer's clean-state proof, or a recorded `Local stack: N/A` |
| DoD gate | slice N | slice N+1 | slice AC tests green against the stack + code review DONE + demo checkpoint |
| criteria coverage check (Phase 4 step 1) | all AC-IDs | CI/CD dispatch | every AC-ID has passing non-mock evidence, or is listed UNVERIFIED |
| local-proof gate (Phase 2 action 5) | whole task | CI/CD dispatch | all four conjuncts recorded in the ledger |

The local-stack gate is the first conjunct of the local-proof gate, not a parallel mechanism: the local-proof gate reads the stack proof from the ledger before it looks at AC evidence, the full suite, or the final demo. The gate carries two obligations — **enablement**, the stack proven healthy from a clean state before there is an app to run against it, and **proof**, every later verification (slice acceptance tests, Mode B suites, criteria coverage) executed against that running stack rather than a substitute.

## Full Workflow (Greenfield)

```mermaid
flowchart TD
    START([User Request]) --> P0["Phase 0: Triage & profile"]
    P0 --> PROF{Profile?}
    PROF -- "Micro / Standard" --> LEAN["Lean pipeline<br/>(see Pipeline Profiles)"]
    LEAN --> LEANREP([Report])
    PROF -- "Full" --> P1

    subgraph P1["Phase 1: Analysis"]
        A1[Parse task & detect stack]
        A1b["Input inventory:<br/>user briefs, prototypes, brand"]
        A2[Identify agents & decompose subtasks]
        A3[Present plan to user]
        A1 --> A1b --> A2 --> A3
    end

    P1 --> CONFIRM{User confirms?}
    CONFIRM -- No --> P1
    CONFIRM -- Yes --> LEDGER[Create docs/progress.md]
    LEDGER --> P2

    subgraph P2["Phase 2: Dispatch & Inline Review"]
        direction TB

        subgraph DOC_PHASE["Documentation Phase"]
            direction TB

            PA[product-analyst] -->|docs/prd.md with AC-IDs| DEBATE_DEPTH{"Debate depth?<br/>Light / Standard / Deep"}
            DEBATE_DEPTH -- Light --> DR1
            DEBATE_DEPTH -- "Standard / Deep" --> ADV1["PRD challenge<br/>depth-proportional cycles"]
            ADV1 -->|Consensus or arbitration| DR1
            subgraph DR1["Doc Review: PRD"]
                DR1_R[doc-reviewer]
                DR1_D{Concerns?}
                DR1_R --> DR1_D
                DR1_D -- Yes --> DR1_FIX[re-dispatch product-analyst]
                DR1_FIX -->|recheck, max 2 reworks| DR1_R
                DR1_D -- No --> DR1_OK
            end

            DR1 --> PAR_DOCS

            subgraph PAR_DOCS["Parallel: Architecture + Design"]
                direction LR
                ARCH[architect<br/>docs/architecture.md]
                UI["ui-ux-designer<br/>docs/design.md<br/>(if UI involved)"]
            end

            PAR_DOCS --> REVIEW_DOCS{"Novel?"}
            REVIEW_DOCS -- "Yes" --> DR2["doc-reviewer:<br/>architecture + design<br/>(max 1 rework each)"]
            REVIEW_DOCS -- "No (routine)" --> DR2_SKIP["Review skipped"]
            DR2 --> PL
            DR2_SKIP --> PL

            PL[planner]
            PL -->|docs/plan.md: vertical slices| DEBATE_DEPTH2{"Debate depth?"}
            DEBATE_DEPTH2 -- Light --> DR4
            DEBATE_DEPTH2 -- "Standard / Deep" --> ADV4["Plan challenge<br/>depth-proportional cycles"]
            ADV4 -->|Consensus or arbitration| DR4
            subgraph DR4["Doc Review: Plan"]
                DR4_R[doc-reviewer]
                DR4_D{Concerns?}
                DR4_R --> DR4_D
                DR4_D -- Yes --> DR4_FIX[re-dispatch planner]
                DR4_FIX -->|recheck, max 2 reworks| DR4_R
                DR4_D -- No --> DR4_OK
            end
        end

        DOC_PHASE --> INFRA

        subgraph INFRA["Local Stack Enablement"]
            DEV["devops-engineer: docker-compose.yml, .env.example,<br/>seed and reset scripts, emulators where no real service runs locally<br/>(pinned image tags + a health check per service)"] --> CRI
            subgraph CRI["Infra Review: Local Stack"]
                CRI_R[code-reviewer]
                CRI_D{Concerns?}
                CRI_R --> CRI_D
                CRI_D -- Yes --> CRI_FIX[re-dispatch devops-engineer]
                CRI_FIX --> CRI_OK["Stack proven healthy from clean<br/>or Local stack: N/A recorded"]
                CRI_D -- No --> CRI_OK
            end
        end

        INFRA --> SCAFFOLD

        subgraph SCAFFOLD["Shared Scaffolding"]
            IMP["implementor: skeleton, config, shared types<br/>(the local stack already exists — read-only for implementor;<br/>no CI/CD — pipelines and deploy come last)"] --> CR1
            subgraph CR1["Code Review: Scaffold"]
                CR1_R[code-reviewer]
                CR1_D{Concerns?}
                CR1_R --> CR1_D
                CR1_D -- Yes --> CR1_FIX[re-dispatch implementor]
                CR1_FIX --> CR1_OK[Scaffold ready]
                CR1_D -- No --> CR1_OK
            end
        end

        SCAFFOLD --> SLICE_LOOP

        subgraph SLICE_LOOP["Per Slice (tracer bullet first)"]
            direction TB
            STACKUP["docker compose up -d --wait<br/>all services healthy"]
            STACKUP --> OQGATE
            OQGATE{"OQ gate: questions tagged<br/>'before Slice N' answered?"}
            OQGATE -- No --> ASKOQ["Ask user in one batch<br/>or record MVP waiver"]
            ASKOQ --> OQGATE
            OQGATE -- Yes --> TA
            TA["tester Mode A: failing acceptance tests<br/>(expected-red per AC-ID)<br/>Collapse A+B if ≤3 AC-IDs + existing harness"] --> SCOPE_CHECK["Mode A scope check:<br/>flag future-slice tests as expected-red"]
            SCOPE_CHECK --> PARALLEL

            subgraph PARALLEL["Parallel Implementation (disjoint scopes)"]
                direction LR
                BE[backend-dev] 
                FE[frontend-dev]
            end

            PARALLEL --> TB2["tester Mode B: full suite (unit + integration + e2e)<br/>green against containers,<br/>extend coverage, update docs/test-plan.md"]
            TB2 --> CRS
            subgraph CRS["Code Review: Slice"]
                CRS_R[code-reviewer]
                CRS_D{Concerns?}
                CRS_R --> CRS_D
                CRS_D -- Yes --> CRS_FIX[re-dispatch responsible agent]
                CRS_FIX --> CRS_OK[Slice done]
                CRS_D -- No --> CRS_OK
            end
            CRS --> GATE{"DoD gate: slice AC tests pass end-to-end<br/>against the running stack + review DONE?"}
            GATE -- Yes --> DEMO["Demo checkpoint:<br/>show increment to user"]
            DEMO --> NEXT_SLICE[Next slice]
            GATE -- No --> FIX[re-dispatch within rework limits]
            FIX --> TB2
        end

        SLICE_LOOP --> CICD["CI/CD — devops-engineer (always last)<br/>local-proof gate: local stack healthy from clean,<br/>all AC-IDs verified against containers,<br/>full suite green, final demo accepted"]
    end

    P2 --> P3

    subgraph P3["Phase 3: Collection"]
        C0["Evidence gate: scope-proportional<br/>In-scope red → DONE_WITH_CONCERNS<br/>Out-of-scope red → accept DONE"]
        C1[Process agent reports, update docs/progress.md]
        C2{All DONE?}
        C0 --> C1 --> C2
        C2 -- "BLOCKED / NEEDS_CONTEXT" --> C3[Re-dispatch with info]
        C3 --> C1
        C2 -- Yes --> C4[Proceed]
    end

    P3 --> P4

    subgraph P4["Phase 4: Final Review"]
        direction TB
        F0["Criteria coverage check:<br/>every AC-ID has passing evidence<br/>or is listed UNVERIFIED"]
        F0 --> F1{Multiple code agents?}
        F1 -- Yes --> F2[code-reviewer: cross-cutting review + test integrity]
        F2 --> F2D{Concerns?}
        F2D -- Yes --> F2FIX[re-dispatch code agent]
        F2FIX --> F3
        F2D -- No --> F3
        F1 -- No --> F3

        F3{Docs created?}
        F3 -- Yes --> F4[doc-reviewer: cross-doc consistency]
        F4 --> F4D{Concerns?}
        F4D -- Yes --> F4FIX[re-dispatch doc agent]
        F4FIX --> F5[Review complete]
        F4D -- No --> F5
        F3 -- No --> F5
    end

    P4 --> P5

    subgraph P5["Phase 5: Report"]
        R1[Compile summary]
        R2["AC-IDs verified N/M + files changed<br/>+ test evidence + concerns"]
        R3[Link docs/progress.md + next steps]
        R1 --> R2 --> R3
    end

    P5 --> DONE([Done])
```

## Adversarial Debate Loop

This loop runs only in the Full profile (and in `/ask-prd`, `/ask-planner`); Micro and Standard use zero debate cycles. Debate depth is proportional to artifact complexity: **Light** (<5 AC-IDs, no external integrations) skips debate entirely; **Standard** (5–15 AC-IDs) allows 1 cycle; **Deep** (15+ AC-IDs with integrations/irreversibility) uses the full 3-cycle budget. The PRD and execution plan use this gate before downstream work. On the consensus path, the artifact then enters ordinary document review. After an unresolved third recheck, the combined arbitration/full-review dispatch replaces that ordinary review; it is not followed by a duplicate review. The creator remains the only writer. The read-only challenger reports stable `CH-*` items with severity, affected requirement or slice, counter-scenario, evidence, impact, and required resolution. The creator records one disposition for every item: `accepted_and_fixed`, `rejected_with_evidence`, or `needs_decision`.
This workflow applies adversarial planning as risk-oriented challenge, not literal competition: trade-off analysis replaces zero-sum scoring; a qualitative maximin check tests the worst plausible outcome; contingency branches are allowed only for high-impact uncertainty and must define a trigger, fallback, verification, and return point. Agents never hide intent. Assumptions, evidence, and residual risks make limited information explicit; likelihood, impact, and confidence stay categorical or `unknown`, never invented probabilities.

```mermaid
flowchart TD
    DRAFT["Creator writes PRD or plan"] --> CHALLENGE["adversarial-reviewer challenges artifact"]
    CHALLENGE --> VERDICT{"Debate verdict"}
    VERDICT -- CONSENSUS --> ORDINARY["Ordinary doc-review gate"]
    VERDICT -- REVISE before cycle 3 --> CREATOR["Creator updates same artifact<br/>and dispositions CH-* items"]
    CREATOR --> RECHECK["adversarial-reviewer rechecks<br/>carried CH-* items"]
    RECHECK --> VERDICT
    VERDICT -- ARBITRATION_REQUIRED after third recheck --> ARBITRATE["doc-reviewer arbitrates unresolved CH-*<br/>and performs the full review"]
    ARBITRATE --> RESULT{"doc-reviewer status"}
    RESULT -- NEEDS_CONTEXT --> USER["Ask user for decision"]
    USER --> CREATOR2["Creator updates artifact"]
    CREATOR2 --> CONFIRM["doc-reviewer resumes and verifies<br/>combined arbitration/full review"]
    CONFIRM --> RESULT
    RESULT -- DONE_WITH_CONCERNS --> REWORK2["Creator/reviewer rework loop<br/>maximum 2"]
    REWORK2 --> RESULT
    RESULT -- BLOCKED --> STOP["Stop; report blocker"]
    RESULT -- DONE with Evidence --> READY["Arbitrated and fully reviewed document<br/>ready for downstream agents"]
    ORDINARY --> ORESULT{"doc-reviewer status"}
    ORESULT -- DONE_WITH_CONCERNS --> OREWORK["Creator/reviewer rework loop<br/>maximum 2"]
    OREWORK --> ORESULT
    ORESULT -- NEEDS_CONTEXT --> OCONTEXT["Obtain context, then re-review"]
    OCONTEXT --> ORESULT
    ORESULT -- BLOCKED --> STOP
    ORESULT -- DONE with Evidence --> READY2["Consensus document passes ordinary review<br/>then becomes ready for downstream agents"]
```

One debate cycle consists of a creator response followed by a challenger recheck. The first challenge pass establishes the initial `CH-*` set. Rechecks carry those IDs forward; they may add an ID only when the revision creates a new defect. Consensus requires no open challenges, no `needs_decision` dispositions, and explicit treatment of residual risks.

Each dispatch includes the original request, artifact path and version, cycle number, unresolved `CH-*` items, latest dispositions and evidence, and related documents. The coordinator stores only the current cycle, debate verdict, and unresolved IDs in `docs/progress.md`; `/ask-prd` and `/ask-planner` retain the same state in their mini-orchestration context. No separate challenge artifact is created.

## Ordinary Review Loop

Artifacts without an adversarial gate, and PRDs/plans whose challenger reaches consensus, follow the ordinary review-and-rework pattern below. A cycle-3 combined arbitration/full-review result follows the same status discipline and rework limit, but substitutes for the ordinary PRD/plan review rather than preceding it. Only `DONE` with Evidence permits acceptance or downstream dispatch.

```mermaid
flowchart LR
    AGENT[Agent creates artifact] --> REVIEWER[Reviewer checks]
    REVIEWER --> STATUS{Report status and Evidence}
    STATUS -- DONE with Evidence --> PASS[Artifact accepted]
    STATUS -- DONE_WITH_CONCERNS or DONE without Evidence --> REWORK[Re-dispatch original agent\nwith all findings]
    REWORK -->|fewer than 2 reworks| REVIEWER
    REWORK -->|2 reworks exhausted| ESCALATE[Change strategy once or escalate]
    STATUS -- NEEDS_CONTEXT --> CONTEXT[Obtain missing context]
    CONTEXT --> REVIEWER
    STATUS -- BLOCKED --> STOP[Stop and report blocker]
    PASS --> NEXT[Continue workflow]
```

| Artifact type | Creator agents | Reviewer | Rework limit |
|---|---|---|---|
| PRD, consensus path | product-analyst | doc-reviewer ordinary review | 2 |
| PRD, unresolved after third recheck | product-analyst | doc-reviewer combined arbitration/full review; replaces ordinary review | 2 |
| Architecture | architect | doc-reviewer | 2 |
| Design spec | ui-ux-designer | doc-reviewer | 2 |
| Execution plan, consensus path | planner | doc-reviewer ordinary review | 2 |
| Execution plan, unresolved after third recheck | planner | doc-reviewer combined arbitration/full review; replaces ordinary review | 2 |
| Scaffold code | implementor | code-reviewer | 2 |
| Backend code | backend-dev | code-reviewer | 2 |
| Frontend code | frontend-dev | code-reviewer | 2 |
| Test code | tester | code-reviewer | 2 |

After 3 identical failure signatures: change strategy once (different agent, narrower scope, split the task) or escalate to the user with the full attempt history.

The budgets are independent: PRD/plan debate allows at most **3 debate cycles**. The consensus path then allows at most **2 creator rework dispatches** in ordinary doc-review. The cycle-3 path instead allows at most **2 creator reworks** while completing the combined arbitration/full review; that dispatch replaces ordinary review, so no second review budget is opened.

## Documentation Gate Roles

| Participant | Writes artifact | Responsibility |
|---|---:|---|
| product-analyst | Yes, PRD only | Defines traceable requirements, stable AC-IDs, assumptions, scope options, trade-offs, negative scenarios, decisions, and residual risks; maintains the OQ register with `Confirm before:` triggers and the Definition of Ready; marks sourceless requirements `invented — requires user confirmation`; resolves PRD challenges. Assigned AC-IDs are never renumbered or reused. |
| planner | Yes, plan only | Defines tracer-bullet-first vertical slices, complete AC-ID mapping, dependency and uncertainty registers, worst-case analysis, and bounded contingency branches; carries OQ triggers into the slices they gate, states the DoD gate, and plans an integration-enablement slice when the PRD names real integrations; schedules the infrastructure-enablement task before slice 1 and before shared scaffolding when the project has external runtime dependencies; resolves plan challenges. |
| adversarial-reviewer | No | Challenges assumptions and plausible failure scenarios in explicit `prd` or `plan` mode; returns the `Debate verdict` field with `CONSENSUS`, `REVISE`, or `ARBITRATION_REQUIRED`. |
| doc-reviewer | No | Checks completeness, consistency, and actionability; arbitrates unresolved `CH-*` items only after cycle 3. |
| coordinator or ask-* mini-orchestrator | No | Carries full debate context, enforces budgets, updates round state, and blocks downstream dispatch until the document passes both gates; collects the input inventory and enforces the OQ, DoD, and demo-checkpoint gates. |

`/ask-prd` and `/ask-planner` are exceptions to the usual direct-dispatch shortcut shape: each runs creator → adversarial debate, then either consensus plus ordinary doc-review or combined arbitration/full review after an unresolved third recheck. There is no `/ask-adversarial-reviewer` shortcut.

## Agent Dispatch Order

```mermaid
sequenceDiagram
    participant U as User
    participant C as Coordinator
    participant PA as product-analyst
    participant ADV as adversarial-reviewer
    participant DR as doc-reviewer
    participant AR as architect
    participant UD as ui-ux-designer
    participant PL as planner
    participant DO as devops-engineer
    participant IM as implementor
    participant CR as code-reviewer
    participant BE as backend-dev
    participant FE as frontend-dev
    participant TE as tester

    U->>C: Task request
    C->>U: Decomposition plan
    U->>C: Confirm
    Note over C: Create docs/progress.md

    rect rgb(230, 245, 255)
        Note over C,DR: Documentation Phase
        Note over C,U: Invented requirements and triggered OQs need user confirmation before dependent work
        C->>PA: Create PRD (AC-IDs)
        PA-->>C: docs/prd.md + Evidence
        C->>ADV: Initial PRD challenge (outside cycle budget)
        ADV-->>C: CONSENSUS or REVISE
        loop If REVISE: creator response + challenger recheck, maximum 3 cycles
            C->>PA: Resolve every CH-* item
            PA-->>C: Updated PRD + dispositions + Evidence
            C->>ADV: Recheck PRD (cycle state + unresolved CH-* items)
            ADV-->>C: CONSENSUS, REVISE before cycle 3, or ARBITRATION_REQUIRED only after cycle 3
        end
        alt Challenger reached CONSENSUS
            C->>DR: Ordinary PRD review
            DR-->>C: DONE or DONE_WITH_CONCERNS
            loop While concerns remain, maximum 2 ordinary reworks
                C->>PA: Fix PRD (all review findings attached)
                PA-->>C: Updated PRD + Evidence
                C->>DR: Recheck PRD
                DR-->>C: DONE or DONE_WITH_CONCERNS
            end
        else ARBITRATION_REQUIRED after third recheck
            C->>DR: Arbitrate CH-* items and review full PRD
            DR-->>C: DONE with Evidence, DONE_WITH_CONCERNS, NEEDS_CONTEXT, or BLOCKED
            alt NEEDS_CONTEXT: product intent or unavailable evidence
                C->>U: Request decision
                U-->>C: Decision
                C->>PA: Apply decision to PRD
                PA-->>C: Updated PRD + Evidence
                C->>DR: Resume and verify combined arbitration/full review
                DR-->>C: DONE with Evidence, DONE_WITH_CONCERNS, NEEDS_CONTEXT, or BLOCKED
            else DONE_WITH_CONCERNS
                loop Creator/reviewer rework, maximum 2
                    C->>PA: Fix arbitration/full-review concerns
                    PA-->>C: Updated PRD + Evidence
                    C->>DR: Resume combined arbitration/full review
                    DR-->>C: DONE with Evidence, DONE_WITH_CONCERNS, NEEDS_CONTEXT, or BLOCKED
                end
                Note over C,DR: After 2 concern reworks, change strategy or escalate
            else BLOCKED
                Note over C,DR: Stop — do not dispatch downstream
            else DONE with Evidence
                Note over C,DR: Combined gate passed — no duplicate ordinary review
            end
        end
        Note over C,AR: Architecture waits for consensus + ordinary review, or successful arbitration/full review

        C->>AR: Design architecture (read PRD)
        AR-->>C: docs/architecture.md + Evidence
        C->>DR: Review architecture
        DR-->>C: DONE or DONE_WITH_CONCERNS
        loop While concerns remain, maximum 2 ordinary reworks
            C->>AR: Fix architecture
            AR-->>C: docs/architecture.md updated + Evidence
            C->>DR: Recheck architecture
            DR-->>C: DONE or DONE_WITH_CONCERNS
        end

        C->>UD: Design UI/UX (read PRD)
        UD-->>C: docs/design.md + Evidence
        C->>DR: Review design
        DR-->>C: DONE or DONE_WITH_CONCERNS
        loop While concerns remain, maximum 2 ordinary reworks
            C->>UD: Fix design
            UD-->>C: docs/design.md updated + Evidence
            C->>DR: Recheck design
            DR-->>C: DONE or DONE_WITH_CONCERNS
        end

        C->>PL: Create slice plan (read architecture)
        PL-->>C: docs/plan.md (vertical slices) + Evidence
        C->>ADV: Initial plan challenge (outside cycle budget)
        ADV-->>C: CONSENSUS or REVISE
        loop If REVISE: creator response + challenger recheck, maximum 3 cycles
            C->>PL: Resolve every CH-* item
            PL-->>C: Updated plan + dispositions + Evidence
            C->>ADV: Recheck plan (cycle state + unresolved CH-* items)
            ADV-->>C: CONSENSUS, REVISE before cycle 3, or ARBITRATION_REQUIRED only after cycle 3
        end
        alt Challenger reached CONSENSUS
            C->>DR: Ordinary plan review
            DR-->>C: DONE or DONE_WITH_CONCERNS
            loop While concerns remain, maximum 2 ordinary reworks
                C->>PL: Fix plan (all review findings attached)
                PL-->>C: Updated plan + Evidence
                C->>DR: Recheck plan
                DR-->>C: DONE or DONE_WITH_CONCERNS
            end
        else ARBITRATION_REQUIRED after third recheck
            C->>DR: Arbitrate CH-* items and review full plan
            DR-->>C: DONE with Evidence, DONE_WITH_CONCERNS, NEEDS_CONTEXT, or BLOCKED
            alt NEEDS_CONTEXT: product intent or unavailable evidence
                C->>U: Request decision
                U-->>C: Decision
                C->>PL: Apply decision to plan
                PL-->>C: Updated plan + Evidence
                C->>DR: Resume and verify combined arbitration/full review
                DR-->>C: DONE with Evidence, DONE_WITH_CONCERNS, NEEDS_CONTEXT, or BLOCKED
            else DONE_WITH_CONCERNS
                loop Creator/reviewer rework, maximum 2
                    C->>PL: Fix arbitration/full-review concerns
                    PL-->>C: Updated plan + Evidence
                    C->>DR: Resume combined arbitration/full review
                    DR-->>C: DONE with Evidence, DONE_WITH_CONCERNS, NEEDS_CONTEXT, or BLOCKED
                end
                Note over C,DR: After 2 concern reworks, change strategy or escalate
            else BLOCKED
                Note over C,DR: Stop — do not dispatch downstream
            else DONE with Evidence
                Note over C,DR: Combined gate passed — no duplicate ordinary review
            end
        end
        Note over C,IM: Implementation waits for consensus + ordinary review, or successful arbitration/full review
    end

    rect rgb(230, 255, 230)
        Note over C,CR: Implementation — per slice, tracer bullet first
        Note over C,DO: Local stack enablement — before any scaffolding or slice
        C->>DO: Stand up the containerized dependencies (inventory rows, pinned tags, health checks)
        DO-->>C: docker-compose.yml, .env.example, seed/reset + Evidence (down -v, up -d --wait, ps healthy — twice from clean)
        C->>CR: Review infrastructure (pins, health checks, named volumes, ports, no production credentials)
        CR-->>C: DONE or DONE_WITH_CONCERNS
        Note over C,DO: Empty inventory instead records "Local stack: N/A — reason"
        C->>IM: Scaffold project (shared skeleton, local stack read-only)
        IM-->>C: Files created + Evidence
        C->>CR: Review scaffold
        CR-->>C: DONE or DONE_WITH_CONCERNS

        loop Each slice
            C->>U: OQ gate — questions tagged "before Slice N" in one batch
            U-->>C: Answers or explicit MVP waiver (recorded in docs/progress.md)
            C->>TE: Mode A — failing acceptance tests for slice AC-IDs
            TE-->>C: expected-red evidence

            par Backend & Frontend (disjoint scopes)
                C->>BE: Build API (make acceptance tests green)
                BE-->>C: Files + Evidence (build/lint/test output)
            and
                C->>FE: Build UI (make acceptance tests green)
                FE-->>C: Files + Evidence (build/lint/test + E2E)
            end

            C->>TE: Mode B — full suite green, extend coverage
            TE-->>C: Green run evidence + docs/test-plan.md
            C->>CR: Review slice (incl. test integrity)
            CR-->>C: DONE or DONE_WITH_CONCERNS
            C->>U: Demo checkpoint — run instructions and slice increment
            U-->>C: Feedback (design/requirement changes go through the owning doc agent first)
            Note over C: DoD gate — slice AC tests pass against the running stack + review DONE + demo before next slice
        end

        opt CI/CD (always last)
            Note over C: Local-proof gate — local stack healthy from clean, every AC-ID verified against that stack, full suite (unit + integration + e2e) green, final demo accepted
            C->>DO: CI/CD setup (pipeline encodes only locally-green checks, same pinned images)
            DO-->>C: Files + Evidence (local green run + pipeline config)
            C->>CR: Review CI/CD config
            CR-->>C: DONE or DONE_WITH_CONCERNS
        end
    end

    rect rgb(255, 245, 230)
        Note over C,DR: Final Review
        Note over C: Criteria coverage: every AC-ID verified or listed UNVERIFIED
        opt Multiple code agents
            C->>CR: Cross-cutting code review
            CR-->>C: DONE or DONE_WITH_CONCERNS
        end
        opt Docs created
            C->>DR: Cross-document consistency
            DR-->>C: DONE or DONE_WITH_CONCERNS
        end
    end

    C->>U: Final report (AC-IDs N/M verified, evidence, progress ledger)
```

## Status Handling

Canonical report statuses remain `DONE`, `DONE_WITH_CONCERNS`, `BLOCKED`, and `NEEDS_CONTEXT`. `Debate verdict` is an agent-specific field, not a new public status. For `adversarial-reviewer`, `DONE` is valid only with `Debate verdict: CONSENSUS` and file:line Evidence.

```mermaid
stateDiagram-v2
    [*] --> AgentWorking

    AgentWorking --> EvidenceCheck: Report received
    EvidenceCheck --> DebateCheck: Challenge report with Evidence
    EvidenceCheck --> DONE: Status DONE, Evidence present, checks green
    EvidenceCheck --> Rework: DONE_WITH_CONCERNS or DONE without Evidence
    EvidenceCheck --> BlockedState: Status BLOCKED
    EvidenceCheck --> ContextState: Status NEEDS_CONTEXT

    DebateCheck --> OrdinaryDocReview: CONSENSUS and Evidence
    DebateCheck --> CreatorRevision: REVISE and cycle fewer than 3
    CreatorRevision --> DebateCheck: Creator dispositions plus challenger recheck
    DebateCheck --> Arbitration: ARBITRATION_REQUIRED after third recheck
    Arbitration --> DONE: Combined review returns DONE with Evidence
    Arbitration --> Rework: DONE_WITH_CONCERNS or DONE without Evidence
    Arbitration --> UserDecision: NEEDS_CONTEXT for product intent or unavailable evidence
    Arbitration --> BlockedState: BLOCKED
    UserDecision --> Arbitration: Non-material answer, creator update, resume combined review
    UserDecision --> DebateCheck: Material scope change, new version and initial pass
    OrdinaryDocReview --> DONE: Ordinary review returns DONE with Evidence
    OrdinaryDocReview --> Rework: DONE_WITH_CONCERNS or DONE without Evidence
    OrdinaryDocReview --> ContextState: NEEDS_CONTEXT
    OrdinaryDocReview --> BlockedState: BLOCKED

    DONE --> NextPhase: Record in docs/progress.md
    Rework --> ReviewerRecheck: Creator updates artifact
    ReviewerRecheck --> DONE: Reviewer returns DONE with Evidence
    ReviewerRecheck --> Rework: Concerns remain and reworks fewer than 2
    ReviewerRecheck --> ChangeStrategy: Concerns remain after 2 reworks
    ReviewerRecheck --> ContextState: NEEDS_CONTEXT
    ReviewerRecheck --> BlockedState: BLOCKED
    ChangeStrategy --> EscalateToUser: Change strategy once or escalate

    BlockedState --> ReDispatch: Blocker can be resolved
    BlockedState --> EscalateToUser: Blocker cannot be resolved
    ReDispatch --> AgentWorking: Within applicable budget
    ReDispatch --> EscalateToUser: Repeated failure limit reached
    ContextState --> AnswerQuestions
    AnswerQuestions --> AgentWorking: Re-dispatch with answers
    AnswerQuestions --> AskUser: Cannot answer
    AskUser --> AgentWorking: User provides context

    NextPhase --> [*]
    EscalateToUser --> [*]
```

## Session Continuity

The `/handoff` skill generates `docs/handoff.md` — a compact session-continuity snapshot capturing the resume point (phase, slice, debate state), artifact states, environment, pending user decisions, and verbal decisions not yet in docs. The ledger's session state carries the local-stack line — `up` / `down` / `N/A` with the command and result of the last healthy verification — so a resumed session knows whether the containers must be brought up before it can verify anything. The `/resume` skill reads the handoff document (or reconstructs state from `docs/progress.md`), validates consistency against the ledger and git history, and continues from the exact next action. The handoff is a convenience snapshot; `docs/progress.md` remains the authority.
