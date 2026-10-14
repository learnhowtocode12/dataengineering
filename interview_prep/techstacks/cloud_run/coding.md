# Cloud Run Coding Questions — Round 2 Drills

## Interview Guide
Graded on production-shaped container code: health checks, correct `PORT` handling, non-root containers,
and Cloud Run Jobs' sharding model. See [../cloud_functions/coding.md](../cloud_functions/coding.md) and
[../gke/coding.md](../gke/coding.md) for the equivalent patterns on the other two compute options.

---

### Q1. Minimal FastAPI app for Cloud Run with a health check
```python
# main.py
from fastapi import FastAPI
import os

app = FastAPI()

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.post("/process")
def process(payload: dict):
    result = run_transform(payload)
    return {"result": result}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
```
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
USER 1000  # don't run as root
CMD ["python", "main.py"]
```
**Talk through:** Cloud Run injects the `PORT` env var at runtime — the app must respect it, not hard-code
8080; running as a non-root user is a basic container security practice worth calling out unprompted.

---

### Q2. Cloud Run Job processing a shard by task index
```python
import os

def main():
    task_index = int(os.environ["CLOUD_RUN_TASK_INDEX"])
    task_count = int(os.environ["CLOUD_RUN_TASK_COUNT"])
    all_files = list_gcs_files(prefix="raw/")
    my_shard = [f for i, f in enumerate(all_files) if i % task_count == task_index]
    for f in my_shard:
        process_file(f)

if __name__ == "__main__":
    main()
```
**Talk through:** Cloud Run Jobs run `task_count` parallel task instances, each knowing its own index —
simple modulo sharding distributes work evenly; for very uneven file sizes, discuss hashing or a work-queue
(Cloud Tasks — see [../cloud_tasks/coding.md](../cloud_tasks/coding.md)) pull model instead of static
sharding.

---

### Q3. Pub/Sub push subscription handler with correct ack/nack semantics
A full worked example lives in [../pubsub/coding.md](../pubsub/coding.md) Q8 — the same Flask/Cloud Run
pattern (2xx acks, 5xx nacks and triggers redelivery) applies whether the push target is Cloud Run or
Cloud Functions.

---

### Q4. Authenticate to BigQuery/GCS with Application Default Credentials (no key files)
```python
from google.cloud import bigquery

# No explicit credentials passed - ADC automatically picks up:
# - the attached service account on Cloud Run (via the service's runtime SA), or
# - gcloud auth application-default login locally for development
client = bigquery.Client(project="my-project")
rows = client.query("SELECT 1").result()
```
**Talk through:** explicitly state *why* this matters — a downloaded JSON key committed to a repo or
baked into an image is a classic OWASP-style credential-exposure risk; ADC + attached service accounts
avoids long-lived secrets entirely. See [../gke/guide.md](../gke/guide.md) Q3 for the GKE equivalent
(Workload Identity), which requires an extra KSA-to-GSA binding step that Cloud Run doesn't need.

---

### Q5. Multi-stage Dockerfile for a leaner Python data-processing image
```dockerfile
FROM python:3.12 AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD ["python", "main.py"]
```
**Talk through:** building in a full image (with compilers available for packages that need them) and
copying only the installed packages into a slim runtime image shrinks the final image size significantly —
directly reduces Cloud Run cold-start time (see [../cloud_run/guide.md](../cloud_run/guide.md) Q3).
