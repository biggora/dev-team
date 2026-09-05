# Reference: Messaging and Mail Containers

## Overview

Queues, brokers, and SMTP capture for a local stack. Every block below satisfies the compose
contract: pinned tag, health check, named volume where the service holds state,
deterministic host port. Declare the volumes once:

```yaml
volumes:
  rabbitmq-data:
  kafka-data:
```

---

## RabbitMQ

```yaml
  rabbitmq:
    image: rabbitmq:3-management-alpine
    environment:
      RABBITMQ_DEFAULT_USER: app
      RABBITMQ_DEFAULT_PASS: devpassword
    ports:
      - "5672:5672"
      - "15672:15672"
    volumes:
      - rabbitmq-data:/var/lib/rabbitmq
    healthcheck:
      test: ["CMD", "rabbitmq-diagnostics", "-q", "check_running"]
      interval: 10s
      timeout: 10s
      retries: 10
      start_period: 30s
```

App connection: `AMQP_URL=amqp://app:devpassword@localhost:5672/`.
Management UI on `http://localhost:15672` (same credentials) — useful for eyeballing queue
depth during a demo.

**Gotchas**
- `check_running` reports the node is up; use `check_port_connectivity` instead if the app
  connects before the broker finishes booting plugins.
- RabbitMQ's boot is slow (30s cold is normal). Do not shorten `start_period` to make the
  stack look faster — that only converts a wait into a flake.
- Queues and exchanges the app expects should be declared by the app on startup, not by hand
  in the UI. Hand-declared topology dies with `down -v`.

---

## Kafka (KRaft mode)

KRaft removes the ZooKeeper container. A single-broker local setup:

```yaml
  kafka:
    image: apache/kafka:3.8.0
    environment:
      KAFKA_NODE_ID: 1
      KAFKA_PROCESS_ROLES: broker,controller
      KAFKA_CONTROLLER_QUORUM_VOTERS: "1@kafka:9093"
      KAFKA_LISTENERS: "INTERNAL://:9092,CONTROLLER://:9093,EXTERNAL://:29092"
      KAFKA_ADVERTISED_LISTENERS: "INTERNAL://kafka:9092,EXTERNAL://localhost:29092"
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: "INTERNAL:PLAINTEXT,CONTROLLER:PLAINTEXT,EXTERNAL:PLAINTEXT"
      KAFKA_INTER_BROKER_LISTENER_NAME: INTERNAL
      KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
    ports:
      - "29092:29092"
    volumes:
      - kafka-data:/var/lib/kafka/data
    healthcheck:
      test: ["CMD-SHELL", "/opt/kafka/bin/kafka-topics.sh --bootstrap-server localhost:9092 --list"]
      interval: 10s
      timeout: 10s
      retries: 12
      start_period: 30s
```

Bootstrap servers: `localhost:29092` from the host, `kafka:9092` from inside the compose
network.

`bitnami/kafka` is an equivalent alternative; its variables are named the same
(`KAFKA_CFG_*` prefix on older tags) and its broker binary lives under `/opt/bitnami/kafka/bin`,
so adjust the health check path accordingly.

**The `advertised.listeners` trap.** A Kafka client's first request returns broker metadata,
and the client then reconnects to whatever address that metadata contains. With a single
listener advertised as `kafka:9092`, a host-side test connects to `localhost:29092`, receives
`kafka:9092`, and hangs or fails with an unresolvable host — even though the initial
connection succeeded. Two listeners (INTERNAL for containers, EXTERNAL advertised as
`localhost`) is the fix, and it is why the port mapping above exposes 29092 rather than 9092.

**Other gotchas**
- Replication factors must be 1 on a single broker; the defaults of 3 make internal topics
  fail to create.
- Auto topic creation may be off. Create the topics the app needs from an init step or from
  the application itself, not by hand.

---

## SMTP capture: Mailpit (preferred)

Mailpit accepts SMTP, stores nothing outside the container by default, and exposes both a web
UI and a JSON API for assertions.

```yaml
  mailpit:
    image: axllent/mailpit:v1.20
    ports:
      - "1025:1025"
      - "8025:8025"
    healthcheck:
      test: ["CMD-SHELL", "wget -q -O - http://localhost:8025/readyz || exit 1"]
      interval: 5s
      timeout: 3s
      retries: 10
      start_period: 5s
```

App configuration: `SMTP_HOST=localhost`, `SMTP_PORT=1025`, no TLS, no auth.
UI on `http://localhost:8025`.

No named volume is declared: mail is deliberately ephemeral, and `down -v` should discard it.

### Asserting a sent email in a test

Mailpit's HTTP API on port 8025 is the assertion surface. Clear the mailbox before the test,
trigger the action, then read the messages.

```
DELETE http://localhost:8025/api/v1/messages          → empties the mailbox
GET    http://localhost:8025/api/v1/messages          → { total, messages: [ { ID, To, Subject, ... } ] }
GET    http://localhost:8025/api/v1/message/{ID}      → full message incl. Text and HTML bodies
```

Node (Vitest/Jest):

```ts
const MAILPIT = process.env.MAILPIT_URL ?? "http://localhost:8025";

beforeEach(async () => {
  await fetch(`${MAILPIT}/api/v1/messages`, { method: "DELETE" });
});

it("sends a verification email on signup", async () => {
  await request(app).post("/signup").send({ email: "user@example.com" }).expect(201);

  const inbox = await (await fetch(`${MAILPIT}/api/v1/messages`)).json();
  expect(inbox.total).toBe(1);
  expect(inbox.messages[0].To[0].Address).toBe("user@example.com");

  const full = await (await fetch(`${MAILPIT}/api/v1/message/${inbox.messages[0].ID}`)).json();
  expect(full.Text).toContain("verify your address");
});
```

Python (pytest):

```python
MAILPIT = os.environ.get("MAILPIT_URL", "http://localhost:8025")

@pytest.fixture(autouse=True)
def empty_mailbox():
    httpx.delete(f"{MAILPIT}/api/v1/messages")

def test_signup_sends_verification(client):
    client.post("/signup", json={"email": "user@example.com"})

    inbox = httpx.get(f"{MAILPIT}/api/v1/messages").json()
    assert inbox["total"] == 1

    body = httpx.get(f"{MAILPIT}/api/v1/message/{inbox['messages'][0]['ID']}").json()
    assert "verify your address" in body["Text"]
```

Sending is asynchronous in most applications. Poll the message list with a short retry loop
rather than sleeping a fixed interval.

## SMTP capture: Mailhog (legacy alternative)

Use Mailhog only when a project already depends on it; it is unmaintained and Mailpit is its
drop-in successor.

```yaml
  mailhog:
    image: mailhog/mailhog:v1.0.1
    ports:
      - "1025:1025"
      - "8025:8025"
    healthcheck:
      test: ["CMD-SHELL", "wget -q -O - http://localhost:8025/api/v2/messages || exit 1"]
      interval: 5s
      timeout: 3s
      retries: 10
      start_period: 5s
```

Its API differs: `GET /api/v2/messages`, `DELETE /api/v1/messages`, and the message shape
nests bodies under `Content.Body`.

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| Kafka client hangs after connecting | Advertised listener unreachable from the host | Add an EXTERNAL listener advertised as `localhost:29092` |
| Kafka internal topics fail to create | Replication factor 3 on one broker | Set the three replication/ISR variables to 1 |
| RabbitMQ healthy but app connection refused | App started before plugins finished | Use `check_port_connectivity`, raise `start_period` |
| Mailbox has leftovers from a prior test | No reset between tests | `DELETE /api/v1/messages` in a `beforeEach` fixture |
| Email assertion is flaky | Send is asynchronous | Poll the message list with retries, not `sleep` |
