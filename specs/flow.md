Теперь у меня полная картина. Вот как выглядит идеальный процесс разработки с нуля:

---

## Разработка приложения с нуля через `/dev-team`

### Этап 0: Твой промпт

Ты пишешь одну команду, например:
```
/dev-team Создать SaaS-приложение для управления задачами. 
Next.js 16, NestJS бэкенд, PostgreSQL. 
Авторизация, дашборд с задачами, CRUD задач.
Эстетика: premium SaaS, минималистичный.
```

Координатор всё остальное делает сам.

---

### Этап 1: Analysis (координатор)

Координатор сканирует проект через `Glob`. Видит пустую директорию → **greenfield detection**. Решает запустить цепочку:

```
architect → planner → [implementors] → tester → code-reviewer
```

Спрашивает у тебя подтверждение плана.

---

### Этап 2: Architect (read-only, opus)

Координатор отправляет архитектору задачу с инструкцией прочитать `references/architecture-patterns.md`.

**Архитектор выдаёт:**
- Компоненты системы (auth module, task module, user module...)
- Интерфейсы между ними (API контракты)
- Data model (entities, relationships)
- Файловая структура (какие папки, какие файлы)
- Порядок сборки (что строить первым)

```
Status: DONE
Summary: 6 модулей, NestJS монолит, Next.js App Router, 4 сущности в БД
```

---

### Этап 3: UI/UX Designer (read-only, sonnet)

Параллельно с архитектором (или после — зависит от задачи) координатор отправляет дизайнеру.

**Дизайнер выдаёт:**
- Цветовую палитру (таблица hex-цветов)
- User flow (регистрация → логин → дашборд → создание задачи)
- ASCII wireframe для каждого экрана
- Состояния компонентов, a11y требования

```
Status: DONE
Summary: 5 экранов, палитра из 14 цветов, wireframes для всех страниц
```

**Ты смотришь на wireframes и палитру** — если не нравится, говоришь координатору переделать.

---

### Этап 4: Planner (read-only, opus)

Получает архитектуру + дизайн-спецификацию. Декомпозирует на конкретные подзадачи:

```
1. [implementor] Scaffolding: package.json, tsconfig, next.config, docker-compose
2. [backend-dev] Auth module: JWT, guards, user entity, registration/login endpoints
3. [backend-dev] Task module: CRUD endpoints, task entity, relations
4. [frontend-dev] Layout: навигация, sidebar, responsive shell (по wireframes дизайнера)
5. [frontend-dev] Auth pages: login, register (по wireframes + палитре)
6. [frontend-dev] Dashboard + task CRUD UI (по wireframes + палитре)
7. [tester] E2E тесты: auth flow, task CRUD
```

Указывает что параллельно (2+3, 4+5+6), что последовательно (1 → всё остальное).

---

### Этап 5: Dispatch (координатор)

Координатор запускает агентов по плану планера:

**Сначала** — `implementor` для scaffolding (один).

**Потом параллельно:**
- `backend-dev` × 2 (auth + tasks) — со stack-specific фразами "NestJS", "TypeScript"
- `frontend-dev` × 3 (layout + auth pages + dashboard) — с полной дизайн-спецификацией (wireframes + hex-цвета)

Каждый агент получает **изолированный промпт** с полным контекстом: что уже сделано, какие файлы трогать, какие нет.

---

### Этап 6: Tester (sonnet)

После реализации координатор отправляет тестировщику:
- Список всех изменённых файлов
- Что должно работать (user flows от дизайнера)
- Какой тест-раннер использовать

Тестер пишет и запускает тесты.

---

### Этап 7: Code Reviewer (sonnet)

Ревьюер получает:
- Все изменённые файлы
- **Точные версии** из package.json: "Next.js 16.2, TypeScript 5.8, NestJS 11"
- Stack-specific фразы для injection скиллов

Ревьюит код против правильных версий.

---

### Этап 8: Report (координатор)

Тебе приходит финальный отчёт:
- Что сделано
- Какие файлы созданы
- Результаты тестов
- Замечания ревьюера
- Следующие шаги (`npm run dev`, что проверить)

---

### Визуально

```
Ты: /dev-team "Создать task manager..."
         │
    ┌────▼─────┐
    │Координатор│ ← Phase 1: Analysis (greenfield detected)
    └────┬─────┘
         │
    ┌────▼─────┐
    │ Architect │ ← архитектура, data model, файловая структура
    └────┬─────┘
         │
    ┌────▼──────────┐
    │ UI/UX Designer │ ← палитра, wireframes, user flows
    └────┬──────────┘
         │
    ┌────▼────┐
    │ Planner │ ← декомпозиция на подзадачи
    └────┬────┘
         │
    ┌────▼─────┐
    │Implementor│ ← scaffolding
    └────┬─────┘
         │
    ┌────┼──────────────────┐
    ▼    ▼                  ▼
backend-dev ×2       frontend-dev ×3    ← параллельно
 (auth, tasks)    (layout, pages, UI)
    │    │                  │
    └────┼──────────────────┘
         │
    ┌────▼───┐
    │ Tester │ ← E2E тесты
    └────┬───┘
         │
    ┌────▼────────┐
    │Code Reviewer│ ← ревью с version-aware скиллами
    └────┬────────┘
         │
    ┌────▼─────┐
    │  Report  │ → тебе
    └──────────┘
```

Главное — **ты можешь вмешаться после любого этапа**. Координатор спрашивает подтверждение после Phase 1, и ты видишь результаты каждого агента.