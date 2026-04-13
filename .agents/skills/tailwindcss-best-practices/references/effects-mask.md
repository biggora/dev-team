---
name: effects-mask
description: Composable mask utilities added in Tailwind CSS v4.1 — linear gradient masks, radial masks, and positioning
---

# Mask Utilities (v4.1+)

Composable mask system for creating fade, reveal, and shape effects. Added in Tailwind CSS v4.1.

## Linear Gradient Masks

Fade elements from a direction using gradient masks:

```html
<!-- Fade from top (visible at top, fades to transparent) -->
<div class="mask-t-from-50%">Content fades from top</div>

<!-- Fade from right -->
<div class="mask-r-from-30%">Content fades from right</div>

<!-- Fade from bottom -->
<div class="mask-b-from-20%">Content fades from bottom</div>

<!-- Fade from left -->
<div class="mask-l-from-40%">Content fades from left</div>
```

The `from-` value sets where the mask starts becoming transparent.

## Radial Masks

Create circular or elliptical mask effects:

```html
<!-- Radial mask with from/to values -->
<div class="mask-radial-from-70% mask-radial-to-85%">
  Circular fade from center
</div>

<!-- Position the radial mask -->
<div class="mask-radial-from-50% mask-radial-at-top-left">
  Fade from top-left corner
</div>
```

## Composing Masks

Masks can be composed — multiple mask utilities combine:

```html
<!-- Fade from both right and bottom -->
<div class="mask-r-from-80% mask-b-from-80%">
  Fades from both edges
</div>

<!-- Radial mask with directional fade -->
<div class="mask-radial-from-70% mask-radial-to-85% mask-t-from-50%">
  Complex mask composition
</div>
```

## Common Patterns

### Image with fade-out edges

```html
<div class="mask-b-from-70% overflow-hidden">
  <img src="/photo.jpg" class="w-full" />
</div>
```

### Spotlight / vignette effect

```html
<div class="mask-radial-from-60% mask-radial-to-90%">
  <img src="/hero.jpg" class="w-full" />
</div>
```

## Key Points

- Linear mask directions: `mask-t-*`, `mask-r-*`, `mask-b-*`, `mask-l-*`
- Radial masks: `mask-radial-from-*`, `mask-radial-to-*`, `mask-radial-at-*`
- Masks are composable — multiple masks combine together
- Works with all variants: `hover:mask-b-from-50%`
- The `from-` percentage controls where the fade begins

<!--
Source references:
- https://tailwindcss.com/blog/tailwindcss-v4-1
-->
