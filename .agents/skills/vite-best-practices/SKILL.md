---
name: vite-best-practices
description: Vite build tool configuration, plugin API, SSR, library mode, and Vite 8 Rolldown/Oxc migration. Use when working with Vite projects, vite.config.ts, Vite plugins, building libraries or SSR apps with Vite, migrating from older Vite versions, or configuring Rolldown/Oxc options. Also use when the user mentions HMR, import.meta.glob, virtual modules, or Vite environment variables.
---

# Vite

> Based on Vite 8.0 stable (March 2026). Vite 8 uses Rolldown bundler and Oxc transformer, replacing esbuild + Rollup.

Vite is a next-generation frontend build tool with fast dev server (native ESM + HMR) and optimized production builds powered by Rolldown.

## Key Vite 8 Changes

Vite 8 replaces the dual esbuild+Rollup architecture with Rolldown (unified Rust-based bundler) and Oxc (transformer/minifier). A **compatibility layer** auto-converts old `esbuild` and `rollupOptions` configs, but both are deprecated — always use the new names in new code:

| Deprecated (still works) | Replacement |
|--------------------------|-------------|
| `build.rollupOptions` | `build.rolldownOptions` |
| `esbuild` | `oxc` |
| `optimizeDeps.esbuildOptions` | `optimizeDeps.rolldownOptions` |
| `build.minify: 'esbuild'` | `build.minify: 'oxc'` (default) |

## Preferences

- Use TypeScript: prefer `vite.config.ts`
- Always use ESM — avoid CommonJS
- Use `import.meta.dirname` (ESM) not `__dirname` (CJS) in config files
- Use `rolldownOptions` not `rollupOptions` in new code
- Use `oxc` not `esbuild` in new code

## Core

| Topic | Description | Reference |
|-------|-------------|-----------|
| Configuration | `vite.config.ts`, `defineConfig`, conditional configs, `loadEnv`, new v8 options | [core-config](references/core-config.md) |
| Features | `import.meta.glob`, asset queries, `import.meta.env`, HMR API, CSS modules | [core-features](references/core-features.md) |
| Plugin API | Vite/Rolldown hooks, virtual modules, hook filters, plugin ordering | [core-plugin-api](references/core-plugin-api.md) |

## Build & SSR

| Topic | Description | Reference |
|-------|-------------|-----------|
| Build & SSR | Library mode, SSR middleware, `ssrLoadModule`, multi-page apps, JavaScript API | [build-and-ssr](references/build-and-ssr.md) |

## Advanced

| Topic | Description | Reference |
|-------|-------------|-----------|
| Environment API | Vite 6+ multi-environment support, custom runtimes | [environment-api](references/environment-api.md) |
| Rolldown Migration | Vite 8 migration: complete esbuild→oxc and rollupOptions→rolldownOptions mapping, breaking changes | [rolldown-migration](references/rolldown-migration.md) |

## Quick Reference

### CLI Commands

```bash
vite              # Start dev server
vite build        # Production build
vite preview      # Preview production build
vite build --ssr  # SSR build
```

### Common Config (Vite 8)

```ts
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [],
  resolve: {
    alias: { '@': '/src' },
    tsconfigPaths: true,  // New in v8: auto-resolve TS path aliases
  },
  server: {
    port: 3000,
    proxy: { '/api': 'http://localhost:8080' },
    forwardConsole: true,  // New in v8: browser logs → terminal
  },
  build: {
    target: 'esnext',
    outDir: 'dist',
    rolldownOptions: {},   // NOT rollupOptions
  },
  oxc: {                   // NOT esbuild
    jsx: {
      runtime: 'automatic',
      importSource: 'react',
    },
  },
})
```

### Official Plugins

- `@vitejs/plugin-react` v6 — React with Oxc transforms (Babel removed)
- `@vitejs/plugin-react-swc` — React with SWC
- `@vitejs/plugin-vue` — Vue 3 SFC support
- `@vitejs/plugin-vue-jsx` — Vue 3 JSX
- `@vitejs/plugin-legacy` — Legacy browser support

### Oxc JSX Quick Reference

```ts
// React (automatic runtime — default)
oxc: { jsx: { runtime: 'automatic', importSource: 'react' } }

// Preact (automatic)
oxc: { jsx: { runtime: 'automatic', importSource: 'preact' } }

// Preact (classic with h/Fragment)
oxc: { jsx: { runtime: 'classic', pragma: 'h', pragmaFrag: 'Fragment' } }

// Auto-inject React import (legacy patterns)
oxc: { jsxInject: `import React from 'react'` }
```
