---
name: next-best-practices
description: Next.js best practices for App Router, Server/Client Components, data fetching, caching, Server Actions, and performance optimization. Use this skill whenever working with Next.js applications — including routing, layouts, data fetching, forms, mutations, caching strategies, streaming, metadata/SEO, image/font optimization, or any React Server Component patterns. Also use when upgrading Next.js, debugging hydration errors, or deciding between server and client rendering. Even if the task seems simple, consult this skill to ensure modern Next.js 16 patterns are used instead of outdated approaches.
---

# Next.js Best Practices

Modern Next.js (v16+) with App Router, React Server Components, and Cache Components. This skill ensures you use current APIs instead of deprecated patterns like `unstable_cache`, `getServerSideProps`, or `useFormState`.

## Critical Modern Patterns

These patterns differentiate production-quality Next.js code from outdated approaches. Prioritize them in every implementation:

| Pattern | What | Why it matters |
|---------|------|---------------|
| `'use cache'` directive | Cache any async computation (not just `fetch`) | Replaces `unstable_cache`. Enables PPR. |
| `useActionState` | Form pending states + error handling | Replaces `useFormState`. React 19 standard. |
| `useOptimistic` | Instant UI updates before server responds | Critical for perceived performance. |
| `updateTag` | Immediate cache expiration in Server Actions | Read-your-own-writes. Use instead of `revalidateTag` after mutations the user should see immediately. |
| `import 'server-only'` | Prevent accidental client import of server code | Protects secrets, reduces bundle. Always use on DB/auth modules. |
| Async request APIs | `params`, `searchParams`, `cookies()`, `headers()` are all `Promise` in Next.js 15+ | Must `await` in server components, `use()` in client components. |
| Proxy (formerly Middleware) | `middleware.ts` renamed: export `proxy()` function instead of `middleware()` | Next.js 16 rename. Same functionality, new name. |

## Core References

Read these for foundational patterns. The routing and component model references are essential for any Next.js work.

| Topic | When to read | Reference |
|-------|-------------|-----------|
| File-System Routing | Setting up routes, layouts, nested routes, route groups | [core-routing](references/core-routing.mdx) |
| Server and Client Components | Deciding where to place `'use client'` boundaries, composing server + client | [core-server-client-components](references/core-server-client-components.mdx) |
| Navigation | Links, prefetching, programmatic navigation, `useRouter` | [core-navigation](references/core-navigation.mdx) |

## Data Fetching & Mutations

These references cover how to get data in and out of the application.

| Topic | When to read | Reference |
|-------|-------------|-----------|
| Server Data Fetching | Fetching in Server Components with `fetch`, ORMs, databases | [data-fetching-server](references/data-fetching-server.mdx) |
| Client Data Fetching | `use` hook, SWR, React Query, streaming promises to client | [data-fetching-client](references/data-fetching-client.mdx) |
| Server Actions | Forms, mutations, `useActionState`, `useOptimistic`, `updateTag`, redirects | [server-actions](references/server-actions.mdx) |
| Streaming | `loading.tsx`, `<Suspense>`, parallel/sequential streaming, preloading | [data-streaming](references/data-streaming.mdx) |

## Caching & Revalidation

Modern Next.js has a layered caching system. Read these when implementing any caching strategy.

| Topic | When to read | Reference |
|-------|-------------|-----------|
| Caching Strategies | `fetch` caching, `revalidateTag`, `updateTag`, `revalidatePath`, ISR | [caching-revalidation](references/caching-revalidation.mdx) |
| Cache Components & PPR | `'use cache'` directive, `cacheLife`, `cacheTag`, `'use cache: remote/private'`, `connection()`, `cacheComponents` config | [cache-components](references/cache-components.mdx) |

## File Conventions & Metadata

| Topic | When to read | Reference |
|-------|-------------|-----------|
| Dynamic Routes | `[slug]`, `[...slug]`, `[[...slug]]`, `generateStaticParams`, async params | [file-conventions-dynamic-routes](references/file-conventions-dynamic-routes.mdx) |
| Loading, Error, Not Found | `loading.tsx`, `error.tsx`, `not-found.tsx`, `global-error.tsx` | [file-conventions-loading-error](references/file-conventions-loading-error.mdx) |
| Metadata & SEO | `generateMetadata`, static metadata, `viewport`, Open Graph, JSON-LD | [metadata-seo](references/metadata-seo.mdx) |

## Built-in Components & Optimization

| Topic | When to read | Reference |
|-------|-------------|-----------|
| Link, Image, Script, Font, Form | `next/link`, `next/image`, `next/script`, `next/font`, `next/form`, `server-only` | [api-components](references/api-components.mdx) |

## Common Gotchas

- **All request APIs are async in Next.js 15+**: `params`, `searchParams`, `cookies()`, `headers()` all return Promises. Always `await` them. Using them synchronously will throw.
- **Middleware → Proxy**: In Next.js 16, `middleware.ts` exports `proxy()` instead of `middleware()`. The `config.matcher` pattern stays the same.
- **`unstable_cache` is deprecated**: Use `'use cache'` + `cacheTag` instead. See [cache-components](references/cache-components.mdx).
- **`useFormState` is deprecated**: Use `useActionState` from `react` (not `react-dom`).
- **`revalidateTag(tag)` without profile**: Legacy immediate expiration. Use `revalidateTag(tag, 'max')` for stale-while-revalidate, or `updateTag(tag)` for read-your-own-writes.

## Decision Guide

Use this to quickly decide which pattern fits your use case:

**Data fetching:**
- Need data on the server? → Server Component with `async/await` (read [data-fetching-server](references/data-fetching-server.mdx))
- Need data on the client with interactivity? → `use` hook or SWR/React Query (read [data-fetching-client](references/data-fetching-client.mdx))
- Need to cache a DB query or computation? → `'use cache'` + `cacheTag` (read [cache-components](references/cache-components.mdx))

**Mutations:**
- Simple form submission? → Server Action with `action={...}` prop
- Form with pending/error states? → `useActionState` + Server Action
- Need instant UI feedback? → `useOptimistic` + `useTransition`
- User must see their own write immediately? → `updateTag` (not `revalidateTag`)
- Background revalidation OK? → `revalidateTag(tag, 'max')` (stale-while-revalidate)

**Caching:**
- Cache a `fetch` call? → `next: { tags: ['...'] }` or `cache: 'force-cache'`
- Cache a DB query / computation? → `'use cache'` + `cacheTag('...')`
- Per-user cached data? → `'use cache: private'`
- Shared runtime cache (not build-time)? → `'use cache: remote'`
- Need PPR (partial prerendering)? → `cacheComponents: true` in next.config.js

**Components:**
- Needs state, effects, or browser APIs? → Client Component (`'use client'`)
- Everything else? → Server Component (default, no directive needed)
- Want to keep server component inside client boundary? → Pass as `children` prop
