# Cloud Functions — Interview Guide & Q&A
> **Round mapping:** R2 (technical deep dive). Hands-on drills: [coding](coding.md). See also
> [../cloud_run/guide](../cloud_run/guide.md) and [../gke/guide](../gke/guide.md) — expect a
> three-way comparison question across all three compute options.

## Interview Guide
For a data engineer, Cloud Functions questions focus on event-driven ingestion/reaction patterns: "an
API/upload lands a file, what do you build and why," reliability under at-least-once delivery, and
knowing when a task has outgrown a Function and belongs in Cloud Run or Dataflow instead.

---

## Q&A

**Q1: What is Cloud Functions, and when do you pick it over Cloud Run or GKE?**

**Answer:** Cloud Functions is single-purpose, event-triggered (GCS, Pub/Sub, Firestore, HTTP), fully managed —
you write just a function handler and Google manages the runtime. Best for small, short-lived, simple
event reactions (e.g., a GCS-upload trigger that kicks off a pipeline or does light validation). Once the
logic needs custom dependencies/longer execution/more memory, or isn't naturally one-event-in-one-handler,
move to [Cloud Run](../cloud_run/guide.md); once you need full cluster/networking control or GPU
scheduling, move to [GKE](../gke/guide.md).

**Q2: How do you trigger a Cloud Function from a GCS upload, and what are the reliability
considerations?**

**Answer:** GCS → Eventarc (or legacy direct GCS trigger for Gen1 Functions) delivers an event (object finalize)
to the Function. Considerations: **at-least-once delivery** — the handler must be idempotent (same object
event could be redelivered); **ordering is not guaranteed** across different objects; handle **large
files** by not loading the whole object into memory (stream processing or hand off to a heavier service/
Dataflow instead of processing in-function — see [coding](coding.md) Q3 for the fix); and **retries/
dead-lettering** — configure Eventarc/Pub/Sub retry policy and route permanently-failing events to a
dead-letter topic instead of infinite retry loops.

**Q3: How do you handle cold starts in Cloud Functions, and when does it matter for data pipelines?**

**Answer:** Cold start = latency to spin up a new container instance (image pull, runtime init, app init) when
scaling from zero or scaling up. Mitigate with: minimum instances (`min-instances` keeps warm instances
ready, at a baseline cost), smaller/leaner dependency footprint, lazy-loading heavy dependencies only when
needed, and keeping app init fast (avoid heavy global-scope work like loading huge models/files at import
time unless necessary). For data pipelines, it mainly matters for latency-sensitive event-driven triggers
(e.g., a user-facing API) more than for scheduled batch jobs where a few seconds of cold start is
negligible.

**Q4: When would a data engineer specifically choose Cloud Run Jobs over Cloud Functions for a batch
task?**

**Answer:** Cloud Run Jobs are built for run-to-completion batch/background work (not request/response), support
much longer execution times than Functions' request timeout, larger memory/CPU footprints, custom
container images with heavy dependencies (e.g., a PySpark/pandas-based transformation), and parallel task
execution with indexed tasks. Cloud Functions are better for small, fast, simple reactions directly tied
to an event trigger. See [../cloud_run/guide](../cloud_run/guide.md) Q2 for the Cloud Run side of this.

**Q5: How would you design an event-driven ingestion pattern using Cloud Functions plus Pub/Sub for
near-real-time use cases, and where does Dataflow fit vs this?**

**Answer:** Source emits events to Pub/Sub (see [../pubsub/guide](../pubsub/guide.md)) → a Cloud Function (push
subscription) handles lightweight per-message processing (e.g., validation, enrichment via a small
lookup, routing) and writes to BigQuery/GCS or re-publishes to another topic. This fits simple, stateless,
per-message transforms with modest throughput. For anything needing **windowed aggregation**, **stateful
processing across events**, **very high throughput with backpressure handling**, or **complex joins/
sessionization**, Dataflow (Beam) is the right tool — a Cloud Function would require hand-rolling
windowing/state management that Beam provides natively. See
[../dataflow/guide](../dataflow/guide.md).

**Q6: How do you handle secrets and configuration in Cloud Functions?**

**Answer:** Cloud Functions mount secrets as environment variables or volume-mounted files directly from Secret
Manager at deploy/runtime with IAM-controlled access — no extra client code needed for basic cases. See
[../gke/guide](../gke/guide.md) Q4 for how this differs on GKE (which needs an extra sync mechanism).

**Q7: Give an example from experience combining Cloud Functions with the rest of this stack (BigQuery,
Dataflow, Airflow, Cloud Run).**

**Answer:** A Cloud Function triggers on a GCS file landing in a raw bucket, validates basic file integrity/schema
header, writes a manifest row to a BigQuery control table, and publishes a Pub/Sub message. A Cloud
Workflow (or Airflow DAG via Composer, triggered by sensing the control table/Dataset) then launches a
Dataflow Flex template job to transform and load the file into BigQuery, and finally calls a small Cloud
Run service that triggers a Looker PDT rebuild via the Looker API so dashboards reflect the new data —
illustrating how the lightweight serverless compute and the heavier processing/orchestration layers
compose together.
