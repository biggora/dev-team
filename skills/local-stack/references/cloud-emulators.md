# Reference: Cloud Emulators (MinIO, LocalStack)

## Overview

Cloud services cannot run on a laptop, so rung 2 of the decision procedure applies: a
containerized emulator. MinIO covers S3-compatible object storage; LocalStack covers the
broader AWS surface. Both are real network services with real wire protocols — the SDK under
test is the production SDK, pointed at a different endpoint.

Declare the volume once:

```yaml
volumes:
  minio-data:
```

---

## MinIO

```yaml
  minio:
    image: minio/minio:RELEASE.2024-09-13T20-26-02Z
    command: ["server", "/data", "--console-address", ":9001"]
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: devpassword
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio-data:/data
    healthcheck:
      test: ["CMD-SHELL", "curl -fs http://localhost:9000/minio/health/live"]
      interval: 5s
      timeout: 3s
      retries: 10
      start_period: 10s
```

MinIO's tags are date-stamped releases rather than semantic versions; pin the exact release
string the project verified against and bump it deliberately.

### Bucket creation on startup

Buckets are stack state, so they are created by code, not by hand in the console. A `mc`
sidecar that runs once and exits does the job idempotently:

```yaml
  minio-init:
    image: minio/mc:RELEASE.2024-09-16T17-43-14Z
    depends_on:
      minio:
        condition: service_healthy
    entrypoint: >
      /bin/sh -c "
      mc alias set local http://minio:9000 minioadmin devpassword &&
      mc mb --ignore-existing local/app-uploads &&
      mc anonymous set download local/app-uploads
      "
```

`mc mb --ignore-existing` makes reruns safe. The container exits 0 when done; that is
expected and is not a failed service. Because it exits, give it no health check and never
make another service `depends_on` it with `condition: service_healthy` — use
`condition: service_completed_successfully` if a consumer must wait for the buckets.

### Pointing an SDK at MinIO

Two settings matter. `endpoint` redirects the SDK, and **path-style addressing** is required
because virtual-host style (`bucket.localhost:9000`) does not resolve locally.

Node (AWS SDK v3):

```ts
new S3Client({
  endpoint: process.env.S3_ENDPOINT,        // http://localhost:9000
  region: process.env.AWS_REGION ?? "us-east-1",
  forcePathStyle: true,
  credentials: {
    accessKeyId: process.env.AWS_ACCESS_KEY_ID,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
  },
});
```

Python (boto3):

```python
boto3.client(
    "s3",
    endpoint_url=os.environ["S3_ENDPOINT"],
    region_name=os.environ.get("AWS_REGION", "us-east-1"),
    config=Config(s3={"addressing_style": "path"}),
)
```

`.env.example` entries: `S3_ENDPOINT=http://localhost:9000`, `AWS_ACCESS_KEY_ID=minioadmin`,
`AWS_SECRET_ACCESS_KEY=devpassword`, `AWS_REGION=us-east-1`, `S3_BUCKET=app-uploads`.
In production these are unset (or point at real AWS) and the SDK's defaults take over — which
is exactly why the endpoint must come from configuration and never be hardcoded.

**Behavioural gaps to flag:** no lifecycle rules, no cross-region replication, no S3 event
notifications to real SNS/SQS, and presigned-URL and CORS edge cases differ. An AC that
depends on any of these is UNVERIFIED against MinIO.

---

## LocalStack

```yaml
  localstack:
    image: localstack/localstack:3.7
    environment:
      SERVICES: "s3,sqs,sns,dynamodb"
      DEBUG: "0"
    ports:
      - "4566:4566"
    volumes:
      - ./docker/localstack-init:/etc/localstack/init/ready.d:ro
    healthcheck:
      test: ["CMD-SHELL", "curl -fs http://localhost:4566/_localstack/health | grep -q '\"s3\": \"available\"'"]
      interval: 10s
      timeout: 5s
      retries: 12
      start_period: 20s
```

**`SERVICES` selection.** List only what the application uses. Every extra service adds boot
time and memory. All of them are reached through the single edge port `4566`.

**Health endpoint.** `GET http://localhost:4566/_localstack/health` returns a JSON map of
service to status (`available` once started, `running` after first use). Grep for the service
the app actually needs — a generic 200 check passes before that service is ready.

**Persistence.** The free tier is ephemeral: state is lost on container restart. Treat that
as a feature — it makes `down -v` and recreate trivially clean — and recreate resources from
an init script on every boot rather than relying on persistence.

**Init scripts.** Executable shell scripts mounted into `/etc/localstack/init/ready.d` run
once the edge is up. Keep them idempotent:

```sh
#!/bin/sh
set -e
awslocal s3 mb s3://app-uploads || true
awslocal sqs create-queue --queue-name app-jobs
```

`awslocal` is preinstalled in the image and is `aws` with the endpoint preset.

**Client configuration** is the same shape as MinIO: `endpoint` (or `endpoint_url`) set to
`http://localhost:4566`, path-style addressing for S3, and dummy credentials
(`AWS_ACCESS_KEY_ID=test`, `AWS_SECRET_ACCESS_KEY=test`) — LocalStack does not validate them.

**Free-tier surface.** S3, SQS, SNS, DynamoDB, Lambda, API Gateway, Secrets Manager, SSM,
IAM (permissive), Kinesis, CloudWatch Logs, StepFunctions. Paid-tier-only services (RDS,
ECS, EKS, AppSync among others) are not available — if the application needs one, that is a
rung-3 HALT, not a workaround.

**Behavioural gaps to flag:** IAM policies are not enforced by default, so a permissions AC
cannot be closed here; eventual consistency, throttling, and quota errors are not reproduced;
cross-region and cross-account behaviour is absent; Lambda cold-start and timeout semantics
differ.

---

## Troubleshooting

| Problem | Cause | Solution |
|---------|-------|----------|
| `NoSuchBucket` on first run | Init sidecar not run or not awaited | Use `mc mb --ignore-existing` and `service_completed_successfully` |
| SDK requests time out against MinIO | Virtual-host addressing | Set `forcePathStyle` / `addressing_style: "path"` |
| Compose reports minio-init unhealthy | It is a one-shot container | Remove its health check; it is expected to exit 0 |
| LocalStack ready but service missing | Service not in `SERVICES` | Add it and recreate the container |
| Resources vanish after restart | Free tier is ephemeral | Recreate from an idempotent init script |
| SignatureDoesNotMatch against MinIO | Region mismatch between client and stack | Set `AWS_REGION` identically on both sides |
