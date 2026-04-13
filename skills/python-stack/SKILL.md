---
name: Python Stack Knowledge
description: >
  This skill should be used when working with Python projects,
  including frameworks like Django, Flask, FastAPI, and related tooling.
metadata:
  priority: 7
  pathPatterns:
    - "**/*.py"
    - "**/pyproject.toml"
    - "**/setup.py"
    - "**/setup.cfg"
    - "**/requirements*.txt"
    - "**/Pipfile"
    - "**/manage.py"
    - "**/wsgi.py"
    - "**/asgi.py"
    - "**/conftest.py"
    - "**/pytest.ini"
    - "**/tox.ini"
    - "**/.flake8"
    - "**/mypy.ini"
    - "**/ruff.toml"
  bashPatterns:
    - "python *"
    - "python3 *"
    - "pip *"
    - "poetry *"
    - "uv *"
    - "pytest *"
    - "django-admin *"
    - "manage.py *"
    - "flask *"
    - "uvicorn *"
    - "gunicorn *"
  importPatterns:
    - "django"
    - "flask"
    - "fastapi"
    - "sqlalchemy"
    - "pydantic"
    - "celery"
    - "pytest"
  promptSignals:
    phrases:
      - "python"
      - "django"
      - "flask"
      - "fastapi"
      - "pytest"
    allOf:
      - ["python", "project"]
      - ["django", "views"]
      - ["flask", "blueprint"]
    noneOf:
      - "typescript only"
      - "node.js only"
      - "react"
    minScore: 6
---

# Python Stack Knowledge

## Project Structure Conventions

### Django
- `manage.py` — entry point
- `<project>/settings.py` — configuration (or `settings/` package for env-based)
- `<app>/models.py` — ORM models
- `<app>/views.py` — views (function-based or class-based)
- `<app>/urls.py` — URL routing
- `<app>/serializers.py` — DRF serializers
- `<app>/admin.py` — admin configuration
- `<app>/tests/` or `<app>/tests.py` — tests
- `<app>/migrations/` — auto-generated, do not edit manually

### Flask
- `app/` or project root — application package
- `app/__init__.py` — app factory (`create_app()`)
- `app/routes/` or `app/views/` — blueprint routes
- `app/models.py` — SQLAlchemy models
- `app/extensions.py` — extension instances (db, migrate, login)
- `app/templates/` — Jinja2 templates
- `tests/` — test directory

### FastAPI
- `app/main.py` — FastAPI instance and startup
- `app/routers/` — route modules (`APIRouter`)
- `app/models/` — SQLAlchemy/Tortoise models
- `app/schemas/` — Pydantic schemas (request/response)
- `app/dependencies.py` — dependency injection
- `app/services/` — business logic
- `tests/` — test directory

## Python Patterns

- Use type hints everywhere: `def func(name: str) -> dict[str, Any]:`
- Prefer `pathlib.Path` over `os.path`
- Use dataclasses or Pydantic for structured data
- Use `with` statement for resource management (files, connections)
- Use `logging` module, not `print()` for debugging

## Testing (pytest)

- File naming: `test_*.py` or `*_test.py`
- Use `conftest.py` for shared fixtures
- Fixtures with `@pytest.fixture`, parametrize with `@pytest.mark.parametrize`
- Django: use `@pytest.mark.django_db` for database access
- Flask: use `app.test_client()` or `pytest-flask`
- FastAPI: use `TestClient` from `starlette.testclient`
- Mock with `unittest.mock.patch` or `pytest-mock`

## Error Handling

- Use specific exceptions, not bare `except:`
- Custom exceptions: inherit from domain-specific base exception
- Django: use `Http404`, `PermissionDenied`, DRF exception classes
- FastAPI: use `HTTPException` with appropriate status codes
- Always log exceptions with traceback: `logger.exception("message")`

## Security

- Never dynamically execute user-provided strings as code
- Django: use ORM queries, never raw SQL with string formatting
- Always validate and sanitize user input
- Use `secrets` module for tokens, not `random`
- Environment variables for secrets via `os.environ`

## Common Anti-Patterns

- Don't use mutable default arguments: `def func(items=[])` — use `def func(items=None):`
- Don't catch broad exceptions: `except Exception:` — be specific
- Don't use `import *` — use explicit imports
- Don't put business logic in views — use services layer
- Don't ignore migration conflicts — resolve them

## Additional Resources

For framework-specific patterns, consult:
- **`references/django-patterns.md`** — Django views, models, DRF, migrations
- **`references/flask-patterns.md`** — Flask blueprints, extensions, app factory
- **`references/testing-patterns.md`** — pytest fixtures, mocking, parametrize
