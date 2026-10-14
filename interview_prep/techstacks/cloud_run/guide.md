# Cloud Run — Interview Guide & Q&A
> **Round mapping:** R2 (technical deep dive). Hands-on drills: [coding.md](coding.md). See also
> [../cloud_functions/guide.md](../cloud_functions/guide.md) and [../gke/guide.md](../gke/guide.md) —
> expect a three-way comparison question across all three compute options.

## Interview Guide
Cloud Run questions focus on container-based serverless compute: when it's the right middle ground
between Cloud Functions (too simple) and GKE (too much ops overhead), sizing concurrency/resources
correctly, and operational concerns (cold starts, monitoring, rollout safety via revisions).

---

## Q&A

**Q1: What is Cloud Run, and when do you pick it over Cloud Functions or GKE?**
A: Cloud Run is fully managed serverless *containers* — you bring any language/runtime/dependencies in a
Docker image, it scales to zero, supports longer request timeouts and more memory/CPU than Functions, and
also supports **Jobs** (run-to-completion batch tasks, not just HTTP services). Best for more complex
processing logic, custom dependencies (e.g., a Python service with PySpark/pandas/ML libs), or when you
want containerized consistency across environments. Reach for
[Cloud Functions](../cloud_functions/guide.md) for simpler single-purpose event reactions, and
[GKE](../gke/guide.md) when you need full cluster/networking control.

**Q2: When would a data engineer specifically choose Cloud Run Jobs over Cloud Functions for a batch
task?**
A: Cloud Run Jobs are built for run-to-completion batch/background work (not request/response), support
up to very long execution times (far beyond Functions' request timeout), larger memory/CPU footprints,
custom container images with heavy dependencies (e.g., a PySpark/pandas-based transformation, ML model
inference libraries), and parallel task execution with indexed tasks (e.g., process N shards
concurrently, each task reading its shard index from an env var — see [coding.md](coding.md) Q3).

**Q3: How do you handle cold starts in Cloud Run, and when does it matter for data pipelines?**
A: Cold start = latency to spin up a new container instance (image pull, runtime init, app init) when
scaling from zero or scaling up. Mitigate with: minimum instances (`min-instances` keeps warm instances
ready, at a baseline cost), smaller/leaner container images (multi-stage Docker builds, slim base images
— see [coding.md](coding.md) Q10), lazy-loading heavy dependencies only when needed, and keeping app init
fast. For data pipelines, it mainly matters for latency-sensitive event-driven triggers more than for
scheduled batch jobs where a few seconds of cold start is negligible.

**Q4: How do you size concurrency and CPU/memory for a Cloud Run service doing data processing?**
A: Cloud Run request concurrency (requests per instance, up to 1000) should match whether the workload is
CPU-bound (lower concurrency, since one request can hog CPU) or I/O-bound (higher concurrency works well
since requests spend time waiting on network/GCS/BigQuery calls). Memory/CPU limits need headroom for
peak data volume per request (avoid OOM kills) — for genuinely heavy/variable-size data processing,
prefer handing off to Dataflow/Dataproc rather than cramming it into a single Cloud Run request; use Cloud
Run mainly as a lightweight dispatcher/trigger plus moderate transformation step.

**Q5: How do you handle secrets and configuration in Cloud Run?**
A: Cloud Run can mount secrets as environment variables or volume-mounted files directly from Secret
Manager at deploy/runtime with IAM-controlled access — no extra client code needed for basic cases. See
[../gke/guide.md](../gke/guide.md) Q4 for how this differs on GKE (which needs an extra sync mechanism).

**Q6: How do you monitor/debug a production incident where a Cloud Run-based processing service is
failing intermittently?**
A: Cloud Logging (structured JSON logs with trace IDs correlated via `X-Cloud-Trace-Context`), Cloud
Monitoring dashboards (request latency percentiles, error rate, instance count, CPU/memory utilization,
container OOM/crash restarts), Cloud Trace for request latency breakdown across downstream calls
(BigQuery/GCS/third-party APIs), and checking revision-level metrics after a deploy to catch regressions
tied to a specific revision (Cloud Run keeps revision history, enabling quick rollback via traffic
splitting if a new revision is the culprit).

**Q7: What's the difference between Cloud Run (fully managed) and Cloud Run for Anthos/GKE?**
A: Fully managed Cloud Run is serverless on Google's infrastructure — no cluster, scale-to-zero, simplest
ops. Cloud Run on GKE (Knative-based) runs the same Cloud Run developer experience on top of your own GKE
cluster — useful when you need it to live alongside other GKE workloads, need custom networking/node
pools, or need features/resources not available in the fully managed offering, at the cost of managing
the underlying cluster yourself.

**Q8: Give an example from experience combining Cloud Run with the rest of this stack.**
A: See [../cloud_functions/guide.md](../cloud_functions/guide.md) Q7 for a full worked example where a
Cloud Function triggers ingestion and a Cloud Run service is the final step, triggering a Looker PDT
rebuild via the Looker API once a Dataflow load completes.
