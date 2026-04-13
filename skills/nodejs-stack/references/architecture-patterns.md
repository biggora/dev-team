# Node.js / TypeScript Architecture Patterns

## NestJS Application Architecture

### Module-Based Structure (Bounded Contexts)
```
src/
├── app.module.ts                  # Root module — imports all feature modules
├── main.ts                        # Bootstrap (NestFactory.create)
├── common/                        # Shared utilities
│   ├── decorators/
│   ├── filters/
│   ├── guards/
│   ├── interceptors/
│   └── pipes/
├── config/                        # Configuration module
│   ├── config.module.ts
│   └── config.service.ts
├── auth/                          # Auth bounded context
│   ├── auth.module.ts
│   ├── auth.controller.ts
│   ├── auth.service.ts
│   ├── strategies/               # Passport strategies
│   ├── guards/                   # Auth guards
│   └── dto/
├── users/                         # Users bounded context
│   ├── users.module.ts
│   ├── users.controller.ts
│   ├── users.service.ts
│   ├── entities/
│   └── dto/
└── [feature]/                     # Each feature = module
    ├── [feature].module.ts
    ├── [feature].controller.ts
    ├── [feature].service.ts
    ├── entities/
    ├── dto/
    └── interfaces/
```

### Key Architectural Patterns

**Dependency Injection**: All services are `@Injectable()`. Inject via constructor. Use custom providers for complex setup.

**Module Boundaries**: Each module encapsulates its own controllers, services, entities. Export only what other modules need.

**Guard/Interceptor Pipeline**:
```
Request → Guards → Interceptors (before) → Pipes → Handler → Interceptors (after) → Response
```

**CQRS Pattern** (for complex domains):
- Commands: write operations (CreateUserCommand)
- Queries: read operations (GetUserQuery)
- Events: side effects (UserCreatedEvent)

**Repository Pattern**: Separate data access from business logic. Use TypeORM/Prisma repositories.

### Database Integration
- **TypeORM**: Decorator-based entities, migrations via CLI
- **Prisma**: Schema-first, auto-generated client, migrations via `prisma migrate`
- **MikroORM**: Unit of work pattern, identity map

---

## Next.js Application Architecture

### App Router Structure
```
app/
├── layout.tsx                     # Root layout (html, body, providers)
├── page.tsx                       # Home page
├── loading.tsx                    # Loading UI
├── error.tsx                      # Error boundary
├── not-found.tsx                  # 404 page
├── (auth)/                        # Route group (no URL segment)
│   ├── login/page.tsx
│   └── register/page.tsx
├── (dashboard)/                   # Route group
│   ├── layout.tsx                # Dashboard layout
│   └── [workspaceId]/
│       ├── page.tsx
│       └── settings/page.tsx
├── api/                           # Route handlers
│   └── [resource]/route.ts
components/                        # Shared components
├── ui/                            # Primitive UI components
└── [feature]/                     # Feature-specific components
lib/                               # Shared utilities
├── db.ts                          # Database client
├── auth.ts                        # Auth utilities
└── utils.ts
```

### Key Architectural Decisions

**Server vs Client Components**:
- Default: Server Components (data fetching, no interactivity)
- `"use client"`: Only for interactivity (onClick, useState, useEffect)
- Keep client boundary as low in the tree as possible

**Data Fetching**: Use Server Components with `async/await` directly. Cache with `unstable_cache` or React `cache()`.

**Server Actions**: Use `"use server"` for mutations. Place in separate files for reusability.

**Route Handlers** (`route.ts`): For webhook endpoints, third-party API integration, non-UI responses.

---

## Monorepo Architecture (Turborepo)

```
apps/
├── web/                           # Next.js frontend
├── api/                           # NestJS backend
└── admin/                         # Admin panel
packages/
├── ui/                            # Shared component library
├── config-eslint/                 # Shared ESLint config
├── config-typescript/             # Shared tsconfig
├── database/                      # Prisma schema + client
└── types/                         # Shared TypeScript types
```

---

## API Design Patterns

**REST**: Resource-based URLs, HTTP methods, status codes. Use DTOs for validation.

**GraphQL**: Schema-first or code-first. Use resolvers per entity. DataLoader for N+1.

**WebSocket**: Gateway pattern (NestJS `@WebSocketGateway`). Event-based communication.

## Authentication Architecture

- **JWT**: Access token (short-lived) + Refresh token (long-lived, httpOnly cookie)
- **Session**: Server-side session store (Redis). Use for SSR apps.
- **OAuth2**: Passport strategies. Store provider tokens securely.

## Error Handling Architecture

- Global exception filter for consistent error responses
- Domain-specific exceptions extending base HttpException
- Error serialization: `{ statusCode, message, error, timestamp, path }`
