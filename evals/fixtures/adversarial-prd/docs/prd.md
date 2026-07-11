# Seeded PRD for adversarial evaluation

Original request: provide email reminders for a single-tenant internal task list. SMS is explicitly excluded. Operations wants reminders sent immediately; Compliance requires a 24-hour approval hold.

## Functional Requirements

- FR-001: Send reminders immediately after task creation.
- FR-002: Hold every outbound reminder for Compliance approval for 24 hours. <!-- DEFECT: contradiction -->
- FR-003: Send SMS reminders even though the request excludes SMS. <!-- DEFECT: invented-requirement -->

Acceptance criteria:

- AC-001: Reminders should work well for users. <!-- DEFECT: unexecutable-ac -->

## Dependencies

- Delivery depends on an unspecified messaging provider with no owner, contract, or validation plan. <!-- DEFECT: unknown-dependency -->

## Stakeholders

- Operations requires immediate delivery while Compliance requires a 24-hour hold; no decision owner or resolution exists. <!-- DEFECT: stakeholder-conflict -->

<!-- DEFECT: missing-nfr — no measurable reliability, latency, security, accessibility, or privacy requirement exists. -->
