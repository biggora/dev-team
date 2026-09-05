# Codex static contracts

Run `node --test evals/codex/contracts.test.cjs` (also exposed by `npm run test:codex`). Node.js 18 or later; no dependencies.

These are **static instruction and package checks**, not model-backed orchestration tests. The package test checks file availability from an unrelated working directory and rejects an incomplete package; it does not execute the adapter.

| Criteria | Checks |
|---|---|
| CX-002 | All routes, explicit-only metadata, package completeness, source/project paths, declared tool schema, isolation, lifecycle and reviewer nonmutation instructions |
| CX-003 | SHA-256 of the original fourteen Claude skill bodies/frontmatter after removing only one bounded Codex entry; unchanged agent definitions, manifests, continuity and Claude model runners |
| CX-004 | Canonical debate and Evidence ownership, limits, combined PRD/catalogue gate, unaffected adversarial cases and retained material-restart expectations |

`baseline.json` is anchored to commit `13f7469a171505f4a4a378d1f56356f487c212ee`, captured before this change. Only CRLF/LF normalization is permitted. It is deliberately independent of the current Git HEAD and must not be regenerated just to pass a test. Intentional future changes to the common workflow require separate review of the corresponding preservation baseline.

The single allowed routing insertion is delimited by `<!-- codex-entry:start -->` and `<!-- codex-entry:end -->`, followed by one blank line. The original content outside that insertion must remain unchanged.

Not covered here: actual natural-language activation, tool execution in different Codex clients, inherited history, successful review/rework, model compliance with read-only constraints, live interruption/resume, installed-cache loading, and Claude behavioral parity. These require separately recorded live runs; static green leaves them UNVERIFIED.
