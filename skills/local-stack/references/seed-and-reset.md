# Reference: Seed, Reset, and Test Isolation

## Overview

Two questions that are easy to conflate:

- **Seeding** — how the stack acquires the data it needs to be usable at all (reference
  tables, a demo tenant, a login the user can click through in a demo).
- **Isolation** — how one test stops leaking state into the next.

They have different owners and different lifetimes. Seeding runs when the stack is created;
isolation runs around every test.

---

## Seed data is idempotent code in the repo

A seed is a committed script that can run any number of times and always leaves the same
result. Upsert on a stable key; never blind-insert.

```ts
// db/seed.ts — run with: npm run seed
await db.tenant.upsert({
  where: { slug: "acme" },
  update: {},
  create: { slug: "acme", name: "Acme Inc" },
});
```

```python
# db/seed.py — run with: python -m db.seed
Tenant.objects.update_or_create(slug="acme", defaults={"name": "Acme Inc"})
```

**Rules**
- Stable keys, not autoincrement ids. A seed that assumes `id=1` breaks the second time it
  runs and on every reordering.
- Development credentials only, and the same fixed values everywhere so a demo script can
  reference them.
- Volume of data small enough that reseeding is fast; large datasets belong in a separate,
  optional performance-fixture script.
- **Never seed by hand.** Data typed into a GUI cannot be recreated after `down -v`, which
  makes teardown unsafe and quietly kills the reset story.

**Wiring it in.** For a fresh volume, `docker-entrypoint-initdb.d` (Postgres, MySQL, Mongo)
runs SQL/JS at first boot — good for extensions and reference tables, but it does not re-run
afterwards. Application-level seeds belong in a `seed` script the developer and the test
setup both invoke explicitly, so the behaviour does not depend on whether the volume happened
to be empty.

---

## Migrations versus fixtures

Keep them separate and keep the order fixed.

| | Migrations | Fixtures / seeds |
|---|---|---|
| Owns | Schema | Rows |
| Applies to | Every environment, including production | Local and test only |
| Versioned | Yes, ordered and immutable once merged | No, rewritable |
| Run | Before seeds, always | After migrations |

Never let a migration insert test data, and never let a seed alter schema. A migration that
seeds rows makes production carry demo tenants; a seed that alters schema means the schema
depends on run order. Test setup is always: start stack → migrate → seed.

---

## Isolation strategies, fastest first

### 1. Transaction rollback per test (default)

Open a transaction in setup, run the test inside it, roll back in teardown. Nothing is ever
committed, so tests are independent and reseeding is unnecessary. Typically single-digit
milliseconds per test.

```python
# pytest
@pytest.fixture
def db_session(connection):
    tx = connection.begin()
    session = Session(bind=connection)
    yield session
    session.close()
    tx.rollback()
```

Use it whenever the code under test shares the test's connection.

**Limits:** it does not work when the application opens its own connection (a real HTTP
request through a server process, a Playwright e2e run), or when the code under test commits
or uses its own transactions in a way the wrapper cannot nest. Do not fight this — fall to
strategy 2.

### 2. Truncate and reseed

Between tests, truncate the mutable tables and re-run the seed. Tens of milliseconds.

```sql
TRUNCATE TABLE orders, order_items, users RESTART IDENTITY CASCADE;
```

Truncate every table in one statement so foreign keys do not force an ordering, and
`RESTART IDENTITY` so ids are deterministic. Preserve migration-bookkeeping tables. This is
the right default for API-level and e2e tests.

For Redis, the equivalent is `FLUSHDB` against the **test database index only**
(`redis://localhost:6379/1`) — never `FLUSHALL`.

### 3. Recreate the container (enablement only)

`docker compose down -v && docker compose up -d --wait`. Tens of seconds. This is the
enablement proof — it demonstrates the stack rebuilds from nothing — and it is far too slow
for per-test or per-suite isolation. Reaching for it inside a test run is a sign that
strategy 1 or 2 was skipped.

---

## The stack stays up across slices

Bring the stack up once and leave it running for the whole session. Tearing it down between
slices costs a minute of boot per slice, discards warm caches, and buys nothing — isolation
is already handled at strategies 1 and 2, which are inside the database, not around the
container.

Recreate the stack only when: the compose file or an image tag changed, a migration cannot be
applied forward, the enablement proof is being re-run, or the work is finished.

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Tests pass alone, fail in a suite | Leaked state between tests | Adopt strategy 1; fall back to 2 |
| Test order changes results | Shared mutable rows | Truncate and reseed per test |
| Seed fails on second run | Blind inserts | Upsert on a stable key |
| Rollback strategy silently commits | App opened its own connection | Use truncate-and-reseed for that suite |
| Reseed leaves stale ids | Sequences not reset | Add `RESTART IDENTITY` |
| Data lost that nobody could recreate | Hand-seeded through a GUI | Move the seed into a committed script |
