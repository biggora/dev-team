# План реализации dev-team плагина

## Контекст

Создаём Claude Code плагин **dev-team** на основе спецификации `specs/dev-team-architecture.md`.

**Проблема**: при глобальной установке скиллов они загружаются в контекст всех агентов, расходуя контекстное окно.

**Решение**: кастомный плагин с архитектурой "координатор + специалисты" — координатор лёгкий (не читает файлы проекта), специалисты получают изолированный контекст и только релевантные скиллы через паттерн-маппинг.

**Реализуемый уровень**: Уровень 2 (Plugin + Skills) — знания вынесены в skills/ с динамической инъекцией.

---

## Целевая структура

```
dev-team/
├── .claude-plugin/
│   └── plugin.json                    # Манифест плагина
├── commands/
│   └── dev-team.md                    # Координатор (/dev-team) — 5-фазный workflow
├── agents/
│   ├── _template.md                   # Шаблон для создания новых агентов
│   └── code-reviewer.md              # Ревьюер (read-only, sonnet, red)
├── skills/
│   └── _template/
│       ├── SKILL.md                   # Шаблон скилла с полным примером metadata
│       └── references/
│           └── _template.md           # Шаблон reference-файла
├── CLAUDE.md                          # Инструкции плагина
├── specs/                             # (существующая) Спецификации
│   ├── dev-team-architecture.md
│   └── dev-team-architecture-plan.md  # (этот файл)
├── package.json                       # (существующий)
├── .gitignore                         # (существующий)
└── README.md                          # (существующий)
```

---

## Детальный план по файлам

### Файл 1: `.claude-plugin/plugin.json`

**Назначение**: Манифест плагина — точка входа для автообнаружения.

```json
{
  "name": "dev-team",
  "description": "Framework for specialized development agents with isolated contexts",
  "version": "1.0.0",
  "author": {
    "name": "Aleksejs Gordejevs"
  }
}
```

**Решения**:
- Явные пути к директориям (`agents`, `commands`, `skills`) НЕ указываем — Claude Code использует auto-discovery по стандартным директориям
- Версия, автор — из существующего `package.json`

---

### Файл 2: `CLAUDE.md`

**Назначение**: Инструкции плагина, видимые всем агентам в рамках плагина.

**Содержание**:
- Описание архитектуры (координатор + специалисты, изоляция контекста)
- **Протокол отчёта** — формат структурированного отчёта субагентов:
  ```
  Status: DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
  Files changed: [список]
  Summary: [что сделано]
  Tests: [тесты и результат]
  Concerns: [если DONE_WITH_CONCERNS]
  Blocked on: [если BLOCKED]
  Questions: [если NEEDS_CONTEXT]
  ```
- Правила dispatch для координатора (полный контекст, scope, параллельность)
- Правила для агентов (работать в scope, следовать протоколу, не гадать если blocked)
- Инструкции по добавлению новых агентов и скиллов

---

### Файл 3: `commands/dev-team.md` — Координатор

**Назначение**: Slash command `/dev-team` — лёгкий оркестратор, который НЕ пишет код сам.

**Frontmatter**:
```yaml
---
description: Координирует работу специализированных агентов для разработки
argument-hint: Описание задачи или фичи
allowed-tools: Bash(git status), Bash(git diff:*), Bash(git log:*), Read, Glob, Grep
---
```

**5-фазный workflow**:

| Фаза | Goal | Действия |
|------|------|----------|
| 1. Анализ | Понять задачу | Парсить $ARGUMENTS, определить тип работы, git status + Glob для структуры (НЕ читать исходники), выбрать агентов, декомпозировать, показать план пользователю |
| 2. Dispatch | Запустить агентов | Для каждой подзадачи: полный текст задачи + scope + контекст + шаблон протокола отчёта. Независимые → параллельно (несколько Agent calls в одном сообщении) |
| 3. Сбор | Обработать результаты | DONE → дальше. DONE_WITH_CONCERNS → оценить concerns. BLOCKED → предоставить info и перезапустить. NEEDS_CONTEXT → ответить или спросить user |
| 4. Ревью | Code review | Если были изменения кода → dispatch code-reviewer. Обработать findings. Если нужны фиксы → dispatch агента |
| 5. Отчёт | Сводка | Задача, что сделано, файлы, тесты, findings ревью, concerns, next steps |

**Ключевые принципы dispatch** (включаются прямо в текст команды):
- Вставлять **полный текст задачи** — агент не видит контекст координатора
- Указывать **scope boundaries** — какие файлы/директории можно менять
- Включать **контекст** от других агентов
- Требовать **шаблон протокола отчёта** в каждом промпте
- Независимые задачи → **несколько Agent tool calls в одном сообщении**

---

### Файл 4: `agents/code-reviewer.md`

**Назначение**: Read-only ревьюер кода с confidence scoring.

**Frontmatter**:
```yaml
---
name: code-reviewer
description: |
  Use this agent when code changes need review for quality, bugs, and project conventions.
  Read-only — cannot modify files.

  <example>
  Context: Development task completed, needs quality verification
  user: "Review the authentication changes for bugs and code quality"
  assistant: "I'll dispatch the code-reviewer agent to analyze the changes."
  <commentary>Code changes need review, trigger read-only code-reviewer.</commentary>
  </example>

  <example>
  Context: Coordinator in Phase 4 needs implementation verification
  user: "Check all modified files in this task"
  assistant: "I'll use the code-reviewer agent for thorough review."
  <commentary>Post-implementation review, code-reviewer validates quality.</commentary>
  </example>

  <example>
  Context: User wants security audit of existing code
  user: "Review src/auth/ for potential security issues"
  assistant: "I'll launch code-reviewer to analyze that directory."
  <commentary>Explicit review request for specific area.</commentary>
  </example>
model: sonnet
color: red
tools: Read, Grep, Glob
---
```

**System prompt**:
- Роль: senior code reviewer, read-only access
- Обязанности: project guidelines compliance, bug detection, code quality, architecture review
- Процесс: read files → check conventions (CLAUDE.md) → rate by confidence → group by severity
- Confidence scoring: 0-100, отчёт только при >= 75
- Severity: Critical / Important / Suggestion
- Встроенный протокол отчёта (Status: DONE | DONE_WITH_CONCERNS)

---

### Файл 5: `agents/_template.md`

**Назначение**: Самодокументирующий шаблон для создания новых агентов.

**Содержание**:
- YAML-комментарии с документацией всех полей
- Таблица role-based tool presets (Implementor, Reviewer, Planner, Tester, Researcher)
- Guidance по выбору модели (haiku/sonnet/opus/inherit)
- Placeholder frontmatter с `<example>` блоками
- Placeholder system prompt со структурой (Role, Responsibilities, Process, Quality, Output)
- Протокол отчёта в конце

---

### Файл 6: `skills/_template/SKILL.md`

**Назначение**: Шаблон скилла с полным примером всех metadata-полей.

**Frontmatter** (с YAML-комментариями):
```yaml
---
name: Skill Name Here
description: >
  This skill should be used when the user asks to
  "specific phrase 1", "specific phrase 2"
metadata:
  priority: 6
  pathPatterns:
    - "**/*.example"
  bashPatterns:
    - "example-command"
  importPatterns:
    - "example-package"
  promptSignals:
    phrases: ["example phrase"]
    allOf: [["word1", "word2"]]
    noneOf: ["unrelated topic"]
    minScore: 6
---
```

**Содержание**: Overview, Key Concepts, Workflow, Best Practices, Common Patterns, ссылки на references/

---

### Файл 7: `skills/_template/references/_template.md`

**Назначение**: Шаблон reference-файла для progressive disclosure.

**Содержание**: Overview, Detailed Patterns, Edge Cases, Troubleshooting table, Examples. HTML-комментарий объясняет когда использовать references vs SKILL.md.

---

## Порядок реализации

```
Шаг 1: Создать директории
  mkdir -p .claude-plugin commands agents skills/_template/references

Шаг 2: Создать файлы (параллельно где возможно)
  2a: .claude-plugin/plugin.json
  2b: CLAUDE.md
  
Шаг 3: Координатор (самый сложный файл)
  commands/dev-team.md

Шаг 4: Агенты (параллельно)
  4a: agents/code-reviewer.md
  4b: agents/_template.md

Шаг 5: Скиллы (параллельно)
  5a: skills/_template/SKILL.md
  5b: skills/_template/references/_template.md
```

---

## Ключевые проектные решения

| Вопрос | Решение | Обоснование |
|--------|---------|-------------|
| Формат tools в агентах | Comma-separated (`Read, Grep, Glob`) | Совпадает с feature-dev референсом |
| Модель code-reviewer | `sonnet` | Стандарт для review-задач по спецификации |
| Manifest paths | Без явных путей к директориям | Auto-discovery по умолчанию, проще |
| Шаблоны `_template` | В agents/ и skills/ | Следуем спецификации; placeholder-ы предотвращают ложные trigger-ы |
| Протокол отчёта | В 3 местах: coordinator, agent prompt, CLAUDE.md | Redundancy — агент увидит минимум одну копию |
| Координатор allowed-tools | `Bash(git status), Bash(git diff:*), Bash(git log:*), Read, Glob, Grep` | Координатор не должен модифицировать файлы — только чтение для анализа |

---

## Референсные реализации

| Компонент | Референс | Путь |
|-----------|----------|------|
| Координатор (command) | feature-dev | `~/.claude/plugins/.../feature-dev/commands/feature-dev.md` |
| Агент (code-reviewer) | feature-dev | `~/.claude/plugins/.../feature-dev/agents/code-reviewer.md` |
| Формат агента | plugin-dev agent-development | `~/.claude/plugins/.../plugin-dev/skills/agent-development/SKILL.md` |
| Формат скилла | plugin-dev skill-development | `~/.claude/plugins/.../plugin-dev/skills/skill-development/SKILL.md` |
| Параллельный dispatch | superpowers | `~/.claude/plugins/.../superpowers/skills/dispatching-parallel-agents/` |

---

## Верификация после реализации

| # | Проверка | Команда / Действие | Ожидаемый результат |
|---|----------|-------------------|---------------------|
| 1 | Структура файлов | `find . -name "*.md" -o -name "*.json" \| sort` | 7 новых файлов в правильных путях |
| 2 | Валидный JSON | `cat .claude-plugin/plugin.json \| python -m json.tool` | Корректный JSON |
| 3 | Frontmatter агентов | Просмотр agents/*.md | Корректный YAML: name, description, model, color |
| 4 | Frontmatter скиллов | Просмотр skills/*/SKILL.md | Корректный YAML: name, description, metadata |
| 5 | Команда доступна | Ввести `/dev-team test` в Claude Code после установки | Координатор запускается |
| 6 | Агент доступен | Claude предлагает code-reviewer | Агент в списке |
| 7 | Изоляция tools | Dispatch code-reviewer | Write/Edit НЕ доступны |
| 8 | Протокол отчёта | Dispatch любого агента | Ответ содержит Status: DONE/... |

---

## Риски и митигация

| Риск | Митигация |
|------|-----------|
| `_template.md` обнаруживается как реальный агент | Placeholder description не совпадёт с реальными запросами. При проблемах — перенести в `docs/` |
| `skills/_template/` обнаруживается как реальный скилл | Паттерны `**/*.example` не совпадут с реальными файлами |
| Координатор случайно читает исходники | `allowed-tools` ограничивает инструменты; инструкции явно запрещают |
| Агент не включает протокол отчёта | Протокол в 3 местах: system prompt агента, dispatch координатора, CLAUDE.md |
