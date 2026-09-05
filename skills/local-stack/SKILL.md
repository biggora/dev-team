---
name: local-stack
description: >
  This skill should be used when the user or an agent needs to run an application's
  external dependencies locally in containers — "docker-compose", "local stack",
  "spin up postgres", "test against a real database", "mailhog", "mailpit", "minio",
  "localstack", "stripe-mock", "wiremock", "service emulator", "healthcheck",
  "seed data", "reset the database", "integration tests against containers" — or
  when writing, reviewing, or debugging a docker-compose.yml, a development
  Dockerfile, or .env.example for local verification.
metadata:
  priority: 7
  pathPatterns:
    - "**/docker-compose*.y*ml"
    - "**/Dockerfile*"
    - "**/.env.example"
    - "**/.env.test"
    - "**/.dockerignore"
    - "**/docker-entrypoint-initdb.d/*"
  bashPatterns:
    - "docker compose *"
    - "docker-compose *"
  promptSignals:
    phrases:
      - "local stack"
      - "docker-compose"
      - "spin up postgres"
      - "test against a real database"
      - "mailhog"
      - "mailpit"
      - "minio"
      - "localstack"
      - "stripe-mock"
      - "wiremock"
      - "service emulator"
      - "healthcheck"
      - "seed data"
      - "reset the database"
      - "integration tests against containers"
    allOf:
      - ["docker", "compose"]
      - ["local", "stack"]
    minScore: 6
---

# Local Stack

## Overview

A **local stack** is every external runtime dependency of the application — database, cache,
queue, SMTP, object storage, third-party APIs — running in containers on the developer's
machine, brought up by a single command from a clean checkout.

The stack carries two distinct obligations. Conflating them is the single largest source of
confusion, so keep them separate in your head and in your reports:

- **Enablement** — the stack itself is proven healthy from a clean state. This happens
  *before there is an application to test*. The evidence is `docker compose up -d --wait`
  succeeding on a machine with no prior volumes, plus `docker compose ps` showing every
  service `healthy`. Nothing about the application is proven here.
- **Proof** — every later verification (integration tests, e2e tests, manual demos) runs
  against that stack instead of against mocks. The evidence is the test suite output plus
  the stack health output captured at the same time.

Enablement is a one-time gate owned by the `devops-engineer` agent. Proof is a recurring
obligation of the `tester` agent, repeated on every slice.

## Decision Procedure

For every external dependency the application talks to, walk this ladder in order and stop
at the first rung that applies:

1. **Real service in a container.** Postgres, MySQL, Mongo, Redis, RabbitMQ, Kafka,
   Elasticsearch all ship official images. Use the real thing.
2. **Containerized emulator.** The real service cannot run locally (AWS, Stripe, a partner
   SaaS). Use LocalStack, MinIO, stripe-mock, WireMock, or Keycloak.
3. **HALT.** No container and no emulator exists. The agent reports `BLOCKED`, the
   coordinator asks the user (sandbox credentials? a recorded contract? a waiver?), and every
   acceptance criterion depending on it stays **UNVERIFIED** until the user answers.

**Never substitute a mock for something that has a container.** An in-memory SQLite stand-in
for Postgres, a fake Redis object, a stubbed S3 client — these hide exactly the failures the
integration test exists to catch (SQL dialect, transaction semantics, serialization,
timeouts). A mock is acceptable only at rung 3, and only with a recorded user waiver named in
the ledger.

## The Compose Contract

Eight non-negotiables. A stack that fails any one of them is not done.

- [ ] **Idempotent lifecycle.** `docker compose up -d --wait` succeeds from a clean checkout
      *and* when the stack is already warm. `docker compose down -v` removes every volume,
      leaving nothing behind.
- [ ] **Health check on every service**, and every dependent service declares
      `depends_on: { <service>: { condition: service_healthy } }`.
- [ ] **Pinned image tags.** Never `latest`, never a bare image name. A major-version pin
      (`postgres:16-alpine`) is the floor; pin the minor when the project needs it.
- [ ] **No production credentials.** Development passwords only, and `.env` is in
      `.gitignore` and never committed.
- [ ] **Complete `.env.example`.** Every variable the stack or the app reads is listed with
      a working development default and a one-line comment.
- [ ] **Deterministic host ports.** Fixed, documented ports, with exactly one documented
      override mechanism (e.g. `POSTGRES_PORT=5432` in `.env`) for developers with a
      conflict.
- [ ] **Seed data as idempotent code in the repo** — a migration, a script, or an init
      volume. Re-running it must not duplicate rows or fail.
- [ ] **Teardown-and-recreate proof.** `down -v` then `up -d --wait`, twice, both times
      healthy, with zero manual steps in between. Capture the output; this is the
      enablement evidence.

## Health Checks and `--wait`

`docker compose up -d` returns when containers are *started*, not when the services inside
them are *ready*. Postgres in particular starts, runs its first-boot initialization, restarts
itself, and only then accepts connections. Following `up -d` with `sleep 10` is a defect: too
short on a cold machine (connection refused, flaky failures), too long on a warm one, and it
hides the real problem — the missing health check.

Declare a `healthcheck` on every service and start the stack with `up -d --wait`. Compose
then blocks until every service reports healthy and exits non-zero if any does not. That exit
code is the enablement evidence.

| Service | `healthcheck.test` | interval / start_period |
|---|---|---|
| postgres | `["CMD-SHELL", "pg_isready -U app -d app_dev"]` | 5s / 10s |
| mysql | `["CMD-SHELL", "mysqladmin ping -h 127.0.0.1 -uroot -p$$MYSQL_ROOT_PASSWORD"]` | 5s / 20s |
| mongo | `["CMD-SHELL", "mongosh --quiet --eval 'db.adminCommand({ping:1}).ok'"]` | 5s / 15s |
| redis | `["CMD", "redis-cli", "ping"]` | 5s / 5s |
| rabbitmq | `["CMD", "rabbitmq-diagnostics", "-q", "check_running"]` | 10s / 30s |
| kafka | `["CMD-SHELL", "/opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list"]` | 10s / 30s |
| elasticsearch | `["CMD-SHELL", "curl -fs http://localhost:9200/_cluster/health \| grep -qE 'green\|yellow'"]` | 10s / 40s |
| minio | `["CMD-SHELL", "curl -fs http://localhost:9000/minio/health/live"]` | 5s / 10s |
| mailpit | `["CMD-SHELL", "wget -q -O - http://localhost:8025/readyz \|\| exit 1"]` | 5s / 5s |

`start_period` is the grace window during which failures do not count against `retries`; size
it to the service's real cold-boot time. In compose files, `$` inside a `healthcheck` must be
escaped as `$$` or it is interpolated by Compose instead of the shell.

## Recipe Index

Full compose blocks live in `references/`, not here.

| Need | Image | Reference |
|---|---|---|
| PostgreSQL | `postgres:16-alpine` | `references/datastores.md` |
| MySQL | `mysql:8.4` | `references/datastores.md` |
| MongoDB | `mongo:7` | `references/datastores.md` |
| Redis | `redis:7-alpine` | `references/datastores.md` |
| Elasticsearch / OpenSearch | `elasticsearch:8.15.0` / `opensearchproject/opensearch:2` | `references/datastores.md` |
| RabbitMQ | `rabbitmq:3-management-alpine` | `references/messaging.md` |
| Kafka (KRaft) | `apache/kafka:3.8.0` | `references/messaging.md` |
| SMTP capture | `axllent/mailpit` (preferred) / `mailhog/mailhog` | `references/messaging.md` |
| S3-compatible object storage | `minio/minio` | `references/cloud-emulators.md` |
| AWS services (SQS, SNS, S3, DynamoDB, …) | `localstack/localstack` | `references/cloud-emulators.md` |
| Stripe | `stripe/stripe-mock` | `references/service-emulators.md` |
| Arbitrary third-party HTTP | `wiremock/wiremock` + recorded mappings | `references/service-emulators.md` |
| OIDC / identity | `quay.io/keycloak/keycloak` (dev mode) | `references/service-emulators.md` |

## Emulator Policy

Emulators are mandatory at rung 2 — not optional, not a fallback to mocks.

- **WireMock requires RECORDED contracts.** Run WireMock in record mode against the real API
  once (with sandbox credentials), commit the generated mappings, then replay from them.
  Hand-written stubs encode what the developer *believes* the API returns and therefore prove
  nothing; a test that passes against them is not evidence.
- **LocalStack covers the AWS surface** (S3, SQS, SNS, DynamoDB, Lambda, Secrets Manager and
  more in the free tier). Select only the services you need via `SERVICES`.
- **Behavioural gaps must be flagged, not papered over.** Where an emulator diverges from the
  real service, any AC that depends on the divergent behaviour is reported UNVERIFIED with
  the gap named — it is not closed by a green emulator test:
  - stripe-mock: no real webhook delivery, no signature verification against live keys, fixed
    fixture data, no state transitions between calls.
  - LocalStack: IAM policy enforcement is permissive; eventual consistency, throttling, and
    cross-region behaviour are not reproduced.
  - MinIO: no S3 lifecycle rules, no cross-region replication; presigned-URL and CORS
    semantics differ in edge cases.
  - Keycloak dev mode: no TLS, in-memory or dev database, not a production security posture.

## Seed, Reset, and Test Isolation

Seed data lives in the repo as idempotent code and is applied by the stack, never typed in by
hand. Test isolation is a separate concern from seeding: prefer transaction rollback per
test, fall back to truncate-and-reseed, and recreate the container only for enablement proof.
The stack stays up across slices. See `references/seed-and-reset.md`.

## Wiring Tests to the Stack

The test runner waits on `up -d --wait` (never `sleep`), reads connection settings from
environment variables supplied by `.env.test`, and splits unit / integration / e2e into
separately invocable commands so "the full suite is green" is a checkable claim. See
`references/test-integration.md`.

## Troubleshooting

- **Docker Desktop / WSL2 (Windows).** Docker Desktop must be running with WSL2 integration
  enabled for the distro you shell from. Keep the repository inside the WSL2 filesystem when
  bind-mount performance matters; mounts from `C:\` are markedly slower.
- **`docker compose` vs `docker-compose`.** Use Compose v2 (`docker compose`, a space). The
  legacy Python `docker-compose` binary does not support `--wait`. If `--wait` is rejected as
  an unknown flag, you are on v1 — upgrade rather than working around it.
- **Port conflicts.** `Bind for 0.0.0.0:5432 failed` means a host service (often a locally
  installed Postgres) owns the port. Stop it, or use the documented override — never
  randomize ports.
- **Slow first pull.** The first `up` pulls images and can take minutes. Run
  `docker compose pull` up front so the wait is not mistaken for a hung health check.
- **ARM vs amd64.** Some images have no arm64 build. Pin `platform: linux/amd64` on that one
  service and note the emulation cost, rather than swapping to a different image.
- **Line endings.** Shell scripts bind-mounted from Windows must be LF, not CRLF, or the
  container reports `no such file or directory`. Add `*.sh text eol=lf` to `.gitattributes`.
- **`--wait` timeouts.** If `--wait` gives up, the fix is a longer `start_period` or a
  corrected health check command — not a shorter test suite and not `sleep`.

## Anti-Patterns

- **`latest` or untagged images** — the stack silently changes under you; yesterday's green
  run is not reproducible.
- **`sleep 10` instead of `--wait`** — flaky when slow, wasteful when fast, and it conceals a
  missing health check.
- **Mocking a service that has a container** — the integration test stops testing integration.
- **A host-installed Postgres instead of a container** — unpinned version, unreproducible
  state, works only on the machine that has it.
- **Committing `.env`** — leaks credentials and hides the real configuration; commit
  `.env.example` instead.
- **Random or developer-specific host ports** — breaks every connection string and every
  teammate's setup.
- **Hand-seeded data** — clicking rows into a database means the stack cannot be recreated,
  so `down -v` becomes unsafe and the reset story dies.
- **A stack only one developer can bring up** — undocumented manual steps make the enablement
  gate unverifiable for everyone else.

## Additional Resources

For detailed recipes, consult:
- **`references/datastores.md`** — Postgres, MySQL, MongoDB, Redis, Elasticsearch/OpenSearch
- **`references/messaging.md`** — RabbitMQ, Kafka (KRaft), Mailpit/Mailhog SMTP capture
- **`references/cloud-emulators.md`** — MinIO and LocalStack
- **`references/service-emulators.md`** — stripe-mock, WireMock, Keycloak
- **`references/seed-and-reset.md`** — seeding, reset strategies, test isolation
- **`references/test-integration.md`** — wiring the test runner to the stack, evidence capture

For container hardening (non-root users, capability drops, secrets, image scanning,
`.dockerignore`), use the `security-review` skill's `infrastructure/docker.md` — this skill
covers local development stacks and deliberately does not duplicate that material.
