---
name: vite-rolldown
description: Vite 8 Rolldown bundler and Oxc transformer migration from Vite 7
---

# Rolldown Migration (Vite 8)

Vite 8 (stable March 2026) replaces esbuild+Rollup with Rolldown, a unified Rust-based bundler. Performance gains of 10-30x for production builds are typical.

## What Changed

| Before (Vite 7) | After (Vite 8) | Compat Layer |
|-----------------|----------------|--------------|
| esbuild (dev transform) | Oxc Transformer | `esbuild` auto-converts to `oxc` |
| esbuild (dep pre-bundling) | Rolldown | `esbuildOptions` auto-converts |
| esbuild (JS minification) | Oxc Minifier | `minify: 'esbuild'` = fallback |
| esbuild (CSS minification) | Lightning CSS | `cssMinify: 'esbuild'` = fallback |
| Rollup (production build) | Rolldown | `rollupOptions` auto-converts |
| `rollupOptions` | `rolldownOptions` | deprecated, auto-converts |
| `esbuild` option | `oxc` option | deprecated, auto-converts |

**Important:** A compatibility layer auto-converts old config names, so many projects upgrade with zero config changes. However, both `esbuild` and `rollupOptions` are deprecated and will be removed in a future version. Always use the new names in new code.

## Config Migration

### rollupOptions → rolldownOptions

Direct rename. Internal structure (`external`, `output.globals`) stays the same:

```ts
// Before (Vite 7)
export default defineConfig({
  build: {
    rollupOptions: {
      external: ['vue'],
      output: { globals: { vue: 'Vue' } },
    },
  },
})

// After (Vite 8)
export default defineConfig({
  build: {
    rolldownOptions: {
      external: ['vue'],
      output: { globals: { vue: 'Vue' } },
    },
  },
})
```

Also applies to `worker.rollupOptions` → `worker.rolldownOptions`.

### esbuild → oxc (JavaScript Transforms)

Complete mapping of esbuild JSX options to Oxc:

| esbuild | oxc equivalent |
|---------|---------------|
| `jsx: 'transform'` | `jsx: { runtime: 'classic' }` |
| `jsx: 'automatic'` | `jsx: { runtime: 'automatic' }` |
| `jsx: 'preserve'` | `jsx: 'preserve'` |
| `jsxFactory: 'h'` | `jsx.pragma: 'h'` |
| `jsxFragment: 'Fragment'` | `jsx.pragmaFrag: 'Fragment'` |
| `jsxImportSource: 'react'` | `jsx.importSource: 'react'` |
| `jsxDev` | `jsx.development` |
| `jsxSideEffects` | `jsx.pure` |
| `jsxInject` | `jsxInject` (same) |
| `include`/`exclude` | `include`/`exclude` (same) |
| `define` | `define` (same) |

**Not supported in Oxc:** `esbuild.supported` option.

**Not supported:** Native decorator lowering — use Babel or SWC plugins.

**Example — Preact classic JSX:**

```ts
// Before (Vite 7)
export default defineConfig({
  esbuild: {
    jsxFactory: 'h',
    jsxFragment: 'Fragment',
  },
})

// After (Vite 8)
export default defineConfig({
  oxc: {
    jsx: {
      runtime: 'classic',
      pragma: 'h',
      pragmaFrag: 'Fragment',
    },
  },
})
```

**Example — React automatic:**

```ts
export default defineConfig({
  oxc: {
    jsx: {
      runtime: 'automatic',
      importSource: 'react',
    },
  },
})
```

### optimizeDeps.esbuildOptions → optimizeDeps.rolldownOptions

Auto-converted options:

| esbuildOptions | rolldownOptions equivalent |
|---------------|--------------------------|
| `minify` | `output.minify` |
| `treeShaking` | `treeshake` |
| `define` | `transform.define` |
| `loader` | `moduleTypes` |
| `preserveSymlinks` | `!resolve.symlinks` |
| `resolveExtensions` | `resolve.extensions` |
| `mainFields` | `resolve.mainFields` |
| `conditions` | `resolve.conditionNames` |
| `keepNames` | `output.keepNames` |
| `platform` | `platform` |
| `plugins` | `plugins` (partial support) |

### Minification

```ts
// Vite 8 default: Oxc minifier
build: { minify: true }  // uses Oxc

// Fallback to esbuild (requires installing esbuild)
build: { minify: 'esbuild' }

// CSS: Lightning CSS is default
build: { cssMinify: true }           // uses Lightning CSS
build: { cssMinify: 'esbuild' }     // fallback (requires esbuild)
```

**Not supported by Oxc minifier:** `mangleProps`, `reserveProps`, `mangleQuoted`, `mangleCache`.

### esbuild.banner/footer

No direct equivalent. Use a custom plugin with the `transform` hook instead.

## Breaking Changes

### manualChunks

- Object form **removed**
- Function form **deprecated** → use `codeSplitting` option instead

### CommonJS Interop

The `default` import from CJS modules follows new rules. If the importer is `.mjs`/`.mts`, or the closest `package.json` has `"type": "module"`, or `module.exports.__esModule` is not true, then `default` = `module.exports` (not `module.exports.default`).

Temporary workaround: `legacy.inconsistentCjsInterop: true`.

### Format Sniffing Removed

Vite no longer sniffs file content to choose between `browser` and `module` fields. `resolve.mainFields` order is always respected.

### build() Error Handling

`build()` now throws `BundleError` (not raw error) with `.errors?: RolldownError[]` array.

### Removed Config Options

| Removed | Replacement |
|---------|-------------|
| `build.commonjsOptions` | No-op (Rolldown handles CJS natively) |
| `build.dynamicImportVarsOptions.warnOnError` | No-op |
| `resolve.alias[].customResolver` | Use custom plugin with `resolveId` hook |
| `rollupOptions.output.manualChunks` (object form) | Use function form or `codeSplitting` |
| `rollupOptions.watch.chokidar` | `rolldownOptions.watch.watcher` |

### Unsupported Output Formats

`'system'` and `'amd'` output formats are not supported by Rolldown.

### Node.js Requirements

Node.js 20.19+ or 22.12+ required (same as Vite 7).

## Plugin Compatibility

Most Vite/Rollup plugins work unchanged because Rolldown supports the Rollup plugin API. If a plugin only works during build:

```ts
{
  ...rollupPlugin(),
  enforce: 'post',
  apply: 'build',
}
```

**Note:** `moduleParsed` hook is NOT called during dev. Plugins relying on it need adjustment.

Detect Rolldown at runtime: `this.meta.rolldownVersion`.

## Gradual Migration

For large projects, migrate via `rolldown-vite` first:

```bash
# Step 1: Test with rolldown-vite (still Vite 7)
pnpm add -D rolldown-vite

# Replace vite import in config
import { defineConfig } from 'rolldown-vite'

# Step 2: Once stable, upgrade to Vite 8
pnpm add -D vite@8

# Revert the import
import { defineConfig } from 'vite'
```

## Overriding Vite in Frameworks

When framework depends on older Vite:

```json
{
  "pnpm": {
    "overrides": {
      "vite": "8.0.0"
    }
  }
}
```

<!--
Source references:
- https://vite.dev/blog/announcing-vite8
- https://vite.dev/guide/migration
- https://vite.dev/config/shared-options#oxc
-->
