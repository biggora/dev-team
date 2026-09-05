# Reference: Third-Party Service Emulators

## Overview

Emulators for third-party services that cannot run locally: payments (stripe-mock),
arbitrary HTTP APIs (WireMock), and identity (Keycloak). Each is a real HTTP server, so the
application under test uses its production client library and only the base URL changes.

Every emulator has behavioural gaps. Naming the gap is part of using it: an acceptance
criterion that depends on behaviour the emulator does not reproduce stays **UNVERIFIED**, no
matter how green the test is.

---

## stripe-mock

```yaml
  stripe-mock:
    image: stripe/stripe-mock:v0.190.0
    ports:
      - "12111:12111"
    healthcheck:
      test: ["CMD-SHELL", "wget -q -O - http://localhost:12111/v1/charges --header='Authorization: Bearer sk_test_123' || exit 1"]
      interval: 5s
      timeout: 3s
      retries: 10
      start_period: 5s
```

Point the Stripe SDK at it (`STRIPE_API_BASE=http://localhost:12111`) with any
`sk_test_...` key — stripe-mock does not validate keys.

Node: `new Stripe(key, { host: "localhost", port: 12111, protocol: "http" })`.
Python: `stripe.api_base = os.environ["STRIPE_API_BASE"]`.

**What it does:** validates requests against Stripe's OpenAPI spec and returns
spec-conformant fixture responses. It catches wrong endpoints, malformed parameters, missing
required fields, and response-parsing bugs — the majority of integration mistakes.

**What it does NOT do, and must be flagged:**
- **No state.** Creating a customer then fetching it returns fixture data, not what you
  created. Any AC about a multi-step flow (create → charge → refund) is UNVERIFIED here.
- **No webhooks.** stripe-mock never calls back. Webhook handling must be verified another
  way — a signed test payload constructed with the SDK's own signature helper against your
  local endpoint, which verifies your handler but not Stripe's delivery.
- **No signature verification against live keys**, no 3D Secure, no real error/decline
  scenarios, no idempotency-key semantics.

For anything stateful, the alternative is Stripe's real test mode with sandbox keys — which
is an external dependency requiring the user's credentials, so it is a coordinator question,
not an agent decision.

---

## WireMock

```yaml
  wiremock:
    image: wiremock/wiremock:3.9.1
    command: ["--global-response-templating", "--disable-banner"]
    ports:
      - "8080:8080"
    volumes:
      - ./docker/wiremock:/home/wiremock:ro
    healthcheck:
      test: ["CMD-SHELL", "curl -fs http://localhost:8080/__admin/health || exit 1"]
      interval: 5s
      timeout: 3s
      retries: 10
      start_period: 10s
```

The mounted directory holds `mappings/` (request/response definitions) and `__files/`
(response bodies). Both are committed to the repo. The mount is read-only in the test stack
so a run cannot mutate the contract.

### Record, then replay — never hand-write

WireMock's value comes entirely from the mappings being a **recording of the real API**. Run
it once in record mode against the real service with sandbox credentials:

```bash
docker run --rm -p 8080:8080 \
  -v "$PWD/docker/wiremock:/home/wiremock" \
  wiremock/wiremock:3.9.1 --proxy-all="https://api.partner.example.com" --record-mappings
```

Exercise the application's real code paths against it, stop the container, and commit the
generated `mappings/` and `__files/`. From then on the stack replays them offline.

**Why hand-written stubs are not acceptable evidence.** A hand-written stub encodes what the
developer *believed* the API returns. If that belief is wrong — a field is `null` not absent,
a status is 202 not 200, an error envelope has a different shape, a date is epoch millis not
ISO — the test passes and production breaks. The test then proves only that the code agrees
with itself. A recorded mapping is a captured observation of the real contract; a
hand-written one is a restatement of the assumption under test. When only hand-written stubs
exist, report the affected AC as UNVERIFIED with "stubs not recorded from the real API" as
the reason.

Re-record when the partner API changes, and treat mapping diffs as contract changes in review.

---

## Keycloak (dev mode)

```yaml
  keycloak:
    image: quay.io/keycloak/keycloak:25.0
    command: ["start-dev", "--import-realm"]
    environment:
      KEYCLOAK_ADMIN: admin
      KEYCLOAK_ADMIN_PASSWORD: devpassword
    ports:
      - "8081:8080"
    volumes:
      - ./docker/keycloak/realm-export.json:/opt/keycloak/data/import/realm-export.json:ro
    healthcheck:
      test: ["CMD-SHELL", "exec 3<>/dev/tcp/localhost/8080 && echo -e 'GET /realms/app/.well-known/openid-configuration HTTP/1.1\\r\\nHost: localhost\\r\\nConnection: close\\r\\n\\r\\n' >&3 && cat <&3 | grep -q 'issuer'"]
      interval: 10s
      timeout: 5s
      retries: 15
      start_period: 30s
```

The image is distroless and ships no `curl` or `wget`, which is why the health check uses
bash's `/dev/tcp`. It probes the realm's OIDC discovery document, so it only passes once the
realm import has actually landed — exactly the condition the app needs.

Host port 8081 avoids the common 8080 clash with WireMock and application servers.

**Realm import is what makes identity reproducible.** Export the realm once
(`kc.sh export`, or the admin console's partial export) with its clients, roles, and test
users, commit `realm-export.json`, and let `--import-realm` recreate it on every boot. Nobody
clicks through the admin console; `down -v` stays safe.

App configuration:
`OIDC_ISSUER=http://localhost:8081/realms/app`,
`OIDC_CLIENT_ID=app-web`, `OIDC_CLIENT_SECRET=devsecret`.

**Gaps to flag:** `start-dev` runs HTTP-only with a dev-grade database and relaxed hostname
checks. Anything about TLS, token-signing key rotation, production hostname handling, or
clustering is UNVERIFIED against dev mode.

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| stripe-mock returns unexpected object | Fixture data, not your input | Do not assert on returned ids/amounts; assert on request shape |
| Webhook test passes but production fails | stripe-mock never delivers webhooks | Verify the handler with an SDK-signed payload; mark delivery UNVERIFIED |
| WireMock returns 404 for a valid request | Mapping matcher too strict (headers, query order) | Inspect `GET /__admin/requests` for the unmatched request |
| WireMock mappings drift from the API | Never re-recorded | Re-run record mode; review the mapping diff |
| Keycloak health check always fails | No curl in the image | Use the `/dev/tcp` probe above |
| Keycloak realm missing after restart | Realm created by hand, not imported | Export it and mount it with `--import-realm` |
