# tsconfig.json Configuration

## Recommended Base Configuration

```jsonc
{
  "compilerOptions": {
    // Type Checking — always enable strict
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noFallthroughCasesInSwitch": true,
    "forceConsistentCasingInFileNames": true,

    // Modules
    "module": "ESNext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "verbatimModuleSyntax": true,

    // Emit
    "target": "ES2022",
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "outDir": "./dist",

    // Interop
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "skipLibCheck": true
  },
  "include": ["src"],
  "exclude": ["node_modules", "dist"]
}
```

## What `strict` Enables

`"strict": true` is a shorthand for all of these:

| Flag | What it does | Why it matters |
|------|-------------|----------------|
| `strictNullChecks` | `null`/`undefined` not assignable to other types | Prevents null reference errors |
| `noImplicitAny` | Error on inferred `any` | Prevents silent type safety holes |
| `strictFunctionTypes` | Strict function parameter checking | Catches unsound function assignments |
| `strictBindCallApply` | Type-check `bind`, `call`, `apply` | Prevents runtime argument mismatches |
| `strictPropertyInitialization` | Class properties must be initialized | Prevents undefined property access |
| `noImplicitThis` | Error on `this` with implicit `any` type | Prevents `this` context bugs |
| `alwaysStrict` | Emits `"use strict"` | JavaScript strict mode |
| `useUnknownInCatchVariables` | `catch(e)` gives `e: unknown` not `any` | Forces error type checking |
| `exactOptionalPropertyTypes` | `?:` means "may be missing", not "may be undefined" | More precise optional semantics |

## Module Resolution Strategies

### `"moduleResolution": "bundler"` (Recommended for apps)

Use when a bundler (Vite, webpack, esbuild, Turbopack) handles module resolution. Supports:
- Extensionless imports (`import "./utils"` resolves to `./utils.ts`)
- `package.json` `exports` field
- Conditional `imports`

### `"moduleResolution": "node16"` / `"nodenext"` (For libraries/Node.js)

Use when targeting Node.js directly or publishing a library. Requires:
- File extensions in relative imports (`import "./utils.js"`)
- `.mts`/`.cts` for ESM/CJS files
- Correct `package.json` `type` and `exports`

### `"moduleResolution": "node"` (Legacy)

The old Node.js resolution. Doesn't understand `exports` or conditional imports. Avoid for new projects.

## `verbatimModuleSyntax` (TS 5.0+)

Replaces the older `importsNotUsedAsValues` and `preserveValueImports`. Forces you to be explicit about type-only imports:

```typescript
// With verbatimModuleSyntax: true
import type { User } from "./types";  // Erased at runtime
import { processUser } from "./utils"; // Kept at runtime

// Mixed import — type and value from same module
import { type User, processUser } from "./module";
```

This prevents accidentally including type-only imports in your runtime bundle.

## Common Configurations by Project Type

### Next.js App

```jsonc
{
  "compilerOptions": {
    "target": "ES2017",
    "lib": ["dom", "dom.iterable", "esnext"],
    "module": "ESNext",
    "moduleResolution": "bundler",
    "jsx": "preserve",
    "strict": true,
    "noEmit": true,
    "incremental": true,
    "plugins": [{ "name": "next" }],
    "paths": { "@/*": ["./src/*"] }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx"],
  "exclude": ["node_modules"]
}
```

### Node.js Library (ESM)

```jsonc
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "nodenext",
    "strict": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "outDir": "./dist",
    "rootDir": "./src"
  },
  "include": ["src"]
}
```

### React SPA (Vite)

```jsonc
{
  "compilerOptions": {
    "target": "ES2020",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "moduleResolution": "bundler",
    "jsx": "react-jsx",
    "strict": true,
    "noEmit": true,
    "skipLibCheck": true
  },
  "include": ["src"]
}
```

### NestJS Backend

```jsonc
{
  "compilerOptions": {
    "module": "commonjs",
    "declaration": true,
    "removeComments": true,
    "emitDecoratorMetadata": true,
    "experimentalDecorators": true,
    "target": "ES2021",
    "sourceMap": true,
    "outDir": "./dist",
    "baseUrl": "./",
    "incremental": true,
    "strict": true,
    "strictNullChecks": true,
    "noImplicitAny": true,
    "strictBindCallApply": true,
    "forceConsistentCasingInFileNames": true,
    "noFallthroughCasesInSwitch": true
  }
}
```

## Path Aliases

```jsonc
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"],
      "@components/*": ["./src/components/*"],
      "@utils/*": ["./src/utils/*"]
    }
  }
}
```

Note: Path aliases require bundler support (Vite, webpack) or a runtime resolver (`tsconfig-paths`). TypeScript only resolves types — it doesn't rewrite paths in emitted JS.

## Project References (Monorepos)

For monorepos with multiple packages:

```jsonc
// Root tsconfig.json
{
  "files": [],
  "references": [
    { "path": "./packages/core" },
    { "path": "./packages/api" },
    { "path": "./packages/web" }
  ]
}

// packages/core/tsconfig.json
{
  "compilerOptions": {
    "composite": true,
    "outDir": "./dist",
    "rootDir": "./src"
  },
  "include": ["src"]
}

// packages/api/tsconfig.json
{
  "compilerOptions": {
    "composite": true,
    "outDir": "./dist",
    "rootDir": "./src"
  },
  "references": [{ "path": "../core" }],
  "include": ["src"]
}
```

Build with `tsc --build` for incremental compilation across packages.

## Key Flags Reference

| Flag | Purpose | Recommended |
|------|---------|-------------|
| `strict` | All strict checks | Always `true` |
| `noUncheckedIndexedAccess` | Index access returns `T \| undefined` | `true` for safety |
| `noEmit` | Don't emit JS (use external compiler) | `true` with bundlers |
| `skipLibCheck` | Skip type-checking `.d.ts` files | `true` (faster builds) |
| `isolatedModules` | Ensure each file can be transpiled alone | `true` (required by most bundlers) |
| `incremental` | Cache type-check results | `true` for faster rebuilds |
| `composite` | Enable project references | Required for monorepos |
| `declaration` | Emit `.d.ts` files | `true` for libraries |
| `erasableSyntaxOnly` | Only erasable TS syntax (5.8+) | `true` for Node `--strip-types` |
