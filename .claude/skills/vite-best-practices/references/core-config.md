---
name: vite-config
description: Vite 8 configuration patterns using vite.config.ts
---

# Vite Configuration

## Basic Setup

```ts
// vite.config.ts
import { defineConfig } from 'vite'

export default defineConfig({
  // config options
})
```

Vite auto-resolves `vite.config.ts` from project root. Supports ES modules syntax regardless of `package.json` type.

## Conditional Config

Export a function to access command and mode:

```ts
export default defineConfig(({ command, mode, isSsrBuild, isPreview }) => {
  if (command === 'serve') {
    return { /* dev config */ }
  } else {
    return { /* build config */ }
  }
})
```

- `command`: `'serve'` during dev, `'build'` for production
- `mode`: `'development'` or `'production'` (or custom via `--mode`)

## Async Config

```ts
export default defineConfig(async ({ command, mode }) => {
  const data = await fetchSomething()
  return { /* config */ }
})
```

## Using Environment Variables in Config

`.env` files are loaded **after** config resolution. Use `loadEnv` to access them in config:

```ts
import { defineConfig, loadEnv } from 'vite'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  return {
    define: {
      __APP_ENV__: JSON.stringify(env.APP_ENV),
    },
    server: {
      port: env.APP_PORT ? Number(env.APP_PORT) : 5173,
    },
  }
})
```

## Key Config Options

### resolve.alias

```ts
export default defineConfig({
  resolve: {
    alias: {
      '@': '/src',
      '~': '/src',
    },
  },
})
```

### resolve.tsconfigPaths (Vite 8)

Auto-resolve TypeScript path aliases from `tsconfig.json`:

```ts
export default defineConfig({
  resolve: {
    tsconfigPaths: true,  // default: false (small perf cost)
  },
})
```

### define (Global Constants)

```ts
export default defineConfig({
  define: {
    __APP_VERSION__: JSON.stringify('1.0.0'),
    __API_URL__: 'window.__backend_api_url',
  },
})
```

Values must be JSON-serializable or single identifiers. Non-strings auto-wrapped with `JSON.stringify`.

### plugins

```ts
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
})
```

Plugins array is flattened; falsy values ignored.

### oxc (Vite 8 — replaces esbuild)

```ts
export default defineConfig({
  oxc: {
    jsx: {
      runtime: 'automatic',  // or 'classic'
      importSource: 'react',
    },
    jsxInject: `import React from 'react'`,  // auto-inject
    include: ['**/*.ts', '**/*.tsx'],         // default: ts, jsx, tsx
    exclude: ['node_modules/**'],
  },
})
```

Set `oxc: false` to disable Oxc transformation entirely.

**Note:** The old `esbuild` option still works via compatibility layer but is deprecated. Always use `oxc` in new code.

### server.proxy

```ts
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:3000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
```

### server.forwardConsole (Vite 8)

Route browser console logs to the dev server terminal:

```ts
export default defineConfig({
  server: {
    forwardConsole: true,  // useful for AI coding agents detecting runtime errors
  },
})
```

### devtools (Vite 8 — Experimental)

```ts
export default defineConfig({
  devtools: true,  // requires @vitejs/devtools installed; build mode only
})
```

### build.target

Default: Baseline Widely Available browsers (Chrome 111+, Firefox 114+, Safari 16.4+).

```ts
export default defineConfig({
  build: {
    target: 'esnext', // or 'es2020', ['chrome90', 'firefox88']
  },
})
```

### build.rolldownOptions (Vite 8 — replaces rollupOptions)

```ts
export default defineConfig({
  build: {
    rolldownOptions: {
      external: ['vue'],
      output: {
        globals: { vue: 'Vue' },
      },
    },
  },
})
```

**Note:** `build.rollupOptions` still works via compat layer but is deprecated.

## TypeScript Intellisense

For plain JS config files:

```js
/** @type {import('vite').UserConfig} */
export default {
  // ...
}
```

Or use `satisfies`:

```ts
import type { UserConfig } from 'vite'

export default {
  // ...
} satisfies UserConfig
```

<!--
Source references:
- https://vite.dev/config/
- https://vite.dev/guide/
- https://vite.dev/guide/migration
-->
