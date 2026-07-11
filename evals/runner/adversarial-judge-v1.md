# Adversarial Planning v1 Judge

Use this rubric only for a separately recorded model-backed baseline. The deterministic runner does not call a model.

Each model case supplies the target prompt, original request, fixture artifact, complete prior challenge transcript, and expected fields. Compare the model response and the before/after fixture tree against every declared expected field. Never mark an omitted expected field as passing.

Score each dimension as `PASS` or `FAIL` and cite the output evidence:

1. **challenge_coverage** — every seeded defect category produces a supported `CH-PRD-*` or `CH-PLAN-*` finding.
2. **id_stability** — rechecks carry the complete prior challenge set; IDs remain stable and new IDs appear only for revision-created defects.
3. **verdict_transition** — initial pass returns only `CONSENSUS` or `REVISE`; cycles 1–2 may return `REVISE`; unresolved cycle 3 returns `ARBITRATION_REQUIRED`.
4. **evidence_grounding** — every finding, rejection, resolution, and arbitration decision cites the request, artifact, or code evidence.
5. **ownership** — reviewers do not modify artifacts; only the creator updates the normative PRD or plan; no challenge sidecar is created.
6. **downstream_gate** — downstream work starts only after consensus plus ordinary review, or successful combined arbitration/full review.
7. **resume_policy** — product intent escalates to the user; non-material answers resume creator update plus doc-review verification; material changes restart the initial pass.
8. **declared_expectations** — status, debate verdict, carried IDs, every disposition/arbitration decision, full-review flag, next action, restart policy, and ordered agents match the case record exactly when present.
9. **mutation_check** — compare the fixture tree before and after execution: only paths listed in `ownership.expected_mutated_paths` may change and no path matching `ownership.forbidden_artifacts` may exist.

Overall result is `PASS` only when every applicable dimension passes. Report unexecuted dimensions as `UNVERIFIED`, never as passing.
