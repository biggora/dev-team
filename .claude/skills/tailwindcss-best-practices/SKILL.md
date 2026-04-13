---
name: tailwindcss-best-practices
description: Tailwind CSS v4.x utility-first CSS framework best practices. Use when styling web applications with utility classes, building responsive layouts, customizing design systems with @theme variables, migrating from v3 to v4, configuring dark mode, creating custom utilities with @utility, or working with any Tailwind CSS v4 features. This skill covers the full v4.x line through v4.2 including text shadows, masks, logical properties, and source detection. Use this skill even for simple Tailwind questions — v4 changed many class names and configuration patterns that trip people up.
---

# Tailwind CSS v4.x Best Practices

> Covers Tailwind CSS v4.0 through v4.2.2 (latest stable as of March 2026). Always check the official docs at https://tailwindcss.com/docs for the latest.

Tailwind CSS is a utility-first CSS framework. Instead of writing custom CSS, you compose designs using utility classes directly in your markup. Tailwind v4 introduced CSS-first configuration with `@theme` variables, `@utility` for custom utilities, and `@custom-variant` for custom variants — replacing the old `tailwind.config.js` approach entirely.

## Critical v4 Migration Gotchas

These are the most common mistakes when working with Tailwind v4. If you're migrating from v3 or using v4 for the first time, read the [upgrade guide](references/features-upgrade.md) — but here are the top trip-ups:

| v3 (old) | v4 (correct) | Why it changed |
|----------|-------------|----------------|
| `!bg-red-500` | `bg-red-500!` | Important modifier moved from prefix to suffix |
| `bg-opacity-75` | `bg-red-500/75` | Opacity modifiers removed; use slash syntax on the color |
| `shadow` | `shadow-sm` | Shadow scale shifted down one step |
| `shadow-sm` | `shadow-xs` | Shadow scale shifted down one step |
| `rounded` | `rounded-sm` | Border radius scale shifted down one step |
| `rounded-sm` | `rounded-xs` | Border radius scale shifted down one step |
| `ring` | `ring-3` | Default ring width changed from 3px to 1px |
| `outline-none` | `outline-hidden` | Renamed for clarity |
| `flex-shrink-0` | `shrink-0` | Shorter alias is now the only form |
| `flex-grow` | `grow` | Shorter alias is now the only form |
| `overflow-ellipsis` | `text-ellipsis` | Renamed for consistency |
| `blur` | `blur-sm` | Blur scale shifted down one step |
| `@tailwind base/components/utilities` | `@import "tailwindcss"` | Single CSS import replaces three directives |
| `tailwind.config.js` | `@theme { }` in CSS | CSS-first configuration replaces JS config |
| `darkMode: 'class'` | `@custom-variant dark (&:where(.dark, .dark *));` | Dark mode config moves to CSS |
| `bg-[--var]` | `bg-(--var)` | CSS variable arbitrary values use parentheses |
| `theme(screens.xl)` | `theme(--breakpoint-xl)` | Theme function uses CSS variable names |
| `@layer utilities { }` | `@utility name { }` | Custom utilities use dedicated directive |
| `start-*` / `end-*` | `inset-s-*` / `inset-e-*` | Deprecated in v4.2 |

## Core References

| Topic | Description | Reference |
|-------|-------------|-----------|
| Installation | Vite, PostCSS, Webpack, CLI, and CDN setup | [core-installation](references/core-installation.md) |
| Utility Classes | Understanding Tailwind's utility-first approach | [core-utility-classes](references/core-utility-classes.md) |
| Theme Variables | Design tokens, `@theme` directive, theme variable namespaces | [core-theme](references/core-theme.md) |
| Responsive Design | Mobile-first breakpoints, responsive variants, container queries | [core-responsive](references/core-responsive.md) |
| Variants | Conditional styling with state, pseudo-class, media query, and pointer variants | [core-variants](references/core-variants.md) |
| Preflight | Tailwind's base styles and how to extend or disable them | [core-preflight](references/core-preflight.md) |
| Source Detection | How Tailwind detects classes, `@source`, `@source not`, `@source inline()` | [core-source-detection](references/core-source-detection.md) |

## Layout

### Display & Flexbox & Grid

| Topic | Description | Reference |
|-------|-------------|-----------|
| Display | flex, grid, block, inline, hidden, sr-only, flow-root, contents | [layout-display](references/layout-display.md) |
| Flexbox | flex-direction, justify, items, gap, grow, shrink, wrap, order | [layout-flexbox](references/layout-flexbox.md) |
| Grid | grid-cols, grid-rows, gap, place-items, col-span, row-span, subgrid | [layout-grid](references/layout-grid.md) |
| Aspect Ratio | Controlling element aspect ratio for responsive media | [layout-aspect-ratio](references/layout-aspect-ratio.md) |
| Columns | Multi-column layout for magazine-style or masonry layouts | [layout-columns](references/layout-columns.md) |

### Positioning

| Topic | Description | Reference |
|-------|-------------|-----------|
| Position | Controlling element positioning with static, relative, absolute, fixed, and sticky | [layout-position](references/layout-position.md) |
| Inset | Placement of positioned elements with inset, logical inset (`inset-s-*`, `inset-bs-*`), and deprecated `start-*`/`end-*` | [layout-inset](references/layout-inset.md) |

### Sizing

| Topic | Description | Reference |
|-------|-------------|-----------|
| Width | Setting element width with spacing scale, fractions, container sizes, viewport units | [layout-width](references/layout-width.md) |
| Height | Setting element height with spacing scale, fractions, viewport units | [layout-height](references/layout-height.md) |
| Min & Max Sizing | min-width, max-width, min-height, max-height constraints | [layout-min-max-sizing](references/layout-min-max-sizing.md) |
| Logical Sizing | Writing-mode-aware sizing: `inline-*`, `block-*`, `min-inline-*`, `max-block-*` (v4.2) | [layout-logical-properties](references/layout-logical-properties.md) |

### Spacing

| Topic | Description | Reference |
|-------|-------------|-----------|
| Margin | Margins with spacing scale, negative values, logical properties (`mbs-*`, `mbe-*`) | [layout-margin](references/layout-margin.md) |
| Padding | Padding with spacing scale, logical properties (`pbs-*`, `pbe-*`) | [layout-padding](references/layout-padding.md) |

### Overflow

| Topic | Description | Reference |
|-------|-------------|-----------|
| Overflow | Controlling how elements handle content that overflows | [layout-overflow](references/layout-overflow.md) |

### Images & Replaced Elements

| Topic | Description | Reference |
|-------|-------------|-----------|
| Object Fit & Position | Controlling how images and video are resized and positioned | [layout-object-fit-position](references/layout-object-fit-position.md) |

### Tables

| Topic | Description | Reference |
|-------|-------------|-----------|
| Table Layout | border-collapse, table-auto, table-fixed | [layout-tables](references/layout-tables.md) |

## Transforms

| Topic | Description | Reference |
|-------|-------------|-----------|
| Transform Base | Base transform utilities, hardware acceleration, custom transform values | [transform-base](references/transform-base.md) |
| Translate | Translating elements on x, y, z axes with spacing scale and percentages | [transform-translate](references/transform-translate.md) |
| Rotate | Rotating elements in 2D and 3D space | [transform-rotate](references/transform-rotate.md) |
| Scale | Scaling elements uniformly or on specific axes | [transform-scale](references/transform-scale.md) |
| Skew | Skewing elements on x and y axes | [transform-skew](references/transform-skew.md) |

## Typography

| Topic | Description | Reference |
|-------|-------------|-----------|
| Font & Text | Font size, weight, color, line-height, letter-spacing, decoration, truncate, `wrap-break-word`, `wrap-anywhere` | [typography-font-text](references/typography-font-text.md) |
| Text Align | Controlling text alignment with left, center, right, justify | [typography-text-align](references/typography-text-align.md) |
| List Style | list-style-type, list-style-position for bullets and markers | [typography-list-style](references/typography-list-style.md) |

## Visual

| Topic | Description | Reference |
|-------|-------------|-----------|
| Background | Background color, gradient, image, size, position | [visual-background](references/visual-background.md) |
| Border | Border width, color, radius, divide, ring, block border utilities (`border-bs-*`, `border-be-*`) | [visual-border](references/visual-border.md) |
| Effects | Box shadow, opacity, mix-blend, backdrop-blur, filter, colored drop shadows | [visual-effects](references/visual-effects.md) |
| SVG | fill, stroke, stroke-width for SVG and icon styling | [visual-svg](references/visual-svg.md) |
| Text Shadow | Text shadow sizes, colors, and opacity modifiers (v4.1) | [effects-text-shadow](references/effects-text-shadow.md) |
| Mask | Composable mask utilities with gradient and radial masks (v4.1) | [effects-mask](references/effects-mask.md) |

## Effects & Interactivity

| Topic | Description | Reference |
|-------|-------------|-----------|
| Transition & Animation | CSS transitions, animation keyframes, reduced motion | [effects-transition-animation](references/effects-transition-animation.md) |
| Visibility & Interactivity | Visibility, cursor, pointer-events, user-select, z-index | [effects-visibility-interactivity](references/effects-visibility-interactivity.md) |
| Form Controls | accent-color, appearance, caret-color, resize | [effects-form-controls](references/effects-form-controls.md) |
| Scroll Snap | scroll-snap-type, scroll-snap-align for carousels | [effects-scroll-snap](references/effects-scroll-snap.md) |

## Features

### Dark Mode

| Topic | Description | Reference |
|-------|-------------|-----------|
| Dark Mode | Dark mode with `dark:` variant, `@custom-variant`, class and data-attribute strategies | [features-dark-mode](references/features-dark-mode.md) |

### Migration

| Topic | Description | Reference |
|-------|-------------|-----------|
| Upgrade Guide | Migrating from v3 to v4, all renamed/removed utilities, scale shifts, config migration | [features-upgrade](references/features-upgrade.md) |

### Customization

| Topic | Description | Reference |
|-------|-------------|-----------|
| Custom Styles | Adding custom styles, utilities with `@utility`, variants with `@custom-variant`, arbitrary values | [features-custom-styles](references/features-custom-styles.md) |
| Functions & Directives | Tailwind's CSS directives (`@theme`, `@utility`, `@custom-variant`, `@source`) and functions | [features-functions-directives](references/features-functions-directives.md) |
| Content Detection | How Tailwind detects classes, `@source` configuration, safelisting with `@source inline()` | [features-content-detection](references/features-content-detection.md) |

## Best Practices

| Topic | Description | Reference |
|-------|-------------|-----------|
| Utility Patterns | Managing duplication, conflicts, important modifier, when to use components | [best-practices-utility-patterns](references/best-practices-utility-patterns.md) |

## Key Recommendations

- **Use utility classes directly in markup** — compose designs by combining utilities
- **Customize with `@theme` directive** — define design tokens as CSS variables, not in JS config
- **Mobile-first responsive design** — unprefixed utilities for mobile, prefixed for breakpoints
- **Use complete class names** — never construct classes dynamically with string interpolation
- **Leverage variants** — stack variants for complex conditional styling (`dark:md:hover:bg-blue-600`)
- **Prefer CSS-first configuration** — use `@theme`, `@utility`, and `@custom-variant` over JavaScript configs
- **Use oklch for custom colors** — Tailwind v4 defaults to oklch; prefer it for perceptual uniformity
- **Use rem for custom breakpoints** — e.g., `--breakpoint-3xl: 90rem` not `1440px`
- **Know the scale shifts** — shadow, rounded, and blur all shifted down one step in v4
- **Use `@custom-variant`** (not `@variant`) — for defining custom variants like class-based dark mode
