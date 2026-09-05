# Reference: Datastore Containers

## Overview

Copy-pasteable compose service blocks for the five datastores a typical application needs.
Every block satisfies the compose contract: pinned tag, health check, named volume,
deterministic host port. Declare the named volumes once at the bottom of the compose file:

```yaml
volumes:
  postgres-data:
  mysql-data:
  mongo-data:
  redis-data:
  elasticsearch-data:
```

Consumers wait on health, never on time:

```yaml
  app:
    depends_on:
      postgres:
        condition: service_healthy
```

---

## PostgreSQL

```yaml
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: devpassword
      POSTGRES_DB: app_dev
    ports:
      - "5432:5432"
    volumes:
      - postgres-data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d app_dev"]
      interval: 5s
      timeout: 5s
      retries: 10
      start_period: 10s
```

App connection: `DATABASE_URL=postgresql://app:devpassword@localhost:5432/app_dev`
(from another container, host `postgres` instead of `localhost`).

**Gotchas**
- `pg_isready` with no `-U` defaults to the OS user `root` inside the container and reports
  ready while rejecting the app's credentials. Always pass `-U` and `-d`.
- `POSTGRES_*` variables and the `/docker-entrypoint-initdb.d` scripts run **only when the
  data volume is empty**. Changing the password in compose after first boot has no effect —
  `docker compose down -v` and start again.
- Pin the minor version (`postgres:16.4-alpine`) once the project targets a specific
  managed-Postgres version in production.

---

## MySQL

```yaml
  mysql:
    image: mysql:8.4
    environment:
      MYSQL_ROOT_PASSWORD: devrootpassword
      MYSQL_DATABASE: app_dev
      MYSQL_USER: app
      MYSQL_PASSWORD: devpassword
    ports:
      - "3306:3306"
    volumes:
      - mysql-data:/var/lib/mysql
    healthcheck:
      test: ["CMD-SHELL", "mysqladmin ping -h 127.0.0.1 -uroot -p$$MYSQL_ROOT_PASSWORD"]
      interval: 5s
      timeout: 5s
      retries: 20
      start_period: 20s
```

App connection: `DATABASE_URL=mysql://app:devpassword@localhost:3306/app_dev`.

**Gotchas**
- `$$` escapes the `$` so Compose passes it through to the shell instead of interpolating it.
- Use `-h 127.0.0.1`, not `localhost`: `localhost` makes the client use a unix socket, which
  can answer before TCP is listening.
- MySQL's cold boot is slower than Postgres's; keep `start_period` at 20s or more.

---

## MongoDB

```yaml
  mongo:
    image: mongo:7
    environment:
      MONGO_INITDB_ROOT_USERNAME: app
      MONGO_INITDB_ROOT_PASSWORD: devpassword
      MONGO_INITDB_DATABASE: app_dev
    ports:
      - "27017:27017"
    volumes:
      - mongo-data:/data/db
    healthcheck:
      test: ["CMD-SHELL", "mongosh --quiet --eval 'db.adminCommand({ping:1}).ok'"]
      interval: 5s
      timeout: 5s
      retries: 10
      start_period: 15s
```

App connection:
`MONGO_URL=mongodb://app:devpassword@localhost:27017/app_dev?authSource=admin`.

**Gotchas**
- Omitting `authSource=admin` gives authentication failures against a root user created by
  `MONGO_INITDB_ROOT_*`.
- **Transactions and change streams require a replica set.** A standalone `mongod` rejects
  them. If the application uses either, run a single-node replica set:

```yaml
  mongo:
    image: mongo:7
    command: ["mongod", "--replSet", "rs0", "--bind_ip_all"]
    ports:
      - "27017:27017"
    volumes:
      - mongo-data:/data/db
    healthcheck:
      test: ["CMD-SHELL", "mongosh --quiet --eval 'try { rs.status().ok } catch (e) { rs.initiate({_id:\"rs0\",members:[{_id:0,host:\"mongo:27017\"}]}).ok }'"]
      interval: 5s
      timeout: 10s
      retries: 20
      start_period: 15s
```

  The health check initiates the replica set on first run and reports ok thereafter, so the
  stack needs no manual step. Connect with
  `mongodb://localhost:27017/app_dev?replicaSet=rs0&directConnection=true`. This variant runs
  without authentication: enabling auth on a replica set additionally requires a keyfile for
  internal cluster auth, which is complexity a local stack does not need.

---

## Redis

```yaml
  redis:
    image: redis:7-alpine
    command: ["redis-server", "--appendonly", "yes"]
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 10
      start_period: 5s
```

App connection: `REDIS_URL=redis://localhost:6379/0`.

**Gotchas**
- The default image has no password. That is correct for a local stack, but means the app's
  production `REDIS_URL` shape (with credentials) differs — keep the URL in `.env`, not in
  code.
- Use a distinct database index for tests (`redis://localhost:6379/1`) so a test flush never
  wipes the development dataset.
- `redis-cli ping` returns `PONG` while Redis is still loading a large AOF file; if the
  dataset is big, add `--appendonly no` for test stacks instead.

---

## Elasticsearch / OpenSearch

```yaml
  elasticsearch:
    image: elasticsearch:8.15.0
    environment:
      discovery.type: single-node
      xpack.security.enabled: "false"
      ES_JAVA_OPTS: "-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch-data:/usr/share/elasticsearch/data
    healthcheck:
      test: ["CMD-SHELL", "curl -fs http://localhost:9200/_cluster/health | grep -qE 'green|yellow'"]
      interval: 10s
      timeout: 5s
      retries: 12
      start_period: 40s
```

App connection: `ELASTICSEARCH_URL=http://localhost:9200`.

OpenSearch is the same shape with `opensearchproject/opensearch:2`,
`discovery.type: single-node`, `DISABLE_SECURITY_PLUGIN: "true"`, and port `9200`.

**Gotchas**
- `discovery.type=single-node` is mandatory; without it the node waits for a cluster that
  will never form and never becomes healthy.
- Set a JVM heap (`ES_JAVA_OPTS`) or the container will size itself against the whole host
  and get OOM-killed on a laptop.
- A single-node cluster reports **yellow**, not green, because replicas are unassigned. A
  health check that requires green never passes — match `green|yellow`.
- Elasticsearch 8 enables security by default; disabling it for a local stack keeps the URL
  simple, but means the production TLS/auth path is untested. Flag that gap if an AC depends
  on it.

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Credentials rejected after changing compose env | Init variables apply only to an empty data volume | `docker compose down -v && docker compose up -d --wait` |
| `pg_isready` healthy but app cannot connect | Health check ran as the wrong role | Add `-U <user> -d <db>` |
| Elasticsearch never healthy | Missing `discovery.type` or requiring green | Set single-node; accept yellow |
| Mongo transaction errors | Standalone mongod | Run the single-node replica-set variant |
| Container OOM-killed | No JVM/memory bound | Set `ES_JAVA_OPTS` or a `mem_limit` |
