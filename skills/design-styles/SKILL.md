---
name: design-styles
description: Aesthetic presets for UI design and implementation — premium parametric, high-end agency, minimalist editorial, industrial brutalist, and Stitch DESIGN.md generation. Use when a design spec or task names a visual style ("premium SaaS", "minimalist", "brutalist", "expensive-looking", "editorial") or when choosing an aesthetic direction before building UI. Pick ONE preset and load only its reference file.
---

# Design Styles

A catalog of aesthetic presets. Each preset is a self-contained directive set in `references/`. Do NOT load them all — pick the one the spec calls for and read only that file.

## How to choose

| Preset | Reference file | Use when the spec says |
|--------|----------------|------------------------|
| **Premium parametric** | `references/premium-parametric.md` | "premium SaaS", "non-generic", parametric control over variance/motion/density; general antidote to default AI look |
| **High-end agency** | `references/high-end-agency.md` | "expensive", "luxury", "Awwwards-tier", cinematic motion, haptic depth, Apple/Linear-tier polish |
| **Minimalist editorial** | `references/minimalist-editorial.md` | "clean", "editorial", "document-style", Notion/Linear-like, warm monochrome, bento grids, no gradients |
| **Industrial brutalist** | `references/industrial-brutalist.md` | "brutalist", "terminal", "blueprint", Swiss typography, data-heavy dashboards, analog degradation effects |
| **Stitch DESIGN.md** | `references/stitch-design-md.md` (example: `references/stitch-design-example.md`) | Generating a DESIGN.md file for Google Stitch screen generation |

## Rules

1. **One preset per project.** Mixing presets produces incoherent UI. If the spec is ambiguous, ask or default to premium parametric.
2. **The design spec wins.** If `docs/design.md` provides a palette and wireframes, presets refine execution quality — they never override the spec's colors, layout, or components.
3. Apply the chosen preset's constraints (typography, spacing, color, motion) consistently across every screen you produce.
