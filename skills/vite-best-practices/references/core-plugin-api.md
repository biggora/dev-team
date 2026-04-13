---
name: vite-plugin-api
description: Vite plugin authoring with Rolldown hooks and Vite-specific hooks (Vite 8)
---

# Vite Plugin API

Vite plugins extend Rolldown's plugin interface with Vite-specific hooks. Refer to Rolldown's plugin documentation for the base API.

## Basic Structure

```ts
import type { Plugin } from 'vite'

function myPlugin(): Plugin {
  return {
    name: 'my-plugin',
    // hooks...
  }
}
```

## Vite-Specific Hooks

### config

Modify config before resolution:

```ts
const plugin = () => ({
  name: 'add-alias',
  config: () => ({
    resolve: {
      alias: { foo: 'bar' },
    },
  }),
})
```

### configResolved

Access final resolved config:

```ts
const plugin = () => {
  let config: ResolvedConfig
  return {
    name: 'read-config',
    configResolved(resolvedConfig) {
      config = resolvedConfig
    },
    transform(code, id) {
      if (config.command === 'serve') { /* dev */ }
    },
  }
}
```

### configureServer

Add custom middleware to dev server:

```ts
const plugin = () => ({
  name: 'custom-middleware',
  configureServer(server) {
    server.middlewares.use((req, res, next) => {
      // handle request
      next()
    })
  },
})
```

Return function to run **after** internal middlewares:

```ts
configureServer(server) {
  return () => {
    server.middlewares.use((req, res, next) => {
      // runs after Vite's middlewares
    })
  }
}
```

### transformIndexHtml

Transform HTML entry files:

```ts
const plugin = () => ({
  name: 'html-transform',
  transformIndexHtml(html) {
    return html.replace(/<title>(.*?)<\/title>/, '<title>New Title</title>')
  },
})
```

Inject tags:

```ts
transformIndexHtml() {
  return [
    { tag: 'script', attrs: { src: '/inject.js' }, injectTo: 'body' },
  ]
}
```

### handleHotUpdate

Custom HMR handling:

```ts
handleHotUpdate({ server, modules, timestamp }) {
  server.ws.send({ type: 'custom', event: 'special-update', data: {} })
  return [] // empty = skip default HMR
}
```

## Virtual Modules

Serve virtual content without files on disk:

```ts
import { exactRegex } from '@rolldown/pluginutils'

const plugin = () => {
  const virtualModuleId = 'virtual:my-module'
  const resolvedId = '\0' + virtualModuleId

  return {
    name: 'virtual-module',
    resolveId: {
      filter: { id: exactRegex(virtualModuleId) },
      handler() {
        return resolvedId
      },
    },
    load: {
      filter: { id: exactRegex(resolvedId) },
      handler() {
        return `export const msg = "from virtual module"`
      },
    },
  }
}
```

Usage:

```ts
import { msg } from 'virtual:my-module'
```

Convention: prefix user-facing path with `virtual:`, prefix resolved id with `\0`.

**Note:** The older function-based syntax (`resolveId(id) { ... }`) still works — the filter-based syntax above is the newer, more performant pattern from Rolldown.

## Hook Filters (Vite 8 / Rolldown)

Hook filters reduce overhead by letting plugins declare which files they care about, so hooks are only called when relevant:

```ts
{
  name: 'transform-ts',
  transform: {
    filter: { id: /\.(ts|tsx)$/ },
    handler(code, id) {
      // Only called for .ts/.tsx files
      return { code: transform(code), map: null }
    },
  },
}
```

## moduleType in load/transform (Vite 8)

When converting non-JS content to JavaScript, you must specify `moduleType: 'js'` so Rolldown interprets the output correctly:

```ts
{
  name: 'txt-loader',
  load(id) {
    if (id.endsWith('.txt')) {
      const content = fs.readFileSync(id, 'utf-8')
      return {
        code: `export default ${JSON.stringify(content)}`,
        moduleType: 'js',
      }
    }
  },
}
```

## Plugin Ordering

Use `enforce` to control execution order:

```ts
{
  name: 'pre-plugin',
  enforce: 'pre',  // runs before core plugins
}

{
  name: 'post-plugin',
  enforce: 'post', // runs after build plugins
}
```

Order: Alias → `enforce: 'pre'` → Core → User (no enforce) → Build → `enforce: 'post'` → Post-build

## Conditional Application

```ts
{
  name: 'build-only',
  apply: 'build',  // or 'serve'
}

// Function form:
{
  apply(config, { command }) {
    return command === 'build' && !config.build.ssr
  }
}
```

## Universal Hooks (from Rolldown)

These work in both dev and build:

- `resolveId(id, importer)` — Resolve import paths
- `load(id)` — Load module content
- `transform(code, id)` — Transform module code

```ts
transform(code, id) {
  if (id.endsWith('.custom')) {
    return { code: compile(code), map: null }
  }
}
```

**Note:** `moduleParsed` hook is NOT called during dev in Vite 8.

## Detecting Rolldown at Runtime

```ts
transform(code, id) {
  if (this.meta.rolldownVersion) {
    // Running on Rolldown-powered Vite (8+)
  }
}
```

## Client-Server Communication

Server to client:

```ts
configureServer(server) {
  server.ws.send('my:event', { msg: 'hello' })
}
```

Client side:

```ts
if (import.meta.hot) {
  import.meta.hot.on('my:event', (data) => {
    console.log(data.msg)
  })
}
```

Client to server:

```ts
// Client
import.meta.hot.send('my:from-client', { msg: 'Hey!' })

// Server
server.ws.on('my:from-client', (data, client) => {
  client.send('my:ack', { msg: 'Got it!' })
})
```

<!--
Source references:
- https://vite.dev/guide/api-plugin
- https://vite.dev/guide/migration
-->
