# Ingesting and Processing Data

## 1. Batch vs Streaming
| | Batch | Streaming |
|---|---|---|
| Latency | Minutes–hours | Seconds–subsecond |
| Use cases | Daily reports, historical loads, ETL migrations | Fraud detection, IoT telemetry, live dashboards |
| GCP tools | Dataflow (batch mode), Dataproc, BigQuery load jobs, Storage Transfer Service | Pub/Sub, Dataflow (streaming mode), Bigtable, BigQuery streaming inserts |

## 2. Pub/Sub (Messaging)
- Fully managed, global, at-least-once delivery, asynchronous messaging (pub/sub pattern).
- Decouples producers and consumers; buffers data during traffic spikes.
- **Pub/Sub Lite**: cheaper, zonal, for cost-sensitive high-throughput workloads where you manage partitions/capacity yourself.
- Key concepts: **Topic**, **Subscription** (pull or push), **Message ordering** (via ordering keys), **Dead-letter topics** for failed messages, **Schema support** (Avro/Protobuf) for validation.
- Retention: messages retained up to 7 days (configurable) even after ack, for replay.
- Exactly-once processing: Pub/Sub supports exactly-once delivery semantics when combined with proper subscriber acking (seek + ordering keys).

## 3. Dataflow (Apache Beam — unified batch/streaming)
- Fully managed, serverless, autoscaling execution of Apache Beam pipelines.
- Same code model (`PCollection`, `PTransform`) works for both batch and streaming — big exam differentiator vs Spark (Dataproc) which needs separate APIs.
- **Windowing** (streaming): Fixed, Sliding, Session windows — groups unbounded data into finite chunks for aggregation.
  - **Watermarks**: track event-time progress; handle **late data** with `allowed lateness` + triggers.
  - **Triggers**: control when results are emitted (event time, processing time, early/late firing).
- **Side inputs**: broadcast small datasets (e.g., lookup tables) to all workers.
- **Dataflow templates**: reusable, parameterized pipelines (classic & Flex templates) — useful for self-service / non-engineer execution.
- Autoscaling workers up/down based on backlog; use **Streaming Engine** to separate compute from state for better scaling.
- When to choose: new pipelines, unified batch+streaming, minimal ops overhead, tight GCP integration.

## 4. Dataproc (Managed Hadoop/Spark)
- Use when: **migrating existing Hadoop/Spark/Hive/Pig jobs** ("lift and shift"), team has existing Spark skills, need specific Spark/Hadoop ecosystem tools (e.g., Presto, Zeppelin).
- Ephemeral clusters recommended: spin up cluster per job, write output to GCS/BigQuery, then delete cluster → saves cost (vs long-running clusters).
- Supports **autoscaling policies** and **preemptible/spot VMs** for cost savings on non-critical batch jobs.
- Can separate storage (GCS via the GCS connector) from compute, unlike on-prem HDFS-bound clusters.
- Dataproc Serverless: run Spark batch jobs without managing clusters at all.

## 5. Cloud Data Fusion
- Fully managed, visual, code-free ETL/ELT tool (built on open-source CDAP).
- Good for teams without strong coding skills who need drag-and-drop pipeline building with many pre-built connectors.

## 6. Cloud Composer (Orchestration)
- Managed Apache Airflow. Use for orchestrating **multi-step, multi-service workflows** (e.g., "run Dataproc job, then load to BigQuery, then trigger ML pipeline") with dependencies, retries, scheduling, SLA alerting.
- DAGs (Directed Acyclic Graphs) define task order; use **Sensors** to wait on external events.

## 7. Transfer Services
- **Storage Transfer Service**: scheduled/one-time transfer from on-prem, S3, Azure Blob, or other GCS buckets into Cloud Storage.
- **Transfer Appliance**: physical hardware shipped for large (petabyte-scale) offline data migration.
- **BigQuery Data Transfer Service**: scheduled ingestion from SaaS apps (Google Ads, YouTube, etc.) directly into BigQuery.

## 8. Common Pipeline Patterns (exam favorites)
- **IoT ingestion**: Devices → Pub/Sub → Dataflow (streaming, windowed aggregation) → Bigtable (time-series) or BigQuery (analytics) → Looker Studio/Looker for dashboards.
- **Batch ETL migration from Hadoop**: On-prem HDFS → Storage Transfer Service/Transfer Appliance → GCS → Dataproc (Spark) transform → BigQuery.
- **Change Data Capture (CDC)**: Datastream (CDC service) captures DB changes → BigQuery/GCS for near-real-time replication without custom code.
- **Error handling**: use dead-letter queues/topics in Pub/Sub and Dataflow for malformed records; never silently drop data.
