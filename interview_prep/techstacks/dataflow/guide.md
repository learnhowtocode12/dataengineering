# Dataflow (Apache Beam) — Interview Guide & Q&A
> **Round mapping:** R2 (technical deep dive). Hands-on drills: [coding](coding.md). See also
> [../dataproc/guide](../dataproc/guide.md) (the alternative compute engine — expect a head-to-head
> comparison question), [../pubsub/guide](../pubsub/guide.md) (the usual streaming source feeding
> Dataflow), and [../apache_iceberg/guide](../apache_iceberg/guide.md).

## Interview Guide
Dataflow is one half of GCP's classic "which compute engine for this job" decision point, so expect a
head-to-head comparison question against Dataproc early, followed by a deep dive into the Apache Beam
programming model (PCollection/PTransform/ParDo), windowing/triggers/watermarks for streaming,
autoscaling, and templates.

---

## Q&A

**Q1: Dataflow vs Dataproc — how do you decide which to use?**

**Answer:** Dataflow is serverless, fully managed Apache Beam — no cluster to manage, autoscales workers per-job,
unified batch+streaming model, pay-per-use. Best when: you don't have existing Hadoop/Spark code/skills,
need true unified batch/streaming semantics, want minimal ops overhead, or need Google-provided templates
(e.g., Pub/Sub to BigQuery). Reach for **Dataproc** instead (see [../dataproc/guide](../dataproc/guide.md)
Q1) when you have existing Spark/Hadoop jobs to lift-and-shift or need Spark-specific libraries. Dataflow's
autoscaling is generally better for unpredictable or streaming loads than a Dataproc cluster.

**Q2: Explain the Apache Beam programming model: PCollection, PTransform, ParDo, pipeline.**

**Answer:** A `Pipeline` is the top-level graph of transforms. A `PCollection` is an immutable, potentially
unbounded distributed dataset flowing through the pipeline. A `PTransform` is an operation that takes
PCollection(s) and returns PCollection(s) (e.g., `Map`, `Filter`, `GroupByKey`, `Combine`). `ParDo` is the
general-purpose element-wise transform (like `flatMap`) backed by a `DoFn` where you implement
`process(element)` — it's the building block for most custom logic (filtering, formatting, side outputs,
calling external APIs with care for retries/batching).

**Q3: Explain windowing, watermarks, and triggers in Beam/Dataflow streaming.**

**Answer:** **Windowing** groups unbounded data into finite chunks by event time (fixed, sliding, or session
windows) so aggregations (`GroupByKey`, `Combine`) can run. A **watermark** is the system's estimate of
"event time up to which we believe all data has arrived" — it accounts for out-of-order/late data.
**Triggers** define *when* to emit a window's results relative to the watermark — e.g., emit once when
the watermark passes the window end (default), or emit early/speculative results plus late updates using
`AfterWatermark.pastEndOfWindow().withEarlyFirings(...).withLateFirings(...)`, combined with
`allowedLateness` to bound how long a window accepts late data before closing permanently.

**Q4: How does Dataflow autoscaling work, and what's the difference between Horizontal Autoscaling and
Streaming Engine?**

**Answer:** Dataflow monitors backlog (unprocessed data) and CPU utilization and adds/removes worker VMs
automatically within a configured min/max range (horizontal autoscaling) — for streaming jobs this reacts
to growing Pub/Sub backlog; for batch, it scales based on remaining work. **Streaming Engine** moves
shuffle/state/windowing bookkeeping off worker VMs into a managed backend service, which decouples compute
scaling from state storage, improves autoscaling responsiveness and reduces worker resource needs
(smaller/fewer VMs needed), and is the modern default for streaming pipelines. Similarly, **Dataflow
Shuffle** does the analogous thing for batch jobs' shuffle phase.

**Q5: How do you handle a dead-letter / error pattern in a Beam pipeline (e.g., malformed records)?**

**Answer:** Use `ParDo` with multiple outputs (`TaggedOutput`/`with_outputs` in Python) — the `DoFn.process` method
emits good records to the main output and problematic records (with error context) to a side output tag,
which is then written to a dead-letter sink (a GCS bucket or a BigQuery error table) instead of failing the
whole pipeline/bundle. This isolates bad data for later inspection/reprocessing without blocking the
happy path.

**Q6: What's a Dataflow template (classic vs Flex) and why use one?**

**Answer:** Templates package a pipeline so it can be triggered/parameterized without needing the Beam SDK/dev
environment at run time — e.g., triggered from Cloud Composer, Cloud Scheduler, or a UI/REST call with
just input parameters (source table, target path). Classic templates stage an execution graph at build
time (more limited, static). Flex templates package the pipeline as a Docker image, allowing arbitrary
runtime logic, dynamic graph construction, and dependency flexibility — Flex templates are the current
recommended approach, and Google ships many prebuilt Flex templates (e.g., "Pub/Sub Topic to BigQuery",
"GCS Text to BigQuery").

**Q7: How do you ensure exactly-once / idempotent processing in a Dataflow pipeline writing to BigQuery?**

**Answer:** Beam's model guarantees each record is processed at-least-once with fault-tolerant retries; true
end-to-end exactly-once depends on the sink. The BigQueryIO sink (using the Storage Write API) supports
effectively-once semantics via dedup. For custom sinks/side effects (e.g., calling an external API),
design `DoFn`s to be idempotent (keyed on a natural/business key so repeated delivery doesn't double-apply
effects), and avoid relying on local in-memory state across bundle retries since bundles can be reprocessed
on worker failure.

**Q8: How would you design a streaming pipeline: Pub/Sub → Dataflow → BigQuery, with late data handling?**

**Answer:** Pub/Sub topic + subscription as the unbounded source (see [../pubsub/guide](../pubsub/guide.md));
Dataflow pipeline reads with `ReadFromPubSub`, parses/validates (dead-letter malformed messages), assigns
event-time windows (e.g., fixed 5-minute windows) based on a timestamp field in the payload (not
processing time, to handle out-of-order delivery), applies `allowedLateness` (e.g., 1 hour) to tolerate
late events, aggregates with `Combine`/`GroupByKey`, and writes to BigQuery via `WriteToBigQuery` with the
Storage Write API, with retries/dead-letter path for write failures. Monitor pipeline lag (Dataflow's
system lag / Pub/Sub unacked message count) for SLA alerting.

**Q9: What monitoring/alerting do you set up for Dataflow pipelines?**

**Answer:** Cloud Monitoring dashboards for system lag, data freshness, autoscaling worker count, and per-stage
throughput; alert on growing Pub/Sub subscription backlog or persistent system lag growth (indicates the
pipeline falling behind). Integrate with Cloud Composer's SLA/callback alerting for end-to-end pipeline
freshness where Dataflow jobs are orchestrated from Airflow.

**Q10: Beam Combine vs GroupByKey — when to use which, and why does it matter for performance?**

**Answer:** `GroupByKey` collects all values per key into an iterable before you process them — requires
materializing the full group, which can be expensive/skewed for hot keys. `Combine` (e.g.,
`CombinePerKey(sum)`) uses an associative/commutative combiner function that can partially aggregate
values on the mapper side before the shuffle (similar to a combiner in MapReduce), drastically reducing
data shuffled, especially valuable for simple aggregations (sum/count/mean) on high-cardinality or
hot-key streaming data.

**Q11: How would you backfill historical data through a Dataflow streaming pipeline without disrupting
live traffic?**

**Answer:** Options: (a) run a separate **batch** Dataflow pipeline (same transform logic, reused via a shared
Beam `PTransform` library) reading historical data from GCS/BigQuery for the backfill window, writing to
the same sink with idempotent keys; (b) replay historical events into a separate Pub/Sub topic/
subscription consumed by a temporary pipeline instance, to reuse the exact streaming DoFns; avoid replaying
into the *production* topic/subscription directly, which would mix backfill with live traffic and skew
windowing/watermarks.

**Q12: What's the Dataflow "Runner" concept, and have you run Beam pipelines on anything besides
Dataflow?**

**Answer:** Beam is runner-agnostic — the same pipeline code can execute on DataflowRunner (GCP managed),
DirectRunner (local, for testing/dev), FlinkRunner, or SparkRunner. In practice, DirectRunner is used for
unit/integration tests in CI (fast, local, no GCP cost), and DataflowRunner for actual deployment — this
portability is part of Beam's value proposition versus being locked to a single engine's API.
