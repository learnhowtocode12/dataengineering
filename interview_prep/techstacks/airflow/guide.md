# Airflow / Cloud Composer — Interview Guide & Q&A
> **Round mapping:** R2 (technical deep dive). Hands-on drills: [coding.md](coding.md). See also
> [../cloud_workflows/guide.md](../cloud_workflows/guide.md),
> [../cloud_tasks/guide.md](../cloud_tasks/guide.md), and
> [../cloud_scheduler/guide.md](../cloud_scheduler/guide.md) — the lighter-weight GCP-native orchestration
> trio, and when you'd pick them over Airflow.

## Interview Guide
Orchestration questions probe whether you can design DAGs that are idempotent, backfill-safe, and
observable — not just "what is a DAG." Expect a question contrasting Airflow/Composer (complex,
dependency-rich, data-aware orchestration) against the lighter GCP-native trio — and when you'd pick the
lightweight option over standing up Composer.

---

## Q&A

**Q1: Explain Airflow's core architecture (scheduler, webserver, executor, workers, metadata DB) and how
Cloud Composer maps onto GKE.**
A: The **scheduler** parses DAG files, evaluates schedules/dependencies, and queues task instances. The
**executor** (CeleryExecutor, KubernetesExecutor, or Composer's managed executor) actually runs tasks —
on workers (Celery) or as pods (Kubernetes executor). The **webserver** serves the UI. The **metadata DB**
(Postgres/MySQL) stores DAG/task state, history, XComs, connections, variables. Cloud Composer manages all
of this on top of GKE — the scheduler/webserver/workers run as pods in a Composer-managed GKE cluster, with
Cloud SQL as the metadata DB and GCS as the DAG-bag storage (DAGs synced from a `dags/` bucket).

**Q2: What makes a DAG idempotent, and why does it matter?**
A: A task is idempotent if re-running it (same `execution_date`/logical date) produces the same end
state without duplicating data or side effects — e.g., a load task that does `DELETE WHERE partition_date
= {{ ds }}` then `INSERT`, or a `MERGE`/upsert keyed on business key, rather than blind `INSERT`/`APPEND`.
It matters because Airflow *will* retry tasks (failures, manual re-runs, backfills, catch-up), and
non-idempotent tasks cause duplicate data, double-charged side effects (e.g., sending an email twice), or
inconsistent backfills.

**Q3: Explain `execution_date`/logical date vs actual run time, and why backfilling is confusing for
newcomers.**
A: Airflow schedules a DAG run for interval *end* historically — `execution_date` represents the *start*
of the data interval being processed, and the run actually happens *after* the interval closes (e.g., a
daily DAG scheduled for `2024-01-01` runs at the end of Jan 1/start of Jan 2 and is meant to process
Jan 1's data). Newer Airflow (2.2+) exposes this more clearly via `data_interval_start`/
`data_interval_end`. Backfilling means running historical DAG runs for past logical dates
(`airflow dags backfill`), which works cleanly only if tasks are idempotent and pull data scoped to that
specific logical date/partition rather than "today."

**Q4: How do you handle cross-DAG dependencies?**
A: `ExternalTaskSensor` (wait for a task in another DAG to reach a state for a given/mapped execution
date), `TriggerDagRunOperator` (actively kick off a downstream DAG from an upstream one, optionally
passing `conf`), Datasets (Airflow 2.4+: DAGs can be scheduled to run when an upstream task "produces" a
Dataset — data-aware scheduling instead of purely time-based), or an external orchestrator/event
(Pub/Sub message triggering a DAG via Cloud Function → Airflow REST API) for cross-system dependencies.

**Q5: Sensors — what's the difference between poke mode and reschedule mode, and why does it matter at
scale?**
A: In poke mode, a sensor holds its worker slot and blocks while repeatedly checking a condition — fine
for short waits but wastes resources on long waits (e.g., waiting hours for a file), risking worker/slot
starvation at scale. Reschedule mode releases the worker slot between checks and re-queues the sensor
task, which scales much better with many concurrent long-running sensors. Deferrable operators/triggers
(Airflow 2.2+, using a lightweight triggerer process) go further — they don't occupy a worker at all while
waiting, using async I/O in a shared triggerer process, which is the most efficient pattern for
high-fan-out "wait for GCS file"/"wait for BigQuery job" style tasks.

**Q6: How do you manage secrets/connections in Composer securely?**
A: Use Airflow Connections/Variables backed by a **Secrets Backend** pointing at Secret Manager (instead
of storing secrets in the metadata DB or `.env` files in plaintext), grant the Composer environment's
service account access to specific secrets via IAM, and avoid hardcoding credentials in DAG code (which
is visible in GCS/source control).

**Q7: How do you structure a large Airflow codebase (many DAGs, shared logic)?**
A: Shared operators/hooks/utilities as an installable internal package (or `plugins/`/`dags/common/`
module synced alongside DAGs), DAG factories (a function generating DAG objects from a config dict/YAML
so near-identical DAGs — e.g., one per source table — aren't copy-pasted), consistent tagging/owners,
and CI that lints DAGs (import test, cycle detection, `airflow dags list-import-errors`) before deployment
to the Composer GCS bucket.

**Q8: How do you test Airflow DAGs?**
A: Unit test custom operators/hooks/Python callables as plain Python (mock external clients). DAG-level
tests: assert the DAG parses without errors, task count/dependencies match expectations, no import cycles,
and tags/owners/retries conform to team conventions (often via `pytest` + Airflow's test utilities or
`dag.test()` in Airflow 2.5+ for a lightweight local run). For integration testing, a local Docker
Compose/Composer dev environment or the Astronomer `astro dev` equivalent to run a DAG end-to-end against
sandboxed resources.

**Q9: How do you set SLAs and alerting on critical DAGs?**
A: Task/DAG-level `sla` parameter triggers SLA-miss callbacks/emails if a task doesn't finish within the
expected time relative to the schedule; `on_failure_callback`/`on_success_callback` hooks post to
Slack/PagerDuty/Monitoring; `retries` + `retry_delay` (often with exponential backoff) handle transient
failures; and separately, Cloud Monitoring can alert on Composer environment health (scheduler heartbeat,
worker pod restarts) independent of DAG-level business logic alerts.

**Q10: Compare `KubernetesPodOperator` vs `PythonOperator`/`BashOperator` — when do you reach for it?**
A: `KubernetesPodOperator` runs a task as an isolated pod with its own container image/dependencies —
use it when a task needs dependencies that conflict with the Airflow worker environment, needs heavier
resources than workers are sized for, needs strong isolation (security/multi-tenant), or you want to reuse
the same container image used elsewhere (e.g., same image as a Cloud Run job) for consistency. Plain
operators are simpler/faster to schedule when the task's dependencies already match the Airflow worker
image. See [../gke/guide.md](../gke/guide.md) for the GKE side of this.

**Q11: How would you design a DAG that loads data from GCS into BigQuery, handles a Dataproc PySpark
transform, then triggers a downstream Looker/BI refresh?**
A: `GCSObjectExistenceSensor` (or event-driven Dataset trigger from an upstream producer) →
`GCSToBigQueryOperator` (raw load to a staging table) → `DataprocCreateClusterOperator` →
`DataprocSubmitJobOperator` (PySpark transform, staging → curated BigQuery table, idempotent
MERGE/overwrite-partition) → `DataprocDeleteClusterOperator` (trigger_rule=`ALL_DONE`) →
a final task calling the Looker API (or a `SimpleHttpOperator`) to trigger a PDT rebuild / cache
invalidation, all wrapped with failure alerting and SLA on the end-to-end DAG.

**Q12: What are the trade-offs of migrating orchestration from Airflow/Composer to Cloud
Workflows/Tasks/Scheduler, and vice versa?**
A: Moving *to* the lightweight stack: lower cost (no always-on environment), simpler ops, less to
maintain, but you lose Airflow's rich UI/observability for complex DAGs, backfill tooling, sensors/
Datasets, and the huge ecosystem of community operators (BigQuery, Dataproc, GCS operators with built-in
retry/idempotency patterns) — so you end up reimplementing some of that glue code yourself in Workflows.
Moving *to* Composer: worth it once you have many interdependent pipelines, need backfills/historical
reprocessing, need a central place for on-call/observability across dozens of DAGs, or need Python-native
custom logic/operators that are awkward to express in Workflows' YAML DSL. See
[../cloud_workflows/guide.md](../cloud_workflows/guide.md) Q1 for the mirror-image framing of this
decision.
