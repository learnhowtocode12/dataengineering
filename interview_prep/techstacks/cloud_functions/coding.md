# Cloud Functions Coding Questions — Round 2 Drills

## Interview Guide
Graded on idempotent event handlers and knowing the memory/time limits of a Function so you recognize
when a task has outgrown it. See [../cloud_run/coding.md](../cloud_run/coding.md) for shared
patterns (ADC auth, Dockerfile practices) that apply equally here once you're on Gen2/container-based
Functions.

---

### Q1. Cloud Function (Gen2) triggered by a GCS finalize event, with idempotency
```python
import functions_framework
from google.cloud import bigquery, firestore

db = firestore.Client()
bq = bigquery.Client()

@functions_framework.cloud_event
def on_file_upload(cloud_event):
    data = cloud_event.data
    object_id = data["id"]  # bucket/object/generation - stable unique id for this event

    doc_ref = db.collection("processed_files").document(object_id)
    if doc_ref.get().exists:
        print(f"Already processed {object_id}, skipping (duplicate delivery)")
        return

    process_file(data["bucket"], data["name"])
    doc_ref.set({"processed_at": firestore.SERVER_TIMESTAMP})
```
**Talk through:** GCS/Eventarc delivery is at-least-once, so the same finalize event can be redelivered —
the Firestore "processed markers" check makes re-processing a no-op instead of double-loading data.

---

### Q2. Debug exercise: Cloud Function times out / OOMs on large files
**Prompt:** "This function reads an entire GCS file into memory with `blob.download_as_bytes()` before
parsing it, and it's timing out/OOMing on files over ~500MB. Fix it."
```python
# Before (loads everything into memory):
data = blob.download_as_bytes()
records = parse_all(data)

# After (streams the file, processing incrementally):
with blob.open("rb") as f:
    for line in f:
        record = parse_line(line)
        process(record)
```
**Follow-up:** "What if even streaming isn't fast enough?" → this is the signal to say "I'd hand this off
to Dataflow/Dataproc instead of trying to force it through a single Cloud Function invocation" — knowing
when *not* to use serverless functions is itself the answer being tested. See
[../dataflow/guide.md](../dataflow/guide.md).

---

### Q3. Authenticate to BigQuery/GCS with Application Default Credentials (no key files)
```python
from google.cloud import bigquery

# No explicit credentials passed - ADC automatically picks up the attached service account.
client = bigquery.Client(project="my-project")
rows = client.query("SELECT 1").result()
```
**Talk through:** a downloaded JSON key committed to a repo or baked into an image is a classic
OWASP-style credential-exposure risk; ADC + attached service accounts avoids long-lived secrets entirely.
Same pattern as [../cloud_run/coding.md](../cloud_run/coding.md) Q5 and
[../gke/guide.md](../gke/guide.md) Q3 (Workload Identity) for GKE specifically.
