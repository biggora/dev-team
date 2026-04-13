Отлично, теперь могу дать полную картину.

---

## 1. Механизм добавления агентов

Каждый агент — это один `.md` файл в `agents/`. Claude Code обнаруживает их автоматически. Структура файла:

```
┌─────────────────────────────────────────┐
│  YAML frontmatter (между ---)          │
│  ├── name        (идентификатор)       │
│  ├── description (когда trigger-ить)   │
│  ├── model       (sonnet/opus/haiku)   │
│  ├── color       (цвет в UI)          │
│  └── tools       (доступные tools)     │
├─────────────────────────────────────────┤
│  System prompt (тело markdown)         │
│  ├── Role & responsibilities           │
│  ├── Process steps                     │
│  ├── Quality standards                 │
│  └── Report protocol                   │
└─────────────────────────────────────────┘
```

**Как агент получает знания** — через два независимых канала:

1. **System prompt** (вшит в файл агента) — базовая экспертиза, роль, процесс
2. **Skills** (инжектируются динамически) — глубокие знания по технологиям, которые приходят **только когда агент работает с соответствующими файлами**

Это ключевое разделение: агент знает *как работать*, а скилл даёт *чем работать*.

---

## 2. Специализированные команды — да, это возможно

Есть два подхода, и они комбинируются:

### Подход A: Универсальные агенты + специализированные скиллы

```
agents/
├── implementor.md      # Универсальный имплементатор
├── code-reviewer.md    # Универсальный ревьюер
└── tester.md           # Универсальный тестировщик

skills/
├── nodejs-knowledge/
│   ├── SKILL.md        # pathPatterns: ["**/*.ts", "**/*.js", "**/package.json"]
│   └── references/
│       ├── nest-patterns.md
│       ├── next-patterns.md
│       └── vite-patterns.md
├── python-knowledge/
│   ├── SKILL.md        # pathPatterns: ["**/*.py", "**/requirements.txt"]
│   └── references/
│       ├── django-patterns.md
│       └── flask-patterns.md
```

Агент `implementor` работает с `.ts` файлами → автоматически получает `nodejs-knowledge`. Работает с `.py` → получает `python-knowledge`. Один агент, разные знания в зависимости от контекста.

### Подход B: Специализированные агенты + специализированные скиллы

```
agents/
├── node-implementor.md     # tools: Read, Write, Edit, Grep, Glob, Bash
├── node-reviewer.md        # tools: Read, Grep, Glob
├── python-implementor.md   # tools: Read, Write, Edit, Grep, Glob, Bash
├── python-reviewer.md      # tools: Read, Grep, Glob
└── code-reviewer.md        # Универсальный (fallback)

skills/
├── nextjs/
│   └── SKILL.md            # pathPatterns: ["**/next.config.*", "**/app/**/*.tsx"]
├── nestjs/
│   └── SKILL.md            # pathPatterns: ["**/*.module.ts", "**/*.controller.ts"]
├── django/
│   └── SKILL.md            # pathPatterns: ["**/views.py", "**/models.py", "**/urls.py"]
```

Каждый агент уже содержит базовые знания стека в system prompt, а скиллы добавляют фреймворк-специфичную экспертизу.

### Подход C (рекомендую): Гибрид — универсальные роли + скиллы-команды

```
agents/
├── implementor.md          # Универсальный, full tools
├── code-reviewer.md        # Универсальный, read-only
├── tester.md               # Универсальный, full tools
└── planner.md              # Универсальный, read-only

skills/
├── nodejs-stack/
│   ├── SKILL.md            # Базовые паттерны Node.js
│   │   pathPatterns: ["**/*.ts", "**/*.js", "**/*.mjs"]
│   │   importPatterns: ["express", "fastify", "koa"]
│   │   promptSignals.phrases: ["node", "typescript", "npm"]
│   └── references/
│       ├── next-app-router.md
│       ├── nest-modules.md
│       ├── vite-config.md
│       └── testing-vitest.md
│
├── python-stack/
│   ├── SKILL.md            # Базовые паттерны Python
│   │   pathPatterns: ["**/*.py", "**/pyproject.toml"]
│   │   importPatterns: ["django", "flask", "fastapi"]
│   │   promptSignals.phrases: ["python", "django", "flask"]
│   └── references/
│       ├── django-views.md
│       ├── flask-blueprints.md
│       └── testing-pytest.md
```

**Как это работает в runtime:**

```
Пользователь: /dev-team Добавить API endpoint для user registration

Координатор (Phase 1 — Analysis):
  → git status, Glob → видит **/*.ts, nest-cli.json
  → Определяет: NestJS проект, нужен implementor

Координатор (Phase 2 — Dispatch):
  → Agent(implementor, prompt="Создай endpoint... scope: src/users/...")
  
  Implementor получает чистый контекст
    → Читает src/users/*.controller.ts
    → pathPattern "**/*.controller.ts" срабатывает
    → skills/nestjs/SKILL.md автоматически инжектируется
    → Агент теперь знает NestJS паттерны (декораторы, pipes, guards)
    → Имплементирует по паттернам проекта
```

**Координатор НЕ получает скиллы**, потому что он не читает `.ts` файлы и не запускает `npm`. Изоляция сохраняется.

### Как координатор знает, какого агента вызвать?

Координатор определяет стек через легковесный анализ:
- `Glob("**/package.json")` → Node.js проект
- `Glob("**/pyproject.toml")` или `Glob("**/requirements.txt")` → Python проект
- `Glob("**/next.config.*")` → Next.js
- `Glob("**/nest-cli.json")` → NestJS

При подходе C координатор всегда вызывает `implementor`, а скиллы сами определяют, какие знания инжектировать на основе файлов, которые агент читает.

---

Если хотите, могу реализовать конкретный стек (например Node.js/Next/Nest с набором скиллов и агентами implementor + tester), чтобы было от чего отталкиваться?