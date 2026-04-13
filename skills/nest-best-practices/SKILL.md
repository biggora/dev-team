---
name: nest-best-practices
description: NestJS framework best practices and production patterns. Use whenever working with NestJS — creating modules, controllers, services, DTOs, guards, interceptors, pipes, middleware, or building REST/GraphQL/microservice APIs. Also use when setting up authentication, authorization, validation, queues, health checks, WebSockets, caching, or any @nestjs/* package. Even for simple NestJS tasks, this skill ensures correct import paths, proper decorator usage, and production-ready patterns. Covers NestJS v11 with Express v5, native JWT auth, Zod validation, Keyv caching, and Suites testing.
---

NestJS is a progressive Node.js framework for building efficient and scalable server-side applications. It uses TypeScript by default, supports both Express and Fastify, and provides an out-of-the-box application architecture inspired by Angular. NestJS combines elements of OOP, FP, and FRP, making it ideal for building enterprise-grade applications.

> Skill based on NestJS documentation, updated 2026-03-28. Covers NestJS v11 with Express v5.

## How to Use This Skill

When generating NestJS code, read the relevant reference files below for the specific topic. The references contain current API patterns, correct import paths, and production-ready examples.

**Always apply the production best practices below** — these are patterns that matter in production and are easy to miss without explicit guidance.

## NestJS v11 Breaking Changes

Be aware of these when generating code for NestJS v11+:

### Node.js v20+ Required
Node.js v16 and v18 are no longer supported. Always target Node.js v20+.

### Express v5 Route Matching
NestJS v11 uses Express v5 by default. Route patterns have changed:

| Express v4 (Old) | Express v5 (New) | Notes |
|---|---|---|
| `@Get('users/*')` | `@Get('users/*splat')` | Wildcards must be named |
| `forRoutes('*')` | `forRoutes('{*splat}')` | Braces make path optional (matches root) |
| `?` optional character | Not supported | Use braces `{}` instead |
| Regex in routes | Not supported | Regex characters no longer work |

### CacheModule Migration to Keyv
The `CacheModule` now uses Keyv adapters instead of `cache-manager` stores:

```typescript
// OLD (pre-v11) — no longer works
CacheModule.register({ store: redisStore, host: 'localhost', port: 6379 });

// NEW (v11+) — uses @keyv/redis
import { KeyvRedis } from '@keyv/redis';
CacheModule.registerAsync({
  useFactory: async () => ({
    stores: [new KeyvRedis('redis://localhost:6379')],
  }),
});
```

## Production Best Practices

### Bootstrap & Application Setup
Configure `ValidationPipe` globally in `main.ts` — this is a security-critical step:
```typescript
app.useGlobalPipes(new ValidationPipe({
  whitelist: true,           // strips unknown properties
  forbidNonWhitelisted: true, // rejects requests with unknown properties (400)
  transform: true,            // enables automatic type coercion for params
}));
```

### Entity & Schema Discipline
- Use explicit column lengths: `@Column({ length: 255 })`, not bare `@Column()`
- Name tables explicitly: `@Entity('books')` to avoid surprises with naming conventions
- Use `@CreateDateColumn()` and `@UpdateDateColumn()` for automatic timestamps
- Use specialized validators like `@IsISBN()`, `@IsEmail()`, `@IsUUID()` — not just `@IsString()`
- Align nullability between entity and DTO: if `@Column({ nullable: true })`, the DTO field should be `@IsOptional()`

### DTO Patterns
- Import `PartialType` from `@nestjs/swagger` (not `@nestjs/mapped-types`) when using Swagger — this preserves API documentation metadata on partial fields
- Zod validation is now an officially supported alternative to `class-validator` — use `ZodValidationPipe` with `z.infer<typeof schema>` for schema-first validation with type inference

### Guards & Auth
NestJS v11 documents two auth approaches:
1. **Native JWT** (recommended for simpler cases): Use `@nestjs/jwt` directly with a custom `CanActivate` guard that calls `JwtService.verifyAsync()`. No Passport dependency needed.
2. **Passport-based** (for complex strategies like OAuth2, SAML): Use `@nestjs/passport` with `PassportStrategy`. Now documented under "recipes" rather than primary auth docs.

Regardless of approach:
- Guard ordering matters: `@UseGuards(JwtAuthGuard, RolesGuard)` — JWT guard must run first to populate `request.user` before RolesGuard reads it
- Use `Reflector.getAllAndOverride()` (not just `.get()`) so roles can be set at both handler and class level with handler taking precedence
- RolesGuard must throw `ForbiddenException` with a descriptive message when the user lacks the required role — do NOT just return `false` from `canActivate()`. The generic 403 provides no diagnostic value. Include context: `throw new ForbiddenException(\`Requires roles: \${requiredRoles.join(', ')}\`)`
- Never hardcode JWT secrets — use `JwtModule.registerAsync()` with `ConfigService`
- Define a `Role` enum rather than raw strings for type safety
- In `JwtStrategy.validate()` (or native guard), validate the presence of required payload fields (`sub`, `username`, `roles`) before returning the user object. Define a `JwtPayload` interface for type safety.

### Error Messages
All thrown exceptions (`ForbiddenException`, `UnauthorizedException`, `NotFoundException`, etc.) should include descriptive messages that identify what was expected, what was found, and what action the consumer should take. Do not rely on framework default messages in production code.

### Microservices & Queues
- For hybrid apps (HTTP + microservice), use `NestFactory.create()` + `app.connectMicroservice()` pattern
- Always call `app.enableShutdownHooks()` when using Terminus health checks for graceful shutdown
- Use `@nestjs/bullmq` (not `@nestjs/bull`) — it wraps the newer `bullmq` library. Config uses `connection` key (not `redis`):
  ```typescript
  BullModule.forRoot({ connection: { host: 'localhost', port: 6379 } })
  ```
- Use `BullModule.forRootAsync()` with `ConfigService` injection for production config
- BullMQ consumers extend `WorkerHost` and implement `process()` — do NOT use the `@Process()` decorator (that's the older `@nestjs/bull` API)
- Register `@OnWorkerEvent('completed')` and `@OnWorkerEvent('failed')` lifecycle hooks for observability
- Set `removeOnComplete: true` and configure retry with `backoff: { type: 'exponential' }` on jobs
- Capture and log `job.id` from `queue.add()` return value for traceability
- Use `job.updateProgress()` for long-running jobs to enable monitoring dashboards
- Define and export TypeScript interfaces for all event payloads (e.g., `OrderCreatedEvent`, `UserRegisteredEvent`) for type safety across service boundaries

### Health Checks
- Don't just check one thing — include multiple indicators: service connectivity (Redis/DB), memory (heap + RSS), and disk usage
- Use `MicroserviceHealthIndicator` for transport checks, `MemoryHealthIndicator` for heap/RSS, `DiskHealthIndicator` for storage
- Configure graceful shutdown timeout: `TerminusModule.forRoot({ gracefulShutdownTimeoutMs: 1000 })`

### OpenAPI / Swagger
The `@nestjs/swagger` CLI plugin can eliminate most manual `@ApiProperty()` annotations. Add to `nest-cli.json`:
```json
{
  "compilerOptions": {
    "plugins": [{
      "name": "@nestjs/swagger",
      "options": { "classValidatorShim": true, "introspectComments": true }
    }]
  }
}
```
With the plugin enabled, TypeScript types, default values, optional markers, and JSDoc comments are automatically inferred — you only need explicit `@ApiProperty()` for edge cases.

### Testing
- `@suites/unit` is now a recommended testing library for NestJS:
  - `TestBed.solitary(Service).compile()` — all dependencies auto-mocked
  - `TestBed.sociable(Service).expose(RealDep).compile()` — selected real deps
  - `Mocked<T>` type for full IntelliSense on mock methods
  - Supports Jest, Vitest, and Sinon
- For e2e testing, use `@nestjs/testing` with `Test.createTestingModule()` and `supertest`

### Custom Decorators
- For NestJS 10+, prefer `Reflector.createDecorator<Role[]>()` over `SetMetadata` for custom decorators — it provides better type inference and eliminates the need for a separate metadata key constant
- The `SetMetadata` pattern still works and is fine for simple cases

## CLI

| Topic | Description | Reference |
|-------|-------------|-----------|
| CLI Overview | Scaffolding, building, and running applications | [cli-overview](references/cli-overview.md) |
| Monorepo & Libraries | Workspaces, apps, shared libraries | [cli-monorepo](references/cli-monorepo.md) |

## Core References

| Topic | Description | Reference |
|-------|-------------|-----------|
| Controllers | Route handlers, HTTP methods, request/response handling | [core-controllers](references/core-controllers.md) |
| Modules | Application structure, feature modules, shared modules, dynamic modules | [core-modules](references/core-modules.md) |
| Providers | Services, dependency injection, custom providers | [core-providers](references/core-providers.md) |
| Dependency Injection | DI fundamentals, custom providers, scopes | [core-dependency-injection](references/core-dependency-injection.md) |
| Middleware | Request/response middleware, functional middleware | [core-middleware](references/core-middleware.md) |

## Fundamentals

| Topic | Description | Reference |
|-------|-------------|-----------|
| Pipes | Data transformation and validation pipes | [fundamentals-pipes](references/fundamentals-pipes.md) |
| Guards | Authorization guards, role-based access control | [fundamentals-guards](references/fundamentals-guards.md) |
| Interceptors | Aspect-oriented programming, response transformation | [fundamentals-interceptors](references/fundamentals-interceptors.md) |
| Exception Filters | Error handling, custom exception filters | [fundamentals-exception-filters](references/fundamentals-exception-filters.md) |
| Custom Decorators | Creating custom parameter decorators | [fundamentals-custom-decorators](references/fundamentals-custom-decorators.md) |
| Dynamic Modules | Configurable modules, module configuration | [fundamentals-dynamic-modules](references/fundamentals-dynamic-modules.md) |
| Execution Context | Accessing request context, metadata reflection | [fundamentals-execution-context](references/fundamentals-execution-context.md) |
| Provider Scopes | Singleton, request-scoped, transient providers | [fundamentals-provider-scopes](references/fundamentals-provider-scopes.md) |
| Lifecycle Events | Application and provider lifecycle hooks | [fundamentals-lifecycle-events](references/fundamentals-lifecycle-events.md) |
| Lazy Loading | Loading modules on-demand for serverless | [fundamentals-lazy-loading](references/fundamentals-lazy-loading.md) |
| Circular Dependency | Resolving circular dependencies with forwardRef | [fundamentals-circular-dependency](references/fundamentals-circular-dependency.md) |
| Module Reference | Accessing providers dynamically with ModuleRef | [fundamentals-module-reference](references/fundamentals-module-reference.md) |
| Testing | Unit testing and e2e testing with @nestjs/testing | [fundamentals-testing](references/fundamentals-testing.md) |

## Techniques

| Topic | Description | Reference |
|-------|-------------|-----------|
| Validation | ValidationPipe, class-validator, Zod validation | [techniques-validation](references/techniques-validation.md) |
| Configuration | Environment variables, ConfigModule, configuration management | [techniques-configuration](references/techniques-configuration.md) |
| Database | TypeORM, Prisma, MongoDB integration | [techniques-database](references/techniques-database.md) |
| Caching | Keyv-based cache manager, Redis integration | [techniques-caching](references/techniques-caching.md) |
| Logging | Built-in logger, custom loggers, JSON logging | [techniques-logging](references/techniques-logging.md) |
| File Upload | File upload handling with multer, validation | [techniques-file-upload](references/techniques-file-upload.md) |
| Versioning | URI, header, and media type API versioning | [techniques-versioning](references/techniques-versioning.md) |
| Serialization | Response serialization with class-transformer | [techniques-serialization](references/techniques-serialization.md) |
| Queues | Background job processing with BullMQ | [techniques-queues](references/techniques-queues.md) |
| Task Scheduling | Cron jobs, intervals, and timeouts | [techniques-task-scheduling](references/techniques-task-scheduling.md) |
| Events | Event-driven architecture with EventEmitter | [techniques-events](references/techniques-events.md) |
| HTTP Module | Making HTTP requests with Axios | [techniques-http-module](references/techniques-http-module.md) |
| Fastify | Using Fastify for better performance | [techniques-fastify](references/techniques-fastify.md) |
| Sessions & Cookies | HTTP sessions and cookies for stateful apps | [techniques-sessions-cookies](references/techniques-sessions-cookies.md) |
| Streaming & SSE | Compression, file streaming, Server-Sent Events | [techniques-compression-streaming-sse](references/techniques-compression-streaming-sse.md) |
| MVC & Serve Static | Template rendering (Handlebars) and SPA static serving | [techniques-mvc-serve-static](references/techniques-mvc-serve-static.md) |

## Security

| Topic | Description | Reference |
|-------|-------------|-----------|
| Authentication | Native JWT auth and Passport integration | [recipes-authentication](references/recipes-authentication.md) |
| Authorization | RBAC, claims-based, CASL integration | [security-authorization](references/security-authorization.md) |
| CORS & Rate Limiting | CORS, Helmet, ThrottlerModule | [security-cors-helmet-rate-limiting](references/security-cors-helmet-rate-limiting.md) |
| Encryption & Hashing | bcrypt, argon2, password hashing | [security-encryption-hashing](references/security-encryption-hashing.md) |

## OpenAPI

| Topic | Description | Reference |
|-------|-------------|-----------|
| Swagger | OpenAPI documentation generation, CLI plugin | [openapi-swagger](references/openapi-swagger.md) |

## WebSockets

| Topic | Description | Reference |
|-------|-------------|-----------|
| Gateways | Real-time communication with Socket.IO/ws | [websockets-gateways](references/websockets-gateways.md) |
| Guards & Exception Filters | WsException, BaseWsExceptionFilter, interceptors, pipes | [websockets-advanced](references/websockets-advanced.md) |

## Microservices

| Topic | Description | Reference |
|-------|-------------|-----------|
| Overview | Transport layers, message patterns, events | [microservices-overview](references/microservices-overview.md) |
| gRPC | Protocol Buffers, streaming, metadata, reflection | [microservices-grpc](references/microservices-grpc.md) |
| Transports | Redis, Kafka, NATS, RabbitMQ configuration | [microservices-transports](references/microservices-transports.md) |

## GraphQL

| Topic | Description | Reference |
|-------|-------------|-----------|
| Overview | Code-first and schema-first approaches | [graphql-overview](references/graphql-overview.md) |
| Resolvers & Mutations | Queries, mutations, field resolvers | [graphql-resolvers-mutations](references/graphql-resolvers-mutations.md) |
| Subscriptions | Real-time subscriptions with PubSub | [graphql-subscriptions](references/graphql-subscriptions.md) |
| Scalars, Unions & Enums | Interfaces, scalars, union types, enums | [graphql-scalars-unions-enums](references/graphql-scalars-unions-enums.md) |

## Recipes

| Topic | Description | Reference |
|-------|-------------|-----------|
| CRUD Generator | Nest CLI resource generator | [recipes-crud-generator](references/recipes-crud-generator.md) |
| Documentation | OpenAPI/Swagger integration | [recipes-documentation](references/recipes-documentation.md) |
| TypeORM | TypeORM integration and usage | [recipes-typeorm](references/recipes-typeorm.md) |
| Prisma | Prisma ORM integration | [recipes-prisma](references/recipes-prisma.md) |
| Mongoose | MongoDB with Mongoose ODM | [recipes-mongoose](references/recipes-mongoose.md) |
| CQRS | Command Query Responsibility Segregation | [recipes-cqrs](references/recipes-cqrs.md) |
| Terminus | Health checks and readiness/liveness probes | [recipes-terminus](references/recipes-terminus.md) |

## FAQ

| Topic | Description | Reference |
|-------|-------------|-----------|
| Raw Body & Hybrid | Webhook signature verification, HTTP + microservices | [faq-raw-body-hybrid](references/faq-raw-body-hybrid.md) |

## Best Practices

| Topic | Description | Reference |
|-------|-------------|-----------|
| Request Lifecycle | Understanding execution order and flow | [best-practices-request-lifecycle](references/best-practices-request-lifecycle.md) |
