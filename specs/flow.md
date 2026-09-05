> **NOTE (2026-07)** — this historical walkthrough predates the evidence-gate and adversarial-planning revisions. It does not describe the mandatory PRD/plan creator → `adversarial-reviewer` debate, cycle-3 arbitration, or the later ordinary document review. The `brainstorming`/`writing-plans`/`using-superpowers` skills mentioned below were removed, the report protocol now requires an `Evidence` field, the planner produces vertical slices, and the tester runs in Mode A (red) / Mode B (green). For current behavior see `specs/workflow.md` and `CLAUDE.md`.

## Процесс разработки приложения с нуля через `/dev-team`

### Шаг 0: Твой промпт

```
/dev-team Создать SaaS task-manager.
Next.js 16, NestJS бэкенд, PostgreSQL.
Авторизация, дашборд, CRUD задач.
Эстетика: premium SaaS, минималистичный.
```

---

### Phase 1: Analysis (координатор)

Координатор сканирует проект:

```
Glob("**/package.json")     → нет
Glob("**/tsconfig*.json")   → нет
Glob("**/*.ts")             → нет
```

**Greenfield detected.** Координатор строит цепочку:

```
architect → ui-ux-designer → planner → devops-engineer → implementor → [backend-dev, frontend-dev] → tester → code-reviewer
```

Показывает тебе план и спрашивает подтверждение.

---

### Phase 2a: Architect (opus, Write)

Координатор dispatch:
> *"Design the architecture for a SaaS task manager. NestJS backend, Next.js 16 frontend, PostgreSQL. Read references/architecture-patterns.md for Node.js/TypeScript architecture patterns. Design using NestJS module architecture for backend and Next.js App Router for frontend. Apply brainstorming to explore design alternatives. Use writing-plans for structured implementation blueprints. Save your architecture blueprint to docs/architecture.md"*

**Архитектор:**
1. Читает `references/architecture-patterns.md`
2. Применяет скилл `brainstorming` — исследует альтернативы (монолит vs модульный, REST vs GraphQL)
3. Применяет скилл `writing-plans` — оформляет blueprint
4. **Сохраняет `docs/architecture.md`** — компоненты, data model, API контракты, файловая структура, порядок сборки

```
Status: DONE
Files changed: docs/architecture.md
Summary: 6 модулей NestJS, Next.js App Router, 4 сущности PostgreSQL
```

---

### Phase 2b: UI/UX Designer (sonnet, Write)

Координатор dispatch:
> *"Design the UI for this SaaS task manager. Read docs/architecture.md for the architecture blueprint. Apply premium frontend design principles. Aesthetic: premium SaaS, minimalist. Include a color palette with hex values and ASCII wireframes for each screen. Save your design specification to docs/design.md"*

**Дизайнер:**
1. Читает `docs/architecture.md` — понимает какие экраны нужны
2. Применяет скилл `design-taste-frontend` — premium параметрика
3. Создаёт user flows: регистрация → логин → дашборд → CRUD задач
4. Рисует ASCII wireframes для каждого экрана
5. Составляет цветовую палитру (hex-таблица)
6. **Сохраняет `docs/design.md`**

```
Status: DONE
Files changed: docs/design.md
Summary: 5 экранов, 14 цветов в палитре, wireframes для всех страниц
```

**Ты смотришь `docs/design.md`** — видишь wireframes и палитру. Если не нравится — говоришь координатору, он re-dispatch дизайнера (максимум 2 попытки, потом спросит тебя).

---

### Phase 2c: Planner (opus, Write)

Координатор dispatch:
> *"Decompose the task manager project into subtasks. Read docs/architecture.md for the architecture blueprint. Read docs/design.md for the design specification. Apply brainstorming before decomposition. Use writing-plans for structured execution plans. Save your execution plan to docs/plan.md"*

**Планер:**
1. Читает `docs/architecture.md` + `docs/design.md`
2. Применяет `brainstorming` — ищет оптимальный порядок сборки
3. Применяет `writing-plans` — оформляет план
4. **Сохраняет `docs/plan.md`** — подзадачи, зависимости, scope, агенты

```
Subtask 1: [devops-engineer] Локальный стек — docker-compose (PostgreSQL, mailpit),
           пинованные теги, health checks, .env.example, seed
Subtask 2: [implementor] Scaffolding — package.json, tsconfig, dirs
Subtask 3: [implementor] Shared types — src/shared/types/, src/shared/config/
Subtask 4: [backend-dev] Auth module — JWT, guards, user entity      ← параллельно
Subtask 5: [backend-dev] Task module — CRUD endpoints, task entity   ← параллельно
Subtask 6: [frontend-dev] Shell layout — nav, sidebar (по wireframes)← параллельно
Subtask 7: [frontend-dev] Auth pages — login, register               ← параллельно
Subtask 8: [frontend-dev] Dashboard + Task UI                        ← после 4,5,6
Subtask 9: [tester] E2E тесты
Subtask 10: [code-reviewer] Финальный ревью
```

**CI/CD last**: пайплайны, деплой и release в план не входят — они не были запрошены. Если бы входили, планер обязан поставить их отдельной финальной подзадачей после Subtask 10, владелец — `devops-engineer`, с предусловием local-proof gate из четырёх конъюнктов: локальный стек поднят с нуля и здоров (`docker compose down -v` → `up -d --wait` зелёный) либо записано `Local stack: N/A`; каждый AC подтверждён свежими доказательствами, полученными **против этого запущенного стека**; полный набор тестов (unit + integration + e2e) зелёный; финальное demo принято пользователем. Пайплайн кодирует только проверки, доказанные зелёными локально.

```
Status: DONE
Files changed: docs/plan.md
Summary: 10 подзадач, 4 фазы: локальный стек → scaffolding → parallel dev → test+review
```

---

### Phase 2d: DevOps Engineer — Локальный стек (sonnet)

Координатор dispatch (из `docs/plan.md`, subtask 1):
> *"Stand up the local stack for this project. Read docs/architecture.md, section 'Local runtime topology'. Infrastructure inventory: PostgreSQL (primary datastore), mailpit (SMTP capture for the registration flow). Produce docker-compose.yml with pinned image tags, a health check per service and deterministic host ports, plus .env.example and seed/reset scripts. Prove with `docker compose down -v` → `docker compose up -d --wait` → `docker compose ps` healthy, twice from clean. Scope: docker-compose.yml, .env.example, scripts/. Keywords: containerized dependencies, local stack, health check."*

**DevOps-инженер:**
1. Читает `docs/architecture.md` — раздел «Local runtime topology»
2. Пишет `docker-compose.yml`: `postgres:16-alpine` и `axllent/mailpit:v1.20`, health check на каждый сервис, именованные тома, фиксированные host-порты
3. Заполняет `.env.example` — каждая переменная с безопасным дефолтом и однострочным комментарием
4. Добавляет идемпотентный seed и скрипт reset
5. Дважды поднимает стек с нуля и подтверждает здоровье сервисов

```
Status: DONE
Files changed: docker-compose.yml, .env.example, scripts/seed.sql, scripts/reset.sh
Evidence:
  docker compose config -q            → 0
  docker compose down -v              → 0
  docker compose up -d --wait         → 0 (18s)
  docker compose ps                   → postgres (healthy), mailpit (healthy)
  psql -c 'select 1' / curl :8025     → 0 / 0
  повтор с нуля: down -v → 0 · up -d --wait → 0 (17s) · ps → оба (healthy)
```

**Ни один слайс и ни один scaffolding не стартует, пока этот шаг не отчитался DONE** — либо пока в `docs/progress.md` не записано `Local stack: N/A — <причина>`.

---

### Phase 2e: Implementor — Scaffolding (sonnet)

Координатор dispatch (из `docs/plan.md`, subtasks 2+3):
> *"Scaffold the project and create shared files. Read docs/architecture.md for the file structure. This is a Node.js TypeScript project using Next.js and NestJS. Create: package.json, tsconfig, directory structure, shared types and config files. The local stack — docker-compose.yml, .env.example, seed and reset scripts — already exists from the previous phase and is read-only for you: read it for host ports and env-var names, do not edit it. Scope: project root, src/shared/"*

**Implementor:**
1. Применяет `brainstorming` — оценивает структуру
2. Создаёт scaffold: package.json, tsconfig, конфиги, директории
3. Создаёт shared types в `src/shared/` — **эти файлы теперь принадлежат ему, не параллельным агентам**

```
Status: DONE
Files changed: package.json, tsconfig.json, src/shared/types/...
```

---

### Phase 2f: Параллельный dispatch (4 агента одновременно)

Координатор проверяет: **scope не пересекается** (shared files уже созданы implementor-ом). Инфраструктурные файлы — `docker-compose.yml`, `.env.example`, seed- и reset-скрипты — принадлежат devops-engineer: параллельные агенты их только читают (порты, имена переменных), но никогда не правят.

Один message — 4 Agent tool calls:

**backend-dev #1** (auth):
> *"Build the authentication module. Read docs/architecture.md for the blueprint. Work with TypeScript controllers and services in this NestJS project. Scope: src/backend/auth/. Do NOT touch src/shared/ or frontend files."*

**backend-dev #2** (tasks):
> *"Build the task CRUD module. Read docs/architecture.md. Work with TypeScript controllers and services in this NestJS project. Scope: src/backend/tasks/."*

**frontend-dev #1** (shell):
> *"Build the app shell layout. Read docs/design.md for wireframes and color palette. Use provided hex colors as authoritative source. Work with React components and TypeScript in this Next.js project. Scope: src/frontend/components/layout/"*

**frontend-dev #2** (auth pages):
> *"Build login and registration pages. Read docs/design.md for wireframes and color palette. Work with React components and TypeScript in this Next.js project. Scope: src/frontend/app/(auth)/"*

Все 4 агента работают параллельно. Каждый получает:
- Stack-specific фразы → injection скиллов (`next-best-practices`, `nest-best-practices`, `typescript-expert`)
- Ссылку на docs/ вместо вставки текста в промпт
- Чёткий scope — никаких пересечений

---

### Phase 2g: Frontend-dev #3 — Dashboard (после backend)

Координатор ждёт backend-dev. Получает отчёты: API endpoints готовы. Dispatch:

> *"Build the dashboard and task management UI. Read docs/design.md for wireframes and palette. Backend API: POST /tasks, GET /tasks, PATCH /tasks/:id, DELETE /tasks/:id (from backend-dev reports). Work with React components and TypeScript in this Next.js project. Scope: src/frontend/app/(dashboard)/"*

Frontend-dev #3 получает **API контракты от backend** — handoff через координатор.

---

### Phase 3: Collection

Координатор читает все отчёты:

| Агент | Status | Действие |
|-------|--------|----------|
| backend-dev #1 | DONE | Записать результат |
| backend-dev #2 | DONE_WITH_CONCERNS | Оценить concerns |
| frontend-dev #1 | DONE | Записать |
| frontend-dev #2 | BLOCKED | Дать недостающую инфу, re-dispatch (**макс. 2 попытки**) |
| frontend-dev #3 | DONE | Записать |

Если агент BLOCKED 2 раза → координатор **спрашивает тебя**, а не зацикливается.

---

### Phase 2h: Tester (sonnet)

Координатор dispatch:
> *"Write and run tests for this TypeScript/Node.js project using Vitest and Playwright. Read docs/design.md for user flows to use as test scenarios. Files changed: [полный список от всех агентов]. Test the auth flow (register → login → access dashboard) and task CRUD (create → read → update → delete). This is a Next.js 16 / NestJS 11 / TypeScript 5.8 project."*

**Тестер:**
1. **Читает `docs/design.md`** — user flows становятся test scenarios
2. Применяет скиллы: `playwright-cli`, `next-best-practices`, `nest-best-practices`, `typescript-expert`
3. Пишет тесты и запускает их

```
Status: DONE
Files changed: tests/auth.spec.ts, tests/tasks.spec.ts, tests/e2e/...
Tests: 24 passed, 0 failed
```

---

### Phase 4: Code Reviewer (sonnet)

Координатор dispatch:
> *"Review this TypeScript 5.8 / Next.js 16.2 / NestJS 11.0 code for correctness and modern patterns. Files changed: [полный список]. Original task: SaaS task manager. next.js, nestjs, typescript, tailwindcss, postgresql."*

**Ревьюер:**
1. **Читает `package.json`** — проверяет версии (шаг 1 процесса)
2. Применяет скиллы: `next-best-practices` (v16), `nest-best-practices`, `typescript-expert`, `code-review`, `security-review`
3. Ревьюит **против правильных версий** — v16 паттерны не помечаются как ошибки

```
Status: DONE_WITH_CONCERNS
Concerns:
- Important (85): Missing rate limiting on auth endpoints
- Suggestion (78): Consider 'use cache' directive instead of fetch revalidation
```

---

### Phase 5: Report

Координатор тебе:

```
Task: SaaS task manager
Stack: Next.js 16.2, NestJS 11.0, TypeScript 5.8, PostgreSQL

What was done:
- Architecture: 6 modules (docs/architecture.md)
- Design: 5 screens with wireframes and palette (docs/design.md)
- Plan: 10 subtasks in 4 phases (docs/plan.md)
- Local stack: postgres + mailpit, healthy from clean twice (docker-compose.yml)
- Backend: Auth + Task modules (12 files)
- Frontend: Shell + Auth + Dashboard (18 files)
- Tests: 24 passed, 0 failed

Review findings:
- ⚠️ Missing rate limiting on auth (Important)
- 💡 Use 'use cache' directive (Suggestion)

Next steps:
- npm run dev
- Review docs/design.md and docs/architecture.md
- Address rate limiting concern
```

---

### Визуально (после всех изменений)

```
Ты: /dev-team "Создать task manager..."
         │
    ┌────▼─────────┐
    │ Координатор   │ Phase 1: Analysis
    │ stack detect  │ → greenfield detected
    │ versions read │ → Next.js 16, TS 5.8, NestJS 11
    └────┬─────────┘
         │
    ┌────▼─────┐
    │ Architect │ → docs/architecture.md     ← brainstorming + writing-plans
    └────┬─────┘
         │
    ┌────▼──────────┐
    │ UI/UX Designer │ → docs/design.md      ← design-taste-frontend
    └────┬──────────┘                          палитра + wireframes
         │
    ┌────▼────┐
    │ Planner │ → docs/plan.md               ← читает оба docs/
    └────┬────┘
         │
    ┌────▼───────────────┐
    │ DevOps Engineer    │ docker-compose + .env.example + seed
    └────┬───────────────┘ ← gate: без DONE слайсы не стартуют
         │
    ┌────▼──────────┐
    │ Implementor   │ scaffolding + shared files
    └────┬──────────┘   стек читает, но не правит
         │
         │  scope изоляция: shared files уже созданы
         │
    ┌────┼────────────────────────┐
    ▼    ▼                        ▼
 backend-dev ×2            frontend-dev ×2    ← параллельно
  (auth, tasks)          (shell, auth pages)    без пересечений
    │    │                        │
    └────┤    handoff: API контракты
         │                        │
    ┌────▼──────────┐             │
    │ frontend-dev  │ dashboard ──┘    ← получает API от backend
    └────┬──────────┘
         │
    ┌────▼───┐
    │ Tester │ читает docs/design.md       ← user flows = test scenarios
    └────┬───┘ next/nest/ts скиллы
         │
    ┌────▼─────────────┐
    │ Code Reviewer    │ читает package.json ← version-aware
    └────┬─────────────┘ next/nest/ts скиллы
         │
    ┌────▼─────────┐
    │ Report → тебе │
    └──────────────┘

Документация остаётся в проекте:
  docs/architecture.md
  docs/design.md
  docs/plan.md
```

### Ключевые отличия от прежней версии

| Было | Стало |
|------|-------|
| Дизайнер не в greenfield flow | Дизайнер между architect и planner |
| Артефакты терялись в контексте | Сохраняются в `docs/` |
| Handoff = вставка текста в промпт | Handoff = "Read docs/architecture.md" |
| Параллельные агенты могли конфликтовать | Shared files → implementor первым, scope изоляция |
| docker-compose и CI/CD делал implementor | Инфраструктура — эксклюзивный writable scope devops-engineer; остальные агенты её только читают |
| Слайсы стартовали без запущенных зависимостей | Локальный стек поднимается до scaffolding; без DONE (или `Local stack: N/A`) слайсы не стартуют |
| Re-dispatch мог зациклиться | Максимум 2 попытки → эскалация пользователю |
| Тестер не знал user flows | Тестер читает `docs/design.md` |
| Ревьюер не знал версий | Ревьюер читает package.json + получает version-aware скиллы |
| Универсальный координатор слабый | Stack detection, greenfield, versions, skill injection |
