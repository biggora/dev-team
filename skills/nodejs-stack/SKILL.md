---
name: Node.js Stack Knowledge
description: >
  This skill should be used when working with Node.js, TypeScript, or JavaScript projects,
  including frameworks like Next.js, NestJS, Express, Fastify, and Vite.
metadata:
  priority: 7
  pathPatterns:
    - "**/*.ts"
    - "**/*.tsx"
    - "**/*.js"
    - "**/*.mjs"
    - "**/*.jsx"
    - "**/package.json"
    - "**/tsconfig*.json"
    - "**/next.config.*"
    - "**/nest-cli.json"
    - "**/vite.config.*"
    - "**/vitest.config.*"
    - "**/jest.config.*"
    - "**/.eslintrc*"
    - "**/eslint.config.*"
  bashPatterns:
    - "npm *"
    - "npx *"
    - "yarn *"
    - "pnpm *"
    - "node *"
    - "tsx *"
    - "ts-node *"
  importPatterns:
    - "react"
    - "next"
    - "express"
    - "fastify"
    - "@nestjs"
    - "vite"
  promptSignals:
    phrases:
      - "typescript"
      - "node.js"
      - "react component"
      - "next.js"
      - "nestjs"
      - "express"
      - "vite"
    allOf:
      - ["node", "project"]
      - ["typescript", "project"]
      - ["react", "component"]
    noneOf:
      - "python only"
      - "django"
      - "flask"
    minScore: 6
---

# Node.js Stack Knowledge

## Project Structure Conventions

### Next.js (App Router)
- `app/` — routes, layouts, pages (`page.tsx`, `layout.tsx`, `loading.tsx`, `error.tsx`)
- `components/` — reusable React components
- `lib/` or `utils/` — shared utilities
- `public/` — static assets
- Server Components by default, `"use client"` for client components
- Server Actions with `"use server"` for mutations

### NestJS
- `src/` → modules (`*.module.ts`), controllers (`*.controller.ts`), services (`*.service.ts`)
- Decorators: `@Controller()`, `@Injectable()`, `@Module()`, `@Get()`, `@Post()`
- Dependency injection via constructor
- Pipes for validation, Guards for auth, Interceptors for transformation

### Express / Fastify
- Router-based structure: `routes/`, `middleware/`, `controllers/`
- Middleware chain: `(req, res, next) => {}`
- Error handling middleware: `(err, req, res, next) => {}`

## TypeScript Patterns

- Prefer `interface` for object shapes, `type` for unions/intersections
- Use `strict: true` in tsconfig
- Avoid `any` — use `unknown` + type guards instead
- Use `as const` for literal types
- Prefer named exports over default exports (except for Next.js pages)

## Testing

- **Jest**: `describe/it/expect`, `jest.mock()`, `beforeEach/afterEach`
- **Vitest**: same API as Jest, use `vi.mock()` instead of `jest.mock()`
- Test file naming: `*.test.ts`, `*.spec.ts`, or `__tests__/` directory
- Mock external dependencies, test behavior not implementation

## Error Handling

- Use custom error classes extending `Error`
- Async functions: always handle promise rejections
- Express: pass errors to `next(error)`
- NestJS: use exception filters (`@Catch()`)
- Never swallow errors silently

## Common Anti-Patterns

- Don't use `require()` in ESM projects — use `import`
- Don't mutate function parameters
- Don't use `var` — use `const` by default, `let` when reassignment needed
- Don't ignore TypeScript errors with `@ts-ignore` — fix the types

## Additional Resources

For framework-specific patterns, consult:
- **`references/nextjs-patterns.md`** — Next.js App Router patterns, data fetching, caching
- **`references/nestjs-patterns.md`** — NestJS modules, DI, decorators, guards, pipes
- **`references/testing-patterns.md`** — Jest/Vitest patterns, mocking strategies
