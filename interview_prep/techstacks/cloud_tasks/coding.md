# Cloud Tasks Coding Questions — Round 2 Drills

## Interview Guide
Graded on correct queue/task configuration: rate limiting lives on the queue, auth lives on the task.

---

### Q1. Enqueue a Cloud Task with rate limiting
```python
from google.cloud import tasks_v2
import json

client = tasks_v2.CloudTasksClient()
parent = client.queue_path("my-project", "us-central1", "process-queue")

task = {
    "http_request": {
        "http_method": tasks_v2.HttpMethod.POST,
        "url": "https://processor-abc.a.run.app/process",
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"file_id": "abc123"}).encode(),
        "oidc_token": {"service_account_email": "task-invoker@my-project.iam.gserviceaccount.com"},
    }
}
client.create_task(request={"parent": parent, "task": task})
```
**Talk through:** rate limiting itself is configured on the **queue** (max dispatches/second, max
concurrent dispatches), not per-task — the enqueue call just adds work; the queue's config is what
protects a rate-limited downstream API. This is the detail that separates a "meets bar" answer from a
"exceeds bar" one for this question.

---

### Q2. Configure queue-level rate limiting (gcloud)
```bash
gcloud tasks queues create process-queue \
  --location=us-central1 \
  --max-dispatches-per-second=5 \
  --max-concurrent-dispatches=10 \
  --max-attempts=5 \
  --min-backoff=10s \
  --max-backoff=300s
```
**Follow-up:** "Why both `max-dispatches-per-second` and `max-concurrent-dispatches`?" → the first caps
throughput rate (protects a rate-limited downstream API), the second caps how many requests are in-flight
at once (protects the downstream service's own concurrency/connection limits) — they solve different
problems and are often both needed together.
