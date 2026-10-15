# Cloud Workflows — Interview Guide & Q&A
> **Round mapping:** R2 (technical deep dive). See also [../airflow/guide](../airflow/guide.md)
> (the heavier alternative), [../cloud_tasks/guide](../cloud_tasks/guide.md), and
> [../cloud_scheduler/guide](../cloud_scheduler/guide.md).

## Interview Guide
Cloud Workflows questions probe whether you know when lightweight, serverless orchestration is the right
call instead of standing up Airflow/Composer — and whether you can reason about retries, branching, and
secure service-to-service auth in a YAML-defined workflow.

---

## Q&A

**Q1: When would you use Cloud Workflows instead of standing up Airflow/Composer?**

**Answer:** Cloud Workflows is a lightweight, serverless YAML/JSON-defined orchestrator for stitching together
GCP API calls and HTTP services (e.g., call Cloud Function A, branch on result, call Cloud Run service B,
handle retries/errors) with no infrastructure to manage and pay-per-step pricing. Use it for simpler,
mostly-linear service orchestration (glue between microservices/APIs) where you don't need Airflow's rich
scheduling semantics (backfills, complex DAG dependency graphs, sensors, data-aware datasets) or its
ecosystem of pre-built data operators. Composer's cost (always-on environment) and operational overhead
aren't justified for a handful of simple orchestration flows — Workflows is cheaper and zero-maintenance
for that case. See [../airflow/guide](../airflow/guide.md) Q12 for the mirror-image framing of this
decision.

**Q2: How does Cloud Workflows handle retries, error handling, and conditionals?**

**Answer:** YAML steps can call HTTP endpoints/GCP connectors; each step can define a `retry` policy (predicate,
max retries, backoff) and `try/except` blocks map errors to custom handling steps (e.g., route to a
dead-letter notification). Conditionals use `switch` steps evaluating expressions on previous step
results, and `parallel` steps run independent branches concurrently with a concurrency limit — enabling
fan-out patterns (e.g., trigger N Cloud Run jobs in parallel, then join).

**Q3: How would you design a lightweight pipeline (no Airflow) using Scheduler + Tasks + Workflows +
Cloud Run for a simple nightly file-processing job?**

**Answer:** Cloud Scheduler fires nightly (see [../cloud_scheduler/guide](../cloud_scheduler/guide.md)) →
triggers a Cloud Workflow → Workflow calls a Cloud Run service to list new files in GCS → for each file,
Workflow enqueues a Cloud Task (see [../cloud_tasks/guide](../cloud_tasks/guide.md)) targeting a Cloud
Run "process file" endpoint (rate-limited, auto-retried) → Workflow (or the final task) calls a final
Cloud Run/Function step to validate completion and write a summary/metric, with errors routed to a Pub/Sub
topic feeding alerting. This whole stack has zero idle-server cost — contrast with Composer's always-on
environment cost — a key point to make about choosing the lightweight stack for simpler, lower-volume
orchestration needs.

**Q4: How do you secure calls between these services (Workflows → Cloud Run, Scheduler → Workflows,
etc.)?**

**Answer:** Use service-to-service auth with a dedicated service account and OIDC tokens — Cloud Scheduler/
Workflows/Tasks attach an identity token (audience = target URL) when calling Cloud Run/Functions, and the
target service's IAM is configured to require authentication (no `allUsers` invoker) and only allow the
specific calling service account as `roles/run.invoker`. Avoid API keys or static secrets for
service-to-service calls; prefer Workload Identity/IAM-based auth throughout.
