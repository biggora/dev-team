# Email Reminder PRD

## Source and scope

The original request adds approved email reminders to a single-tenant internal task list. SMS is out of scope.

## Scope alternatives and trade-offs

- Alternative A — immediate delivery without approval: rejected because it conflicts with the original request's explicit approval requirement. It minimizes latency but violates the stated compliance boundary.
- Alternative B — queue email and release it after approval: selected because it satisfies the original request. The accepted trade-off is approval latency in exchange for compliance control.
- Alternative C — email plus SMS: rejected because the original request explicitly excludes SMS and supplies no evidence for expanding channel scope.

## Assumptions and decisions

- Compliance approval is required before delivery.
- Reminder records are retained for 30 days.
- Residual provider outage risk is mitigated by retry with an operator-visible failure state.

## Negative scenarios

- An unapproved reminder reaches its due time: no outbound request is made and the reminder remains pending.
- The provider times out: retry is bounded to three attempts, then Operations receives a visible failure state.
- A retry follows an accepted provider request: the same reminder key prevents duplicate delivery.
- A delivery record reaches 30 days: it is deleted under the stated retention decision.

## Functional requirements

- FR-001: Queue one email reminder after task creation and release it only after Compliance approval.
- FR-002: Never send SMS.

## Acceptance criteria

- AC-001: Given a task with an approved reminder, when its due time arrives, then exactly one email is submitted to the configured provider within 60 seconds.
- AC-002: Given a reminder without approval, when its due time arrives, then no outbound message is submitted and the reminder remains pending.
- AC-003: Given provider failure, when delivery is attempted, then the system retries three times and exposes the final failure to Operations.

## Non-functional requirements

- Reliability: at least 99.9% of approved reminders are submitted within the stated latency target, measured monthly.
- Security and privacy: provider credentials remain secret; reminder payloads contain task ID and recipient email only; delivery records expire after 30 days.

## Dependency

The messaging provider contract and sandbox verification are owned by Operations before implementation begins.
