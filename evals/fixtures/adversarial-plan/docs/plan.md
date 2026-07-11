# Seeded execution plan for adversarial evaluation

## Tasks

1. Build the complete database layer.
2. Build the complete API layer.
3. Build the complete UI layer. <!-- DEFECT: horizontal-slices -->

No first end-to-end path is designated. <!-- DEFECT: missing-tracer-bullet -->

Only AC-001 and AC-002 are mapped; AC-003 has no task. <!-- DEFECT: uncovered-ac -->

Backend and frontend agents both write `src/shared/types.ts` in parallel. <!-- DEFECT: overlapping-scopes -->

Deploy the UI before the API contract and persistence schema exist. <!-- DEFECT: bad-dependency-order -->

Always switch to the alternate provider, regardless of observed conditions. <!-- DEFECT: unconditional-branch -->

The alternate-provider branch defines no fallback, verification, or rejoin point. <!-- DEFECT: missing-fallback -->
