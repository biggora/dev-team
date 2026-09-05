# Reference: Wiring Tests to the Local Stack

## Overview

The stack exists so that verification runs against real services. This file covers the
mechanics: waiting for readiness, configuring connections, splitting the suite so claims are
checkable, and capturing evidence.

---

## Wait for readiness, never sleep

```bash
docker compose up -d --wait
```

`--wait` blocks until every service with a health check reports healthy, and exits non-zero
otherwise. Its exit code is the readiness signal the test command depends on.

```json
{
  "scripts": {
    "stack:up": "docker compose up -d --wait",
    "stack:down": "docker compose down -v",
    "test:unit": "vitest run --project unit",
    "test:integration": "npm run stack:up && vitest run --project integration",
    "test:e2e": "npm run stack:up && playwright test",
    "test:all": "npm run test:unit && npm run test:integration && npm run test:e2e"
  }
}
```

`sleep 10` is not an alternative. It is too short on a cold machine and wasteful on a warm
one, and its real cost is that it conceals a missing health check — the thing that would have
made the wait correct.

---

## Env-var-driven configuration with `.env.test`

Connection details never appear in test code. `.env.example` documents them; `.env.test`
holds the values the suite uses; both are committed (they contain development-only
credentials). `.env` is not committed.

```
# .env.test
DATABASE_URL=postgresql://app:devpassword@localhost:5432/app_test
REDIS_URL=redis://localhost:6379/1
S3_ENDPOINT=http://localhost:9000
S3_BUCKET=app-uploads
AWS_ACCESS_KEY_ID=minioadmin
AWS_SECRET_ACCESS_KEY=devpassword
SMTP_HOST=localhost
SMTP_PORT=1025
MAILPIT_URL=http://localhost:8025
```

A separate database (`app_test`) and a separate Redis index (`/1`) keep a test reset from
destroying the developer's working data on the same stack.

Node (Vitest): `setupFiles` loads it.

```ts
// vitest.config.ts
import { config } from "dotenv";
config({ path: ".env.test" });
```

Python (pytest): load it in `conftest.py`.

```python
from dotenv import load_dotenv
load_dotenv(".env.test", override=True)
```

---

## Split the suite so the claim is checkable

"The full suite is green against the real stack" is only verifiable if the commands are
distinguishable. Three tiers:

| Tier | Talks to the stack | Command |
|---|---|---|
| unit | No — pure logic, no I/O | `test:unit` / `pytest -m unit` |
| integration | Yes — real DB, cache, queue, S3 | `test:integration` / `pytest -m integration` |
| e2e | Yes — through the running application | `test:e2e` / `pytest -m e2e` |

Node: Vitest projects or Jest `projects`, with directory-based selection
(`tests/unit`, `tests/integration`, `tests/e2e`).
Python: pytest markers registered in `pyproject.toml` and selected with `-m`.

If a test in the integration tier still mocks the database, it is a unit test wearing the
wrong label, and it silently weakens the coverage claim. Move it.

---

## Node examples

Integration, through the HTTP layer with supertest:

```ts
import request from "supertest";
import { app } from "../src/app";

it("persists an order and returns it", async () => {
  const created = await request(app)
    .post("/orders")
    .send({ sku: "ABC", qty: 2 })
    .expect(201);

  // Real round-trip: read it back from the real database through the API.
  await request(app).get(`/orders/${created.body.id}`).expect(200);
});
```

E2E with Playwright — start the app against the stack, not against fixtures:

```ts
// playwright.config.ts
export default defineConfig({
  webServer: {
    command: "npm run start:test",   // reads .env.test, so it hits the containers
    url: "http://localhost:3000",
    reuseExistingServer: !process.env.CI,
  },
});
```

---

## Python examples

```python
# conftest.py
@pytest.fixture(scope="session")
def engine():
    return create_engine(os.environ["DATABASE_URL"])   # real Postgres container

@pytest.fixture
def client(db_session):
    from app.main import app
    return TestClient(app)
```

```python
@pytest.mark.integration
def test_creates_and_reads_order(client):
    created = client.post("/orders", json={"sku": "ABC", "qty": 2})
    assert created.status_code == 201
    assert client.get(f"/orders/{created.json()['id']}").status_code == 200
```

`TestClient` exercises the real application against the real database; the only thing it
skips is the network hop to the ASGI server.

---

## What "100% functional tests green against the real stack" means

All four conditions, in the same run:

1. `docker compose up -d --wait` exited 0, and `docker compose ps` shows every service
   `healthy`.
2. The integration and e2e tiers ran with `.env.test` pointing at those containers.
3. Zero failures, zero errors, and **zero skipped tests in those tiers** — a skip is not a
   pass. A skipped test is reported as a gap, not counted as green.
4. No test in those tiers mocked a dependency that has a container.

Anything short of all four is `DONE_WITH_CONCERNS` at best, with the shortfall named.

---

## Capturing evidence

Stack health and test results are captured together, in that order, in one session:

```bash
docker compose ps --format "table {{.Service}}\t{{.Status}}"
npm run test:integration
```

```
SERVICE        STATUS
postgres       Up 4 minutes (healthy)
redis          Up 4 minutes (healthy)
mailpit        Up 4 minutes (healthy)

Test Files  12 passed (12)
     Tests  87 passed (87)
```

Both blocks go in the report's Evidence field with their exit codes. Health output without
test output proves only enablement; test output without health output leaves it unproven that
the tests hit containers rather than mocks.

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| First test fails, later tests pass | Suite started before services were ready | `up -d --wait`, not `sleep` |
| Tests wipe development data | Same database as development | Point `.env.test` at `app_test` and Redis index 1 |
| Suite green but the feature is broken | Integration tier still mocks the dependency | Move it to unit, or use the container |
| Tests pass locally, fail after `down -v` | Migrations or seeds not part of setup | Run migrate + seed in the test setup path |
| `--wait` times out | Health check wrong or `start_period` too short | Fix the check; raise the grace window |
| Skipped tests counted as passing | Skips read as green in summaries | Report skips as gaps in Evidence |
