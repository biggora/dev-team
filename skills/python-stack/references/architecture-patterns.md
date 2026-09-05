# Python Architecture Patterns

## Django Application Architecture

### Project Structure
```
project/
├── manage.py
├── config/                        # Project configuration
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py               # Shared settings
│   │   ├── development.py        # Dev overrides
│   │   └── production.py         # Prod overrides
│   ├── urls.py                   # Root URL configuration
│   ├── wsgi.py
│   └── asgi.py
├── apps/                          # Application modules
│   ├── users/
│   │   ├── __init__.py
│   │   ├── models.py             # User model
│   │   ├── views.py              # Views or ViewSets
│   │   ├── serializers.py        # DRF serializers
│   │   ├── urls.py               # App URL patterns
│   │   ├── admin.py              # Admin configuration
│   │   ├── services.py           # Business logic (service layer)
│   │   ├── selectors.py          # Complex queries
│   │   ├── tests/
│   │   │   ├── test_models.py
│   │   │   ├── test_views.py
│   │   │   └── test_services.py
│   │   └── migrations/
│   ├── [feature]/                 # Each feature = Django app
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── services.py
│   │   ├── selectors.py
│   │   └── urls.py
│   └── common/                    # Shared utilities
│       ├── models.py             # Abstract base models (TimeStampedModel)
│       ├── permissions.py
│       └── pagination.py
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
└── templates/                     # Global templates (if needed)
```

### Key Architectural Patterns

**Service Layer**: Keep views thin. Business logic lives in `services.py`. Views handle HTTP, services handle domain logic.

```python
# views.py — thin, delegates to service
class UserViewSet(viewsets.ModelViewSet):
    def perform_create(self, serializer):
        user_service.create_user(**serializer.validated_data)

# services.py — business logic
def create_user(*, email: str, name: str) -> User:
    user = User.objects.create(email=email, name=name)
    send_welcome_email(user)
    return user
```

**Selectors Pattern**: Complex queries in `selectors.py`, not in views or services.

**Fat Models, Thin Views**: Model methods for data logic, views only for request/response handling.

**Signals**: Use sparingly for cross-cutting concerns (audit logs, cache invalidation). Prefer explicit service calls.

### Django REST Framework Architecture

- **ViewSets + Routers**: Auto-generate URL patterns from ViewSets
- **Serializers**: Validate input, serialize output. Nested serializers for relations.
- **Permissions**: Custom permission classes per view/action
- **Filtering**: django-filter for querystring-based filtering

---

## Flask Application Architecture

### Application Factory Pattern
```
project/
├── app/
│   ├── __init__.py               # create_app() factory
│   ├── extensions.py             # db, migrate, login, mail instances
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── [entity].py
│   ├── routes/                    # Blueprints
│   │   ├── __init__.py
│   │   ├── auth.py               # auth_bp = Blueprint('auth', ...)
│   │   ├── api.py
│   │   └── [feature].py
│   ├── services/                  # Business logic
│   │   └── [feature]_service.py
│   ├── schemas/                   # Marshmallow schemas
│   │   └── [entity]_schema.py
│   └── templates/
├── config.py                      # Configuration classes
├── tests/
│   ├── conftest.py               # Fixtures (app, client, db)
│   ├── test_auth.py
│   └── test_[feature].py
└── migrations/                    # Alembic migrations
```

### Key Patterns

**Application Factory**: `create_app()` function that configures and returns the Flask app. Enables testing with different configs.

**Blueprints**: Each feature is a Blueprint. Register in factory.

**Extensions**: Initialize without app, then `init_app()` in factory.

---

## FastAPI Application Architecture

### Structure
```
project/
├── app/
│   ├── __init__.py
│   ├── main.py                   # FastAPI instance, lifespan, middleware
│   ├── core/
│   │   ├── config.py             # Settings (pydantic BaseSettings)
│   │   ├── security.py           # JWT, password hashing
│   │   └── database.py           # SQLAlchemy engine, session
│   ├── models/                    # SQLAlchemy models
│   │   ├── base.py               # Declarative base
│   │   └── [entity].py
│   ├── schemas/                   # Pydantic schemas
│   │   └── [entity].py           # Create, Update, Response schemas
│   ├── routers/                   # API routes
│   │   ├── __init__.py
│   │   └── [feature].py          # APIRouter per feature
│   ├── services/                  # Business logic
│   │   └── [feature].py
│   └── dependencies.py           # Shared Depends() functions
├── tests/
│   ├── conftest.py
│   └── test_[feature].py
├── alembic/                       # Database migrations
└── alembic.ini
```

### Key Patterns

**Dependency Injection**: Use `Depends()` for database sessions, auth, permissions. Composable and testable.

**Pydantic Schemas**: Separate schemas for Create, Update, Response. Use `model_config` for ORM mode.

**Async by Default**: Use `async def` for route handlers. Use async database drivers (asyncpg, aiomysql).

---

## Cross-Cutting Architecture

### Authentication
- **Django**: django-allauth or DRF TokenAuthentication / JWT (djangorestframework-simplejwt)
- **Flask**: Flask-Login (session) or Flask-JWT-Extended
- **FastAPI**: OAuth2PasswordBearer + JWT, custom Depends()

### Database Migrations
- **Django**: Built-in (`makemigrations` / `migrate`). Auto-generated from model changes.
- **Flask/FastAPI**: Alembic (`alembic revision --autogenerate` / `alembic upgrade head`)

### Task Queues
- **Celery**: Works with all frameworks. Redis/RabbitMQ broker. Use `@shared_task`.
- **Django-Q2**: Django-specific alternative.
- **ARQ**: Async task queue for FastAPI.

### Caching
- **Django**: Built-in cache framework (Redis backend)
- **Flask**: Flask-Caching
- **FastAPI**: fastapi-cache2 or manual Redis

### Testing Strategy
- Unit tests: services and models (fast, no HTTP)
- Integration tests: API endpoints (TestClient/test_client, real database)
- The real database is a container from the project's `docker-compose.yml` — `docker compose up -d --wait`, healthcheck-gated, pinned image tag; never an ad-hoc local install or a mock
- The test session connects through env vars (`DATABASE_URL` or `POSTGRES_*`) pointing at that container
- Per-test isolation: transaction rollback around each test (preferred), otherwise truncate-and-reseed between tests
- Fixtures: shared test data in conftest.py
- See the `local-stack` skill for compose recipes, healthchecks, and reset strategies
