---
name: layout-logical-properties
description: Writing-mode-aware logical property utilities added in Tailwind CSS v4.2 — inline/block sizing, spacing, and inset
---

# Logical Property Utilities (v4.2+)

Writing-mode-aware utilities for internationalization and vertical text support. These use CSS logical properties that adapt to the document's writing mode (LTR, RTL, vertical). Added in Tailwind CSS v4.2.

## Logical Sizing

Size elements relative to the writing mode:

```html
<!-- Inline size (width in LTR, height in vertical writing) -->
<div class="inline-full">Full inline size</div>
<div class="inline-80">Fixed inline size</div>
<div class="min-inline-0">Minimum inline size</div>
<div class="max-inline-lg">Maximum inline size</div>

<!-- Block size (height in LTR, width in vertical writing) -->
<div class="block-screen">Full block size (viewport)</div>
<div class="block-64">Fixed block size</div>
<div class="min-block-0">Minimum block size</div>
<div class="max-block-full">Maximum block size</div>
```

## Block Spacing

Spacing utilities for block-start and block-end:

```html
<!-- Block padding -->
<div class="pbs-4">Padding block-start: 1rem</div>
<div class="pbe-8">Padding block-end: 2rem</div>

<!-- Block margin -->
<div class="mbs-4">Margin block-start: 1rem</div>
<div class="mbe-8">Margin block-end: 2rem</div>

<!-- Scroll padding/margin -->
<div class="scroll-pbs-4">Scroll padding block-start</div>
<div class="scroll-mbs-4">Scroll margin block-start</div>
```

## Block Borders

Border utilities for block direction:

```html
<div class="border-bs border-bs-gray-200">Border block-start</div>
<div class="border-be-2 border-be-blue-500">Border block-end (2px blue)</div>
```

## Logical Inset

Position elements using logical directions:

```html
<!-- Inline positioning (replaces start-*/end-*) -->
<div class="absolute inset-s-0">Inline-start: 0</div>
<div class="absolute inset-e-4">Inline-end: 1rem</div>

<!-- Block positioning -->
<div class="absolute inset-bs-0">Block-start: 0</div>
<div class="absolute inset-be-4">Block-end: 1rem</div>
```

> **Deprecation note:** `start-*` and `end-*` utilities are deprecated in v4.2. Use `inset-s-*` and `inset-e-*` instead.

## When to Use Logical Properties

- **Internationalization (i18n):** When your app supports RTL languages (Arabic, Hebrew)
- **Vertical writing modes:** For CJK vertical text layouts
- **Future-proofing:** Logical properties adapt automatically to any writing mode

For Western-only LTR layouts, physical properties (`w-*`, `h-*`, `pt-*`, `mb-*`) remain perfectly fine.

## Key Points

- `inline-*` = width in LTR, height in vertical writing
- `block-*` = height in LTR, width in vertical writing
- `pbs-*`/`pbe-*` = padding block-start/end
- `mbs-*`/`mbe-*` = margin block-start/end
- `border-bs-*`/`border-be-*` = border block-start/end
- `inset-s-*`/`inset-e-*` replace deprecated `start-*`/`end-*`
- All use the spacing scale like regular spacing utilities

<!--
Source references:
- https://github.com/tailwindlabs/tailwindcss/releases/tag/v4.2.0
-->
