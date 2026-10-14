# Mock Questions: Ingesting and Processing Data (Q1–Q100)

---

**Q1.** You need a service to decouple a fleet of producers from multiple downstream consumers, with at-least-once delivery, at global scale, without managing any servers.
A) Pub/Sub
B) Cloud Tasks
C) Apache Kafka self-hosted on GCE
D) Cloud Scheduler

**Correct answer: A**
**Why A is correct:** Pub/Sub is a fully managed, global, serverless messaging service built exactly for decoupled async pub/sub patterns with at-least-once delivery.
**Why the others are wrong:**
- B) Cloud Tasks is for managing discrete task execution/retries against a specific endpoint, not fan-out pub/sub messaging.
- C) Self-hosted Kafka requires managing servers, violating "without managing any servers."
- D) Cloud Scheduler only triggers jobs on a schedule; it is not a messaging/queueing system.

---

**Q2.** Your Pub/Sub subscriber occasionally receives messages out of order, but your use case (bank transaction processing per account) requires per-account ordering.
A) Switch to Cloud Tasks
B) Use ordering keys scoped per account
C) Add a global lock in the subscriber
D) Increase the number of subscriptions

**Correct answer: B**
**Why B is correct:** Pub/Sub supports message ordering when you set an ordering key; messages with the same key are delivered in the order they were published, per key (e.g., per account ID).
**Why the others are wrong:**
- A) Cloud Tasks doesn't provide pub/sub fan-out semantics needed here.
- C) A global lock doesn't guarantee ordering and creates a bottleneck/anti-pattern.
- D) More subscriptions does not address ordering; it affects fan-out distribution, not sequence.

---

**Q3.** You need the cheapest Pub/Sub-like option for a very high-throughput workload where you're willing to manage partitioning and capacity planning yourself.
A) Pub/Sub Lite
B) Pub/Sub
C) Cloud Storage notifications
D) Firestore triggers

**Correct answer: A**
**Why A is correct:** Pub/Sub Lite offers significantly lower cost for high-throughput workloads in exchange for manual capacity/partition management (zonal, not globally managed like Pub/Sub).
**Why the others are wrong:**
- B) Pub/Sub is fully managed but costs more and doesn't require manual partition management — it fails the "manage yourself for lower cost" requirement.
- C) GCS notifications are event triggers for bucket changes, not a general messaging backbone.
- D) Firestore triggers only fire on document changes; not a general-purpose high-throughput message bus.

---

**Q4.** Malformed messages are occasionally published to a Pub/Sub topic and crash the Dataflow pipeline consuming them. What should you configure to prevent pipeline failures without losing the bad data?

A) Increase Dataflow worker count
B) Configure a dead-letter topic on the subscription
C) Delete malformed messages manually
D) Pause the subscription until fixed

**Correct answer: B**
**Why B is correct:** A dead-letter topic captures messages that fail processing after a configured number of delivery attempts, isolating bad data for later inspection while letting the main pipeline continue.
**Why the others are wrong:**
- A) More workers doesn't fix malformed-data crashes; it's a scaling lever, not an error-handling one.
- C) Manual deletion loses data and doesn't scale as an operational practice.
- D) Pausing halts all processing, including valid messages — unacceptable for most SLAs.

---

**Q5.** A schema change in upstream producers is silently breaking downstream Pub/Sub consumers. What feature should be used going forward to catch this at publish time?
A) Pub/Sub schema validation (Avro/Protobuf)
B) Cloud Logging alerts
C) BigQuery schema auto-detect
D) Dataflow side inputs

**Correct answer: A**
**Why A is correct:** Pub/Sub lets you attach a schema (Avro or Protobuf) to a topic; publishers must conform, so incompatible messages are rejected at publish time instead of breaking consumers downstream.
**Why the others are wrong:**
- B) Logging alerts are reactive (after failure), not preventive.
- C) BigQuery schema auto-detect applies to load jobs, not to Pub/Sub message validation.
- D) Side inputs are a Dataflow concept for broadcasting auxiliary data, unrelated to schema enforcement.

---

**Q6.** Which Apache Beam/Dataflow concept lets you group unbounded streaming data into finite chunks (e.g., 5-minute intervals) for aggregation?
A) Side inputs
B) Windowing
C) Flex templates
D) Autoscaling

**Correct answer: B**
**Why B is correct:** Windowing (fixed, sliding, or session windows) is exactly the Beam mechanism for bucketing unbounded data by time for aggregation.
**Why the others are wrong:**
- A) Side inputs broadcast auxiliary/reference data to all workers; unrelated to time-based grouping.
- C) Flex templates package and parameterize pipelines for reuse; not a data-grouping concept.
- D) Autoscaling adjusts worker count for load; doesn't group data.

---

**Q7.** Mobile clients sometimes go offline for hours, causing events to arrive well after their event-time window has closed. You must still incorporate this late data into results.
A) Reduce window size to 1 second
B) Configure allowed lateness and appropriate triggers
C) Discard all late data to keep pipeline simple
D) Switch to batch processing only

**Correct answer: B**
**Why B is correct:** Beam's `allowed lateness` extends how long a window stays open for late data, and triggers (early/on-time/late firings) let you emit updated results as late data arrives.
**Why the others are wrong:**
- A) Smaller windows don't address lateness; they only change aggregation granularity.
- C) Discarding violates the stated requirement to incorporate late data.
- D) Pure batch loses the real-time/near-real-time requirement implied by streaming mobile events.

---

**Q8.** You want to broadcast a small reference/lookup table (e.g., currency exchange rates) to every worker in a Dataflow pipeline without re-reading it per element.
A) Side input
B) Dead-letter topic
C) Windowing
D) BigQuery streaming insert

**Correct answer: A**
**Why A is correct:** Side inputs are designed exactly for broadcasting a bounded, relatively small auxiliary dataset to all workers for use during processing (e.g., a `PCollectionView` used as a lookup map).
**Why the others are wrong:**
- B) Dead-letter topics handle failed messages, not lookup data distribution.
- C) Windowing groups the main data stream by time; unrelated to auxiliary data.
- D) Streaming insert is how data gets written to BigQuery, not how reference data is distributed to workers.

---

**Q9.** Your organization wants non-engineers to be able to run a parameterized Dataflow pipeline (e.g., specifying an input/output path) through a simple UI/API call.
A) Classic or Flex Dataflow templates
B) Raw Beam pipeline source code
C) Cloud Composer DAG only
D) BigQuery scheduled query

**Correct answer: A**
**Why A is correct:** Dataflow templates package a pipeline with defined runtime parameters so it can be launched via Console, gcloud, or API without touching code — ideal for self-service by non-engineers.
**Why the others are wrong:**
- B) Raw source code requires engineering knowledge to run/modify, which the requirement explicitly avoids.
- C) Composer orchestrates jobs but doesn't itself provide the simple parameterized launch UI described (though it could invoke a template).
- D) Scheduled queries are a BigQuery feature, not a Dataflow mechanism.

---

**Q10.** A Dataflow streaming job's backlog is growing because it can't keep up with incoming Pub/Sub volume during traffic spikes. What addresses this automatically?
A) Dataflow horizontal autoscaling
B) Manually fixing the worker count higher permanently
C) Disabling retries
D) Switching the job to batch mode

**Correct answer: A**
**Why A is correct:** Dataflow's autoscaling (especially with Streaming Engine) automatically adds workers when backlog/throughput demands increase, and scales back down when load drops — no manual intervention or static over-provisioning needed.
**Why the others are wrong:**
- B) Statically higher worker count wastes money during low-traffic periods — not cost-efficient compared to autoscaling.
- C) Disabling retries risks data loss and doesn't solve throughput.
- D) Batch mode breaks the real-time/streaming nature of the requirement.

---

**Q11.** You are migrating 200 existing on-premises Spark and Hive jobs to GCP. The team has deep Spark expertise and a tight deadline. Which service minimizes rewrite effort?
A) Dataproc
B) Dataflow
C) BigQuery scheduled queries
D) Cloud Functions

**Correct answer: A**
**Why A is correct:** Dataproc is managed Hadoop/Spark/Hive, so existing Spark/Hive jobs can run largely unchanged (lift-and-shift), matching the tight deadline and existing skill set.
**Why the others are wrong:**
- B) Dataflow uses the Beam programming model; migrating Spark/Hive jobs would require a full rewrite, inconsistent with "minimize rewrite effort."
- C) BigQuery scheduled queries only run SQL, not arbitrary Spark/Hive jobs.
- D) Cloud Functions are for lightweight event-driven code, not large-scale Spark/Hive batch processing.

---

**Q12.** To minimize cost for a nightly Dataproc Spark batch job that can tolerate node preemption, what should you use?
A) Standard (non-preemptible) VMs only
B) Preemptible/Spot VMs for worker nodes
C) A permanently running cluster sized for peak load
D) Dedicated sole-tenant nodes

**Correct answer: B**
**Why B is correct:** Preemptible/Spot VMs are significantly cheaper and well-suited to fault-tolerant, restartable batch jobs like nightly Spark jobs, since occasional preemption is acceptable here.
**Why the others are wrong:**
- A) Standard VMs cost more with no benefit for a job that tolerates preemption.
- C) An always-on cluster sized for peak load incurs unnecessary idle cost; ephemeral clusters are preferred.
- D) Sole-tenant nodes address compliance/isolation needs, not cost minimization, and cost more.

---

**Q13.** What is the recommended Dataproc cluster pattern to minimize cost when running discrete, scheduled batch jobs?
A) One large cluster running continuously for all jobs
B) Ephemeral clusters created per job and deleted afterward
C) Manually resizing a static cluster each night
D) Running jobs on a single-node cluster always

**Correct answer: B**
**Why B is correct:** Ephemeral (per-job) clusters mean you only pay for compute while the job runs; storing data in GCS (not HDFS) lets you safely delete the cluster afterward — the standard GCP cost-saving pattern.
**Why the others are wrong:**
- A) A continuously running cluster incurs idle cost between jobs.
- C) Manual resizing is operationally heavy and error-prone vs. automation/ephemeral patterns.
- D) Single-node clusters limit throughput/parallelism and aren't a cost-optimization "pattern," just undersizing.

---

**Q14.** Which Dataproc feature lets the cluster automatically add/remove worker nodes based on YARN pending memory, without manual intervention?
A) Autoscaling policies
B) Initialization actions
C) Component gateway
D) Cloud Scheduler triggers

**Correct answer: A**
**Why A is correct:** Dataproc autoscaling policies monitor YARN metrics and automatically scale the cluster's secondary workers up/down to match workload.
**Why the others are wrong:**
- B) Initialization actions run custom setup scripts at cluster creation; they don't perform ongoing scaling.
- C) Component gateway provides secure web UI access to cluster components (e.g., Spark UI); unrelated to scaling.
- D) Cloud Scheduler can trigger jobs on a schedule but doesn't dynamically scale a running cluster based on load.

---

**Q15.** You want a no-code, drag-and-drop ETL tool with many pre-built connectors for a team with limited coding experience.
A) Cloud Data Fusion
B) Dataproc with raw Spark code
C) Dataflow with custom Beam code
D) Cloud Functions

**Correct answer: A**
**Why A is correct:** Cloud Data Fusion is a fully managed, visual ETL/ELT tool (built on CDAP) specifically designed for code-free pipeline building with many connectors.
**Why the others are wrong:**
- B) Requires Spark coding expertise, contradicting "limited coding experience."
- C) Requires writing Beam pipeline code.
- D) Cloud Functions is for lightweight event-driven snippets, not visual ETL pipeline design.

---

**Q16.** You need to orchestrate a workflow: run a Dataproc Spark job, then on success load results into BigQuery, then trigger a Vertex AI pipeline, with retry logic and SLA alerting across all steps.
A) Cloud Scheduler
B) Cloud Composer
C) A single Dataflow job
D) Pub/Sub only

**Correct answer: B**
**Why B is correct:** Cloud Composer (managed Airflow) is built for exactly this kind of multi-step, multi-service DAG orchestration with dependencies, retries, and SLA monitoring.
**Why the others are wrong:**
- A) Cloud Scheduler only triggers single jobs/endpoints on a schedule; no multi-step dependency management.
- C) Dataflow executes a single data processing pipeline; it doesn't orchestrate heterogeneous cross-service workflows.
- D) Pub/Sub is messaging, not a workflow orchestrator with retries/SLAs.

---

**Q17.** A lightweight workflow just needs to call three REST APIs in sequence with basic branching logic, without the overhead of a full Airflow environment.
A) Cloud Composer
B) Workflows
C) Dataproc
D) BigQuery Data Transfer Service

**Correct answer: B**
**Why B is correct:** Workflows is a lightweight, serverless orchestrator ideal for simple HTTP/API call sequencing without needing a full Airflow (Composer) environment.
**Why the others are wrong:**
- A) Composer carries more operational overhead (a persistent Airflow environment) than needed for this simple case.
- C) Dataproc runs Hadoop/Spark jobs; not an API orchestration tool.
- D) BigQuery Data Transfer Service is for scheduled data ingestion from SaaS sources, not generic API orchestration.

---

**Q18.** Which Airflow/Composer concept defines the order and dependencies of tasks in a pipeline?
A) DAG (Directed Acyclic Graph)
B) Side input
C) Watermark
D) Dead-letter queue

**Correct answer: A**
**Why A is correct:** A DAG defines tasks and their dependency order in Airflow/Composer — the core orchestration structure.
**Why the others are wrong:**
- B) Side input is a Beam/Dataflow concept for broadcast data.
- C) Watermark is a Beam streaming concept tracking event-time progress.
- D) Dead-letter queue is an error-isolation pattern, not a workflow structure.

---

**Q19.** You need to migrate 2 PB of on-premises data to Cloud Storage, but your network link is too slow to transfer it in a reasonable time.
A) Storage Transfer Service over the network
B) Transfer Appliance (physical hardware)
C) gsutil cp over the internet
D) Pub/Sub

**Correct answer: B**
**Why B is correct:** Transfer Appliance is a physical device shipped to your site to capture large (petabyte-scale) datasets offline and ship them to Google for upload — built exactly for slow-network/huge-data scenarios.
**Why the others are wrong:**
- A) Storage Transfer Service still relies on network transfer, which is the stated bottleneck.
- C) gsutil cp is a manual CLI tool, impractical and slow at petabyte scale over a poor link.
- D) Pub/Sub is a messaging service, not a bulk data migration tool.

---

**Q20.** You need to perform a one-time scheduled sync of files from an Amazon S3 bucket into Cloud Storage with minimal custom code.
A) Transfer Appliance
B) Storage Transfer Service
C) Datastream
D) Cloud Data Fusion only

**Correct answer: B**
**Why B is correct:** Storage Transfer Service natively supports scheduled or one-time transfers from S3 (and other clouds/HTTP sources/on-prem) into GCS without custom coding.
**Why the others are wrong:**
- A) Transfer Appliance is for offline/physical large-scale migration, overkill for a scheduled S3 sync.
- C) Datastream is for database Change Data Capture, not generic object storage sync.
- D) Data Fusion could be configured for this but requires more setup than the purpose-built Storage Transfer Service.

---

**Q21.** You need near-real-time replication of changes from a production MySQL database into BigQuery for analytics, without writing custom CDC code.
A) Datastream
B) Storage Transfer Service
C) Pub/Sub Lite
D) Cloud SQL export to CSV nightly

**Correct answer: A**
**Why A is correct:** Datastream is GCP's managed Change Data Capture (CDC) service, specifically designed to stream database changes (e.g., MySQL, Oracle, PostgreSQL) into BigQuery/GCS in near real time.
**Why the others are wrong:**
- B) Storage Transfer Service moves objects/files, not live database change streams.
- C) Pub/Sub Lite is generic messaging; you'd still need to build the CDC logic yourself.
- D) Nightly CSV export is batch, not near-real-time, and is more custom/manual than Datastream.

---

**Q22.** Which combination best supports an IoT architecture ingesting millions of sensor events/second and performing windowed aggregation before storage?
A) Cloud Functions + Cloud SQL
B) Pub/Sub + Dataflow (streaming, windowed) + Bigtable/BigQuery
C) Storage Transfer Service + Dataproc batch
D) Cloud Scheduler + BigQuery load jobs

**Correct answer: B**
**Why B is correct:** Pub/Sub ingests high-throughput events, Dataflow performs windowed streaming aggregation, and Bigtable (time-series lookups) or BigQuery (analytics) stores results — this is the canonical GCP IoT streaming pattern.
**Why the others are wrong:**
- A) Cloud Functions don't scale well for sustained millions-of-events/sec stateful aggregation; Cloud SQL isn't built for this throughput.
- C) Storage Transfer Service moves files, not live event streams; Dataproc batch isn't real-time.
- D) Cloud Scheduler is for scheduled triggers, not continuous ingestion; BigQuery load jobs are batch-oriented.

---

**Q23.** In Apache Beam, what tracks how complete the input data is with respect to event time, helping decide when a window can be considered "done"?
A) Watermark
B) Trigger
C) Template
D) Dead-letter topic

**Correct answer: A**
**Why A is correct:** The watermark is Beam's estimate of event-time completeness — it tells the system "we believe all data up to this time has arrived," driving default window closing behavior.
**Why the others are wrong:**
- B) Triggers decide *when* to emit results relative to the watermark/processing time, not track completeness itself.
- C) Templates are a packaging/deployment mechanism, unrelated to event-time tracking.
- D) Dead-letter topics isolate failed messages; unrelated concept.

---

**Q24.** Which Beam concept allows you to emit early (speculative), on-time, and late results for the same window as data arrives?
A) Trigger
B) Side input
C) Flex template
D) Autoscaling policy

**Correct answer: A**
**Why A is correct:** Triggers explicitly control when a window emits its results — supporting early/on-time/late firings as needed.
**Why the others are wrong:**
- B) Side inputs broadcast static/auxiliary data; unrelated to emission timing.
- C) Flex templates package pipelines for parameterized launch.
- D) Autoscaling policies control compute resources, not emission timing.

---

**Q25.** Your streaming pipeline must guarantee that reprocessing the same Pub/Sub message after a transient failure doesn't create duplicate rows in BigQuery. What design principle addresses this?
A) Idempotent writes (e.g., upsert/dedupe by message ID)
B) Increasing subscriber acknowledgment deadline
C) Disabling retries entirely
D) Using more Dataflow workers

**Correct answer: A**
**Why A is correct:** Designing writes to be idempotent (e.g., using a unique message ID to dedupe or upsert) ensures that redelivery/retries don't produce duplicate data, which is essential since Pub/Sub provides at-least-once delivery.
**Why the others are wrong:**
- B) Longer ack deadlines reduce premature redelivery but don't eliminate duplicates outright.
- C) Disabling retries risks losing data on transient failures.
- D) More workers affects throughput/scaling, not duplicate prevention.

---

**Q26.** You need to ingest clickstream data from a web app and immediately make it queryable in BigQuery with sub-minute latency, without an intermediate processing step.
A) BigQuery streaming inserts
B) BigQuery batch load jobs once per day
C) Storage Transfer Service
D) Transfer Appliance

**Correct answer: A**
**Why A is correct:** BigQuery streaming inserts make rows available for query almost immediately (seconds), satisfying sub-minute latency without needing full Dataflow/Dataproc pipelines for simple direct ingestion.
**Why the others are wrong:**
- B) Daily batch loads violate the sub-minute latency requirement.
- C) Storage Transfer Service moves objects between storage systems, not individual streaming records into BigQuery tables.
- D) Transfer Appliance is for offline bulk migration, irrelevant to live clickstream ingestion.

---

**Q27.** A pipeline ingesting from Pub/Sub needs to be tested locally before deploying to Dataflow, using the same Beam pipeline code. What enables this?
A) The Beam DirectRunner
B) Dataproc
C) BigQuery sandbox
D) Pub/Sub Lite

**Correct answer: A**
**Why A is correct:** Apache Beam's DirectRunner executes pipelines locally for testing/development, using the identical pipeline code that later runs on DataflowRunner in production.
**Why the others are wrong:**
- B) Dataproc runs Spark/Hadoop jobs, a different programming model than Beam.
- C) BigQuery sandbox is for exploring BigQuery without billing setup, unrelated to pipeline testing.
- D) Pub/Sub Lite is a messaging tier choice, not a pipeline execution/test environment.

---

**Q28.** Which GCP service would you choose to ingest data from Google Ads, YouTube, and other Google SaaS products directly into BigQuery on a schedule, with no custom code?
A) BigQuery Data Transfer Service
B) Datastream
C) Pub/Sub
D) Cloud Data Fusion only

**Correct answer: A**
**Why A is correct:** BigQuery Data Transfer Service has built-in connectors specifically for Google SaaS products (Ads, YouTube, etc.) enabling scheduled, code-free ingestion into BigQuery.
**Why the others are wrong:**
- B) Datastream targets database CDC, not SaaS application data.
- C) Pub/Sub would require you to build the SaaS integration yourself.
- D) Data Fusion could work but is a heavier, more general tool than the purpose-built Transfer Service for this exact use case.

---

**Q29.** When should you prefer Dataflow over Dataproc for a brand-new data pipeline (no existing code)?
A) When you need unified batch and streaming with minimal operations overhead
B) When your team only knows Spark/Scala
C) When you need HDFS compatibility
D) When you must use YARN resource management

**Correct answer: A**
**Why A is correct:** For new pipelines, Dataflow (Beam) provides a single programming model for batch and streaming, fully managed/serverless, minimizing ops overhead — the ideal default choice absent legacy constraints.
**Why the others are wrong:**
- B) Existing Spark/Scala skills point toward Dataproc instead, not Dataflow.
- C) HDFS compatibility is a Hadoop/Dataproc ecosystem feature, irrelevant to Dataflow.
- D) YARN is Hadoop's resource manager, used by Dataproc, not Dataflow.

---

**Q30.** What is the primary reason to avoid long-running, always-on Dataproc clusters for periodic nightly batch jobs?
A) They can't run Spark jobs
B) They incur unnecessary idle compute cost
C) They don't support preemptible VMs
D) They can't connect to Cloud Storage

**Correct answer: B**
**Why B is correct:** An always-on cluster keeps paying for compute even when idle between nightly runs; ephemeral clusters created per job avoid this waste.
**Why the others are wrong:**
- A) Dataproc clusters absolutely run Spark jobs — that's their main purpose.
- C) Dataproc does support preemptible/Spot VMs even on long-running clusters.
- D) Dataproc fully supports the GCS connector regardless of cluster lifetime.

---

**Q31.** A Pub/Sub subscription uses the pull delivery method, but you want GCP to push messages directly to an HTTPS endpoint you control instead. What should you configure?
A) A push subscription
B) A dead-letter topic
C) An ordering key
D) A schema

**Correct answer: A**
**Why A is correct:** Push subscriptions have Pub/Sub actively deliver messages via HTTP POST to a configured endpoint, as opposed to pull subscriptions where the consumer polls.
**Why the others are wrong:**
- B) Dead-letter topics handle failed message routing, unrelated to delivery method.
- C) Ordering keys control message order, not delivery mechanism.
- D) Schemas validate message structure, unrelated to push vs. pull delivery.

---

**Q32.** You need to reprocess the last 3 days of messages from a Pub/Sub subscription after fixing a bug in your consumer logic. What feature enables this?
A) Seek (replay via message retention)
B) Ordering keys
C) Push subscriptions
D) Flex templates

**Correct answer: A**
**Why A is correct:** Pub/Sub retains acknowledged messages for a configurable period (up to 7+ days) and supports `seek` to a timestamp, allowing you to replay/reprocess historical messages within that window.
**Why the others are wrong:**
- B) Ordering keys control delivery order, not replay capability.
- C) Push subscriptions only change delivery mechanism, not retention/replay.
- D) Flex templates relate to Dataflow pipeline packaging, not Pub/Sub message replay.

---

**Q33.** Which statement about Dataflow Streaming Engine is correct?
A) It moves pipeline state/processing off worker VMs for more efficient autoscaling
B) It replaces the need for Pub/Sub entirely
C) It only works for batch pipelines
D) It is a Dataproc-only feature

**Correct answer: A**
**Why A is correct:** Streaming Engine separates compute from state management, moving state handling off worker VMs, enabling smaller/faster-scaling workers and more efficient autoscaling for streaming jobs.
**Why the others are wrong:**
- B) Streaming Engine is a Dataflow execution feature, not a messaging replacement for Pub/Sub.
- C) It specifically targets streaming pipelines, not batch.
- D) It's a Dataflow feature, unrelated to Dataproc.

---

**Q34.** A finance company needs exactly-once semantics end-to-end from Pub/Sub through Dataflow into BigQuery. What is the most accurate statement?
A) Pub/Sub + Dataflow can achieve effectively-once processing using Beam's exactly-once sink support combined with deduplication
B) Exactly-once is impossible on GCP
C) Only Dataproc guarantees exactly-once
D) You must use Cloud SQL instead of BigQuery

**Correct answer: A**
**Why A is correct:** While Pub/Sub provides at-least-once delivery, Dataflow/Beam provides exactly-once processing guarantees within the pipeline, and BigQuery sinks with proper deduplication (e.g., insertId) achieve effectively-once end-to-end results.
**Why the others are wrong:**
- B) It is achievable with the right design, not impossible.
- C) Dataproc/Spark doesn't inherently provide stronger guarantees here; this isn't a Dataproc-specific feature.
- D) Switching databases doesn't address the processing semantics question.

---

**Q35.** Your company wants a managed ETL tool with a visual pipeline designer so business analysts (not just engineers) can build data pipelines connecting to many sources (SaaS, databases, files).
A) Cloud Data Fusion
B) Raw Dataflow Java SDK
C) Dataproc with PySpark
D) Cloud Functions

**Correct answer: A**
**Why A is correct:** Cloud Data Fusion's visual, drag-and-drop interface with a large connector library is designed for business/analyst users to build pipelines without deep coding skills.
**Why the others are wrong:**
- B) Writing raw Java SDK pipelines requires strong engineering skills.
- C) PySpark requires coding and Spark knowledge.
- D) Cloud Functions require writing and deploying code snippets, not visual pipeline design.

---

**Q36.** What should you use to run a parameterized, templated Dataflow job on a recurring daily schedule?
A) Cloud Scheduler triggering the Dataflow template
B) Manually launching the job each day
C) Pub/Sub ordering keys
D) BigQuery materialized views

**Correct answer: A**
**Why A is correct:** Cloud Scheduler can invoke a Dataflow template (via HTTP/Cloud Functions or direct integration) on a cron schedule, automating recurring template-based job launches.
**Why the others are wrong:**
- B) Manual daily launches don't scale operationally and are error-prone.
- C) Ordering keys are unrelated to scheduling.
- D) Materialized views are a BigQuery query optimization feature, unrelated to job scheduling.

---

**Q37.** Which is true regarding Dataproc vs. Dataflow for a pipeline requiring custom, complex Spark MLlib model training logic already written in Scala?
A) Dataproc is preferred since it runs native Spark/Scala code directly
B) Dataflow is preferred because it's always cheaper
C) Both are equally suited with zero migration effort
D) Neither supports machine learning workloads

**Correct answer: A**
**Why A is correct:** Since the logic is already in Scala/Spark MLlib, Dataproc lets you run it with little to no change, avoiding a costly rewrite into the Beam model that Dataflow would require.
**Why the others are wrong:**
- B) Cost depends on workload pattern, not a blanket rule, and ignores the rewrite cost implied by switching platforms.
- C) Migrating Scala/Spark code to Beam/Dataflow is a non-trivial rewrite, not "zero effort."
- D) Both platforms can support ML workloads in different ways; the statement is factually wrong.

---

**Q38.** You need to enrich streaming events with reference data stored in Bigtable during Dataflow processing, with low per-element latency. What pattern is appropriate?
A) Call Bigtable synchronously per element using the Bigtable I/O connector within a ParDo
B) Reload the entire Bigtable table as a side input every run
C) Write all events to GCS first, then join in a separate batch job
D) Avoid Bigtable entirely and hardcode values

**Correct answer: A**
**Why A is correct:** For large or frequently-changing reference data, performing a low-latency lookup against Bigtable directly within a ParDo (via the Bigtable connector) is the standard enrichment pattern, since Bigtable is built for millisecond-level point lookups.
**Why the others are wrong:**
- B) Side inputs are best for small, fairly static datasets that fit in memory — not ideal for large/frequently changing Bigtable tables.
- C) Writing to GCS and batch-joining introduces unacceptable latency for a streaming enrichment use case.
- D) Hardcoding values isn't scalable or maintainable and ignores the actual data source.

---

**Q39.** Your streaming pipeline ingests from multiple Pub/Sub topics and must apply different transformation logic per topic before a common aggregation step. What Beam concept supports branching/merging like this?
A) PCollection branching with multiple ParDo transforms, then Flatten to merge
B) Windowing only
C) A single monolithic ParDo
D) Cloud Composer sensors

**Correct answer: A**
**Why A is correct:** Beam pipelines naturally support branching a PCollection into multiple transform paths (different ParDos per topic) and later merging them back together using `Flatten`, enabling flexible per-source logic before common processing.
**Why the others are wrong:**
- B) Windowing groups by time, not by applying distinct per-source transformation logic.
- C) A single monolithic ParDo would need complex conditional logic internally, losing the clarity/maintainability of separate branches.
- D) Composer sensors are for workflow-level waiting on external events, not intra-pipeline data transformation branching.

---

**Q40.** A Dataproc job fails intermittently due to a dependency only available via a custom initialization script. Where should this script run?
A) As a Dataproc initialization action during cluster creation
B) Inside a BigQuery scheduled query
C) As a Cloud Function triggered after the job
D) Embedded directly in Pub/Sub message payloads

**Correct answer: A**
**Why A is correct:** Dataproc initialization actions are scripts executed on all nodes during cluster creation/startup — the correct place to install custom dependencies before jobs run.
**Why the others are wrong:**
- B) BigQuery scheduled queries only run SQL, unrelated to cluster node setup.
- C) Running after the job doesn't help the job itself start successfully.
- D) Pub/Sub payloads carry data, not cluster configuration scripts.

---

**Q41.** For cost-sensitive ingestion of a very high volume of click events where some message loss is tolerable and you want to manage partitions/throughput yourself, which Pub/Sub variant fits, and why would standard Pub/Sub be rejected here?
A) Pub/Sub Lite; standard Pub/Sub costs more for this throughput profile
B) Standard Pub/Sub; it's always cheaper at any scale
C) Cloud Tasks; built for exactly this
D) Firestore; built for exactly this

**Correct answer: A**
**Why A is correct:** Pub/Sub Lite is explicitly designed to reduce cost for very high throughput at the expense of manual partition/capacity management — matching the stated cost sensitivity and willingness to self-manage.
**Why the others are wrong:**
- B) Standard Pub/Sub is not always cheaper; at very high sustained throughput, Lite is typically more cost-effective.
- C) Cloud Tasks is for task/queue execution against endpoints, not high-throughput pub/sub messaging.
- D) Firestore is a document database, not a messaging system.

---

**Q42.** You need to run a one-off Spark batch job without provisioning or managing any cluster infrastructure at all.
A) Dataproc Serverless for Spark
B) A manually created long-running Dataproc cluster
C) Cloud Composer
D) BigQuery ML

**Correct answer: A**
**Why A is correct:** Dataproc Serverless lets you submit Spark batch workloads without creating or managing clusters — Google handles all infrastructure provisioning transparently.
**Why the others are wrong:**
- B) Manually created clusters require you to provision and eventually delete infrastructure yourself.
- C) Composer is an orchestrator, not a Spark execution engine.
- D) BigQuery ML trains models via SQL; it doesn't run general-purpose Spark code.

---

**Q43.** What's the key reason Dataflow is described as "unified" for batch and streaming, which Dataproc/Spark historically was not (prior to Structured Streaming maturity)?
A) The same Apache Beam pipeline code and APIs work for both bounded and unbounded PCollections
B) Dataflow only supports streaming, not batch
C) Dataflow requires separate SDKs for batch vs streaming
D) Dataproc cannot run any streaming jobs at all

**Correct answer: A**
**Why A is correct:** Apache Beam's core abstraction (PCollection, PTransform) treats batch (bounded) and streaming (unbounded) data uniformly, so the same pipeline logic/APIs apply to both — this is the defining "unified" characteristic.
**Why the others are wrong:**
- B) Dataflow fully supports batch pipelines as well as streaming.
- C) There is one unified Beam API, not separate SDKs per mode.
- D) Dataproc can run Spark Structured Streaming jobs; the statement is too absolute.

---

**Q44.** A pipeline needs to call a third-party REST API to enrich each streaming record, but the API has strict rate limits. What should you consider in your Dataflow design?
A) Throttling/batching calls and controlling parallelism (e.g., via GroupByKey or rate-limited DoFn) to respect the API's limits
B) Ignore rate limits since Dataflow autoscaling handles everything automatically
C) Switch to Dataproc since it has no rate-limit concerns
D) Remove the enrichment step entirely

**Correct answer: A**
**Why A is correct:** External rate limits require explicit pipeline design (e.g., limiting concurrent calls, batching requests, or adding a custom rate limiter in the DoFn); autoscaling alone doesn't understand external-system quotas.
**Why the others are wrong:**
- B) Autoscaling scales Dataflow workers but has no awareness of third-party API quotas — it can actually make rate-limit violations worse.
- C) Switching engines doesn't eliminate an external API's own rate limits.
- D) Removing enrichment defeats the pipeline's purpose; a real solution designs around the constraint instead.

---

**Q45.** Which is the best approach to validate incoming JSON event structure before it enters your main processing logic in a streaming pipeline?
A) Attach a Pub/Sub schema and/or validate early in the Dataflow pipeline, routing invalid records to a dead-letter output
B) Let invalid records crash the pipeline so you notice immediately
C) Validate only once a day in a separate batch job
D) Perform validation only in the BigQuery table after load

**Correct answer: A**
**Why A is correct:** Validating early (schema enforcement at Pub/Sub and/or explicit validation transforms in Dataflow) with dead-letter routing for invalid records keeps the main pipeline resilient and makes bad data visible without crashing the job.
**Why the others are wrong:**
- B) Crashing the pipeline on bad data harms availability and violates reliability best practices.
- C) Daily batch validation introduces unacceptable delay for a streaming system and lets bad data flow downstream in the meantime.
- D) Validating only after BigQuery load means bad/malformed data may already have caused failures or corrupted earlier processing steps.

---

**Q46.** What's an appropriate reason to choose Cloud Composer over Workflows for orchestration?
A) You need complex dependency graphs, retries, backfills, and a large ecosystem of pre-built operators/sensors across many GCP and third-party services
B) You only need to call two REST endpoints in sequence
C) You want the absolute lowest operational overhead
D) You don't need scheduling at all

**Correct answer: A**
**Why A is correct:** Composer's Airflow foundation shines for complex multi-service DAGs, backfilling historical runs, and leveraging the rich operator/sensor ecosystem — capabilities that go beyond what lightweight Workflows offers.
**Why the others are wrong:**
- B) A simple two-call sequence is better served by lightweight Workflows, not the heavier Composer environment.
- C) Composer actually carries more operational overhead (a persistent environment) than Workflows, which is serverless.
- D) Scheduling is a feature of Composer (and Workflows+Scheduler); "not needing scheduling" doesn't justify choosing Composer specifically.

---

**Q47.** A Dataflow pipeline needs to write aggregated results to both BigQuery (for analytics) and Bigtable (for low-latency serving) from the same streaming job. What approach is correct?
A) Branch the PCollection after aggregation and apply two separate I/O sinks (BigQueryIO and BigtableIO)
B) Run two entirely separate pipelines reading from the same Pub/Sub topic with a shared subscription
C) Write only to BigQuery, then use Datastream to copy data into Bigtable
D) This is not possible in a single Dataflow pipeline

**Correct answer: A**
**Why A is correct:** Beam fully supports multiple sinks from a single pipeline — branch the PCollection post-aggregation and write to BigQueryIO and BigtableIO independently within the same job, avoiding duplicated compute and ensuring consistent processing.
**Why the others are wrong:**
- B) Running two pipelines doubles compute and risks a shared subscription causing each to receive only a subset of messages (unless each has its own subscription), adding complexity for no benefit.
- C) Datastream is for database CDC, not a general BigQuery-to-Bigtable transfer mechanism, and adds unnecessary latency/complexity.
- D) Multiple sinks from one pipeline are a standard, well-supported Beam pattern.

---

**Q48.** What is the primary benefit of Cloud Data Fusion's use of CDAP under the hood when it comes to pipeline execution?
A) Pipelines can be compiled to run on Dataproc, abstracting away cluster management from the pipeline designer
B) It eliminates the need for any compute resources entirely
C) It only supports batch, never streaming
D) It replaces the need for BigQuery

**Correct answer: A**
**Why A is correct:** Cloud Data Fusion pipelines execute on ephemeral Dataproc clusters behind the scenes, so users designing pipelines visually don't need to manage the underlying Spark/Hadoop infrastructure directly.
**Why the others are wrong:**
- B) Compute resources (Dataproc clusters) are still used; they're just abstracted away, not eliminated.
- C) Data Fusion supports both batch and (via the Streaming plugin ecosystem) realtime pipelines, so this is too absolute.
- D) Data Fusion is an ETL tool; it doesn't replace BigQuery as a destination/warehouse.

---

**Q49.** Which component in a Dataflow job graph would you inspect in the Google Cloud Console to diagnose why a specific transform step is running slowly?
A) The Dataflow job's execution graph and per-step metrics (e.g., system lag, CPU utilization)
B) Cloud DNS records
C) IAM policy bindings
D) VPC firewall rules

**Correct answer: A**
**Why A is correct:** The Dataflow job monitoring UI shows the execution graph with per-step metrics (throughput, system lag, CPU/memory) — the correct place to diagnose a slow transform.
**Why the others are wrong:**
- B) DNS records relate to name resolution, unrelated to pipeline step performance.
- C) IAM bindings control access permissions, not performance diagnostics.
- D) Firewall rules control network traffic, not pipeline step-level performance.

---

**Q50.** A batch Dataflow job processing a huge GCS dataset keeps running out of memory on certain workers due to large per-key groupings. What's a reasonable mitigation?
A) Use combiner functions (e.g., `Combine.perKey`) instead of materializing all values per key, and consider increasing worker memory/machine type
B) Decrease the number of workers
C) Switch the job to push delivery
D) Add an ordering key

**Correct answer: A**
**Why A is correct:** Combiners aggregate incrementally instead of holding all grouped values in memory at once, reducing memory pressure; pairing this with appropriately sized machine types addresses OOM issues directly.
**Why the others are wrong:**
- B) Fewer workers would concentrate more data per worker, worsening memory pressure.
- C) Push delivery is a Pub/Sub subscription concept, unrelated to Dataflow worker memory.
- D) Ordering keys affect message sequencing in Pub/Sub, not Dataflow memory usage during grouping.

---

**Q51.** You must ingest data from an on-premises Oracle database into GCP continuously, minimizing load on the production database and avoiding custom ETL development.
A) Datastream (log-based CDC)
B) Nightly full-table export scripts
C) Cloud Functions polling the database every minute
D) Manual CSV upload to GCS

**Correct answer: A**
**Why A is correct:** Datastream uses log-based CDC, which reads database transaction logs rather than querying tables directly, minimizing load on the production Oracle instance while providing continuous, low-latency replication — no custom ETL needed.
**Why the others are wrong:**
- B) Full-table nightly exports are batch (not continuous) and can place heavy load on the source DB.
- C) Polling every minute via Cloud Functions adds custom code and recurring query load on the database.
- D) Manual CSV upload is not continuous and is operationally unsustainable.

---

**Q52.** In a Beam pipeline, what's the difference between a fixed window and a sliding window?
A) Fixed windows are non-overlapping fixed-size intervals; sliding windows overlap and can have a period smaller than their size
B) Fixed windows only work in batch; sliding windows only work in streaming
C) They are identical concepts with different names
D) Sliding windows never close

**Correct answer: A**
**Why A is correct:** Fixed windows divide time into equal, non-overlapping buckets (e.g., every 5 minutes), while sliding windows have a size and a period, producing overlapping windows (e.g., 10-minute window every 5 minutes) — useful for rolling aggregations.
**Why the others are wrong:**
- B) Both window types apply to streaming (and conceptually to batch); the batch/streaming distinction isn't tied to window type.
- C) They are distinct concepts with different overlap behavior.
- D) Sliding windows do close/fire based on triggers/watermarks like other window types.

---

**Q53.** Which is the most operationally efficient way to handle a recurring requirement to backfill 90 days of historical data through an existing streaming Dataflow pipeline?
A) Run the same (or a batch-mode variant of the) pipeline in batch mode against historical GCS/archive data
B) Replay all 90 days of Pub/Sub messages through the live streaming pipeline, overloading production
C) Manually recompute results in a spreadsheet
D) It cannot be done; streaming pipelines can't process historical data

**Correct answer: A**
**Why A is correct:** Because Beam unifies batch and streaming semantics, you can typically run the same pipeline logic in batch mode against historical data stored in GCS/archives, efficiently backfilling without disturbing the live streaming path.
**Why the others are wrong:**
- B) Replaying through the live pipeline risks overwhelming production processing and mixing historical/live data awkwardly.
- C) Manual spreadsheet recomputation doesn't scale for 90 days of pipeline-scale data.
- D) Beam's unified model explicitly supports processing historical/bounded data with the same pipeline logic.

---

**Q54.** You're designing ingestion for sensor data that must still be captured and later synced when connectivity is intermittent (e.g., trucks in remote areas). What approach addresses this at the edge?
A) Buffer data locally at the edge and sync via Pub/Sub (or similar) once connectivity resumes
B) Drop data when offline to keep things simple
C) Require constant connectivity before deployment
D) Disable retries on reconnect

**Correct answer: A**
**Why A is correct:** Local buffering at the edge device, syncing once reconnected, is the standard approach for intermittent-connectivity IoT scenarios (e.g., TerramEarth-style vehicles), ensuring no data loss despite connectivity gaps.
**Why the others are wrong:**
- B) Dropping data loses valuable telemetry, unacceptable for most monitoring/analytics use cases.
- C) Requiring constant connectivity isn't realistic for remote/mobile equipment.
- D) Retries on reconnect are needed to ensure buffered data is successfully delivered, not disabled.

---

**Q55.** Why might a team choose Cloud Data Fusion over hand-written Dataflow pipelines for integrating 30 different SaaS and database sources into BigQuery?
A) Data Fusion provides pre-built connectors/plugins for many sources, reducing development time versus custom Beam I/O connectors for each
B) Data Fusion is always faster at runtime than Dataflow
C) Data Fusion doesn't use Dataproc under the hood
D) Dataflow cannot connect to more than 5 sources

**Correct answer: A**
**Why A is correct:** With many heterogeneous sources, Data Fusion's library of pre-built plugins/connectors significantly reduces the engineering effort of writing and maintaining custom connector code for each source compared to hand-rolled Beam pipelines.
**Why the others are wrong:**
- B) Runtime performance isn't guaranteed to be faster; the benefit here is development speed/connector availability, not raw performance.
- C) Data Fusion does use Dataproc under the hood for execution.
- D) Dataflow has no such hard limit on number of sources; custom I/O connectors can be written for many sources, just with more effort.

---

**Q56.** Your streaming pipeline must compute a running count of unique users per hour. Which windowing + aggregation approach is correct?
A) Fixed hourly windows with an approximate or exact distinct-count aggregation (e.g., HyperLogLog++ or `Distinct` + `Count`)
B) No windowing, global aggregation across all time
C) Session windows only
D) Side inputs instead of windowing

**Correct answer: A**
**Why A is correct:** Fixed hourly windows naturally bucket events into the desired per-hour granularity, and a distinct-count aggregation (exact or approximate via HLL++) computes unique users within each window.
**Why the others are wrong:**
- B) Global aggregation across all time would give a single running total, not per-hour unique counts.
- C) Session windows group by gaps in user activity, not fixed hourly boundaries — wrong grouping semantic for this requirement.
- D) Side inputs are for broadcasting auxiliary data, not for time-based aggregation.

---

**Q57.** What GCP-native way exists to monitor whether a Dataflow streaming job is falling behind (processing lag) and alert the on-call team?
A) Cloud Monitoring alerting policies on Dataflow's system lag/data freshness metrics
B) Checking BigQuery billing reports
C) Reading raw Pub/Sub message payloads manually
D) IAM audit logs

**Correct answer: A**
**Why A is correct:** Dataflow exports metrics like system lag and data freshness to Cloud Monitoring, where alerting policies can notify teams automatically when the pipeline falls behind thresholds.
**Why the others are wrong:**
- B) Billing reports show cost, not pipeline processing lag.
- C) Manually reading payloads doesn't scale and isn't a monitoring strategy.
- D) IAM audit logs track access/permission events, not pipeline performance metrics.

---

**Q58.** A legacy on-prem pipeline used HDFS to store intermediate Spark job output. When moving to Dataproc on GCP, what is the recommended replacement?
A) Cloud Storage (via the GCS connector), allowing ephemeral clusters and decoupled storage/compute
B) Keep using local HDFS on persistent disks indefinitely
C) Store intermediate data in Firestore
D) Store intermediate data in Pub/Sub

**Correct answer: A**
**Why A is correct:** Using GCS instead of HDFS decouples storage from compute, enabling ephemeral Dataproc clusters (data persists in GCS even after the cluster is deleted) — the recommended cloud-native pattern.
**Why the others are wrong:**
- B) Persistent local HDFS reintroduces the tight storage/compute coupling that prevents ephemeral, cost-saving cluster patterns.
- C) Firestore is a document database, not suited for large intermediate Spark data files.
- D) Pub/Sub is a messaging system, not a file storage system for Spark intermediate output.

---

**Q59.** Which statement correctly differentiates Pub/Sub's "at-least-once" delivery guarantee from "exactly-once" processing in a downstream system?
A) Pub/Sub may redeliver a message more than once; the downstream system must handle deduplication/idempotency to achieve effectively-once results
B) Pub/Sub guarantees exactly-once delivery natively with no extra work
C) At-least-once means messages are sometimes lost
D) Exactly-once and at-least-once mean the same thing

**Correct answer: A**
**Why A is correct:** At-least-once means every message is delivered one or more times (never zero), so duplicates are possible; achieving exactly-once *processing* requires the consumer (e.g., Dataflow with dedup logic, or idempotent writes) to handle potential duplicates.
**Why the others are wrong:**
- B) Pub/Sub's core guarantee is at-least-once, not exactly-once, without additional application-level handling.
- C) At-least-once explicitly means no message loss — the opposite of what's being described.
- D) They are distinct guarantees; conflating them is incorrect.

---

**Q60.** For a pipeline where cost predictability matters more than peak elasticity, and the Dataproc workload runs on a steady, predictable schedule every day, what pricing/commitment approach reduces cost?
A) Committed use discounts for the underlying Compute Engine resources
B) On-demand pricing exclusively
C) Pub/Sub Lite reservations
D) BigQuery flat-rate slots

**Correct answer: A**
**Why A is correct:** Committed use discounts apply to steady, predictable Compute Engine usage (which underlies Dataproc clusters), reducing cost versus pure on-demand pricing for workloads that run reliably every day.
**Why the others are wrong:**
- B) On-demand pricing is the baseline/default, not a discount strategy, and costs more for predictable steady usage.
- C) Pub/Sub Lite reservations concern messaging throughput capacity, not Dataproc compute cost.
- D) BigQuery flat-rate slots are a BigQuery-specific pricing model, unrelated to Dataproc compute costs.

---

**Q61.** A retailer wants to trigger a Cloud Function immediately whenever a new file lands in a specific Cloud Storage bucket, to kick off a small transformation. What is the simplest trigger mechanism?
A) Cloud Storage event notifications (via Eventarc/Pub/Sub) triggering a Cloud Function
B) A Dataproc cluster polling the bucket every second
C) A Cloud Composer DAG scheduled every second
D) Manual uploads followed by manual function invocation

**Correct answer: A**
**Why A is correct:** Cloud Storage can emit object-change events (through Eventarc, which uses Pub/Sub under the hood) that directly and immediately trigger a Cloud Function — the simplest, native event-driven mechanism for this use case.
**Why the others are wrong:**
- B) Polling every second via a Dataproc cluster is wasteful, slow to set up, and not event-driven.
- C) A DAG scheduled every second is an anti-pattern for Composer and introduces unnecessary latency/overhead compared to native event triggers.
- D) Manual invocation doesn't scale and defeats the purpose of automation.

---

**Q62.** You are designing a pipeline where occasional bursts can be 50x the average load. Which Dataflow feature specifically helps absorb these bursts without manual capacity planning?
A) Horizontal autoscaling (and Streaming Engine for streaming jobs)
B) Fixed worker count set to 50x average
C) Disabling the Dataflow service during bursts
D) Running on a single VM

**Correct answer: A**
**Why A is correct:** Dataflow's autoscaling dynamically adjusts worker count based on real-time backlog/load, efficiently absorbing bursts without requiring you to over-provision for worst-case scenarios in advance.
**Why the others are wrong:**
- B) Fixing workers at 50x average wastes money the vast majority of the time when load is normal.
- C) Disabling the service during bursts would drop/delay exactly the data you need to process.
- D) A single VM cannot handle large-scale parallel processing or bursts at all.

---

**Q63.** A Beam pipeline must join a large unbounded stream with another large unbounded stream (not just a small side input). What is the appropriate approach?
A) CoGroupByKey (or a windowed join) on both streams, using consistent windowing/keys
B) Load one entire stream as a side input
C) This is not possible in Beam
D) Only Dataproc supports stream-stream joins

**Correct answer: A**
**Why A is correct:** Beam supports stream-stream joins using `CoGroupByKey` (or Join libraries) combined with consistent windowing on both sides, to match corresponding elements from two unbounded PCollections within a time frame.
**Why the others are wrong:**
- B) Side inputs are intended for smaller, more static datasets — not appropriate when both sides are large unbounded streams.
- C) Beam explicitly supports this pattern via windowed joins; the claim is incorrect.
- D) Beam (and thus Dataflow) supports this directly; it is not Dataproc-exclusive.

---

**Q64.** Which best describes when to use "Flex Templates" over "Classic Templates" in Dataflow?
A) Flex Templates package the pipeline as a Docker container, supporting more flexible runtime parameterization (including dynamic execution graphs) than Classic Templates
B) Flex Templates are only for batch jobs
C) Classic Templates support Docker containers; Flex Templates do not
D) There is no difference between them

**Correct answer: A**
**Why A is correct:** Flex Templates containerize the pipeline (via Docker) and allow more dynamic construction of the pipeline graph at runtime based on parameters, offering more flexibility than the more static Classic Templates.
**Why the others are wrong:**
- B) Flex Templates support both batch and streaming, not just batch.
- C) It's the reverse — Flex Templates use Docker containers, not Classic Templates.
- D) There is a meaningful difference in flexibility and packaging, as described.

---

**Q65.** What's a key operational risk of using a single long-lived Dataproc cluster shared across many different teams' unrelated jobs?
A) Resource contention and noisy-neighbor effects between unrelated workloads, plus harder cost attribution
B) It guarantees better performance for all jobs
C) It eliminates the need for IAM
D) It automatically isolates each team's data

**Correct answer: A**
**Why A is correct:** Shared long-lived clusters can suffer resource contention (one team's heavy job slows another's), and it becomes harder to attribute cost/usage per team — a common reason to prefer ephemeral, per-job or per-team clusters.
**Why the others are wrong:**
- B) Shared contention typically degrades performance for some jobs, not guarantees improvement.
- C) IAM is still fully required for access control regardless of cluster-sharing model.
- D) Data isolation is not automatic; it must be explicitly configured (e.g., via IAM, separate storage locations).

---

**Q66.** For a pipeline needing to process both real-time events and periodic large historical reprocessing jobs with the same transformation logic, what Beam/Dataflow property is most valuable?
A) The same pipeline code can run in both streaming and batch execution modes
B) You must maintain two entirely separate codebases
C) Only Dataproc can do batch; Dataflow can't
D) Historical reprocessing requires a different cloud provider

**Correct answer: A**
**Why A is correct:** Beam's unified model allows writing the transformation logic once and running it against either an unbounded (streaming) or bounded (batch/historical) source, reducing duplicated engineering effort.
**Why the others are wrong:**
- B) Maintaining two codebases is exactly what Beam's unified model avoids — this contradicts the core value proposition.
- C) Dataflow fully supports batch mode; the claim is false.
- D) There's no reason historical reprocessing requires switching cloud providers.

---

**Q67.** A compliance requirement states that message data must not leave a specific region. Which Pub/Sub feature or configuration supports this requirement?
A) Message storage policies restricting Pub/Sub message storage to specific regions
B) Ordering keys
C) Dead-letter topics
D) Push subscriptions

**Correct answer: A**
**Why A is correct:** Pub/Sub message storage policies let you restrict where message data is persisted (allowed/denied regions), directly supporting data residency/compliance requirements.
**Why the others are wrong:**
- B) Ordering keys control delivery order, unrelated to data residency.
- C) Dead-letter topics handle failed message routing, not geographic storage restriction.
- D) Push subscriptions define delivery mechanism, not storage location policy.

---

**Q68.** Your Dataflow job needs to write results to a destination that doesn't have a built-in Beam I/O connector. What is the recommended approach?
A) Implement a custom `DoFn`/sink using the target system's client library within the pipeline
B) It's impossible to write to systems without a built-in connector
C) Switch entirely to Dataproc, which supports all destinations natively
D) Use Cloud Scheduler to write the data instead

**Correct answer: A**
**Why A is correct:** Beam is extensible — you can write a custom `DoFn` that uses the destination's client library/API to perform writes, effectively creating a custom sink when no built-in I/O connector exists.
**Why the others are wrong:**
- B) Beam's extensibility makes this entirely possible via custom code.
- C) Dataproc doesn't inherently support "all destinations natively" either; it has the same kind of extensibility need via custom code.
- D) Cloud Scheduler triggers jobs on a schedule; it doesn't perform data writes itself.

---

**Q69.** What's the main advantage of decoupling ingestion (Pub/Sub) from processing (Dataflow) rather than having producers write directly to BigQuery?
A) It buffers traffic spikes, enables multiple independent consumers, and improves resilience if downstream processing is temporarily unavailable
B) It reduces the total number of GCP services used
C) BigQuery cannot accept direct writes at all
D) It removes the need for any schema definition

**Correct answer: A**
**Why A is correct:** Pub/Sub acts as a buffer and decoupling layer — if BigQuery or Dataflow processing is briefly unavailable or slow, messages queue safely in Pub/Sub; it also allows multiple independent subscribers to consume the same data for different purposes.
**Why the others are wrong:**
- B) Reducing service count isn't a stated goal nor an inherent benefit; architecture should match requirements, not minimize service count artificially.
- C) BigQuery does accept direct streaming inserts/loads; the claim is factually wrong.
- D) Schema definition is still needed for BigQuery tables and ideally for Pub/Sub messages; decoupling doesn't eliminate this need.

---

**Q70.** A nightly Dataproc job reads 10 TB from GCS, transforms it, and writes 2 TB back to GCS. Which practice reduces both runtime and cost?
A) Right-sizing cluster machine types/node count via autoscaling policies and using preemptible workers for the bulk of the processing
B) Always using the largest available machine type regardless of job size
C) Running the job on a single-node cluster to simplify billing
D) Disabling autoscaling to keep configuration static

**Correct answer: A**
**Why A is correct:** Autoscaling + appropriately sized machine types ensure compute matches actual workload demand, and preemptible workers cut cost for fault-tolerant batch processing — directly reducing both runtime (via adequate parallelism) and cost (via cheaper, right-sized resources).
**Why the others are wrong:**
- B) Always using the largest machine type overprovisions and wastes money regardless of actual job needs.
- C) Single-node clusters bottleneck parallel processing, increasing runtime for a 10 TB job.
- D) Disabling autoscaling removes the ability to adapt to actual load, risking either under- or over-provisioning.

---

**Q71.** Which GCP service is purpose-built to let you preview, clean, and prepare data visually before loading it into a warehouse, often used by data analysts (not engineers)?
A) Cloud Data Fusion (Wrangler feature)
B) Cloud Composer
C) Dataproc Spark shell
D) Cloud KMS

**Correct answer: A**
**Why A is correct:** Cloud Data Fusion includes a "Wrangler" interface for interactively previewing and cleaning data (data preparation), targeted at analysts without deep coding skills.
**Why the others are wrong:**
- B) Composer orchestrates workflows; it has no visual data-preview/cleaning UI.
- C) The Spark shell requires coding knowledge, contrary to the analyst-friendly requirement.
- D) Cloud KMS manages encryption keys, unrelated to data preparation.

---

**Q72.** You need to ensure a Dataflow streaming pipeline survives a zonal outage without manual intervention. What should you verify/configure?
A) Dataflow jobs run regionally by default and can withstand zonal failures by automatically redistributing work to available zones
B) Manually migrate the job to another zone after the outage is noticed
C) Pin the job to a single zone for simplicity
D) Disable autoscaling to avoid cross-zone movement

**Correct answer: A**
**Why A is correct:** Dataflow is a regional service — it runs across zones within a region, so a single zonal outage doesn't require manual failover; Dataflow automatically works around unavailable zones using available capacity in the region.
**Why the others are wrong:**
- B) Manual migration introduces downtime and operational burden that regional execution already avoids.
- C) Pinning to a single zone removes the resilience benefit entirely, risking an outage.
- D) Autoscaling is unrelated to zonal resilience and shouldn't be disabled for this reason.

---

**Q73.** For an ingestion pipeline needing a guarantee that produced data in Pub/Sub is encrypted both at rest and in transit by default, what do you need to configure?
A) Nothing extra — Pub/Sub encrypts data at rest and in transit by default
B) You must manually enable TLS
C) You must bring your own encryption library
D) Encryption is only available with Pub/Sub Lite

**Correct answer: A**
**Why A is correct:** Google encrypts Pub/Sub data at rest and in transit by default with no extra configuration required (Google-managed keys); CMEK can be added if customer-managed keys are specifically required.
**Why the others are wrong:**
- B) TLS in transit is already enabled by default for Google APIs; you don't need to manually enable it.
- C) No custom encryption library is required for baseline encryption.
- D) Both Pub/Sub and Pub/Sub Lite provide default encryption; it's not Lite-exclusive.

---

**Q74.** A team wants to validate a new Dataflow pipeline version against production traffic without impacting the existing production pipeline or risking data duplication. What approach is reasonable?
A) Run the new pipeline version against a separate test subscription/topic (or a copy of sampled production data) in a staging environment before cutting over
B) Deploy directly to production and monitor for issues after the fact
C) Modify the existing production pipeline code in place without testing
D) Skip testing since Dataflow jobs can't be versioned

**Correct answer: A**
**Why A is correct:** Testing against a separate subscription/topic or sampled data in a staging environment validates the new version safely, avoiding risk to production data and enabling a controlled cutover.
**Why the others are wrong:**
- B) Deploying untested changes directly to production risks data issues and outages — poor practice.
- C) Modifying production code in place without testing is risky and hard to roll back safely.
- D) Dataflow jobs/pipelines absolutely can be versioned and tested in parallel environments.

---

**Q75.** Which combination of services would best support ingesting files dropped by partners via SFTP into a GCP pipeline, given partners cannot change their delivery mechanism?
A) Stand up a GCS-backed SFTP gateway (e.g., via a managed/partner solution or a small VM-based SFTP server) that lands files in Cloud Storage, triggering downstream processing
B) Require all partners to migrate to Pub/Sub publishing
C) Ask partners to call BigQuery's streaming insert API
D) Manually email files to the data team daily

**Correct answer: A**
**Why A is correct:** Since partners can't change their SFTP-based delivery, a gateway that accepts SFTP and lands data into GCS (triggering event-based downstream processing) meets them where they are while still integrating into the GCP pipeline.
**Why the others are wrong:**
- B) The scenario explicitly states partners cannot change their delivery mechanism, ruling out requiring a Pub/Sub integration from them.
- C) Same issue — this requires partner-side changes that are explicitly disallowed.
- D) Manual email handling doesn't scale and isn't an automated pipeline solution.

---

**Q76.** In a Beam pipeline, what's the purpose of a `Combine.globally` or `Combine.perKey` transform compared to `GroupByKey` followed by manual aggregation?
A) Combiners can partially aggregate data before a full shuffle, improving performance over naive group-then-aggregate approaches
B) They are functionally identical with no performance difference
C) Combiners only work in batch mode
D) Combiners replace the need for windowing

**Correct answer: A**
**Why A is correct:** Combiner functions can apply associative/commutative partial aggregation (e.g., local combining before shuffle), reducing data movement and improving performance compared to grouping all raw values before aggregating manually.
**Why the others are wrong:**
- B) There is a meaningful performance distinction; combiners are specifically an optimization over raw group-then-aggregate.
- C) Combiners work in both batch and streaming pipelines.
- D) Combiners handle aggregation; windowing handles time-based grouping — they address different concerns and both may be used together.

---

**Q77.** Which is the most appropriate way to grant a Dataflow job's worker service account only the permissions it needs to read from a specific Pub/Sub subscription and write to a specific BigQuery dataset?
A) Assign a custom or predefined IAM role scoped to just those resources on the service account used by the Dataflow workers
B) Grant the Owner role on the project to the service account
C) Use the default Compute Engine service account with Editor role
D) Share your own user credentials with the pipeline

**Correct answer: A**
**Why A is correct:** Following least privilege, you should grant narrowly scoped roles (e.g., Pub/Sub Subscriber on the specific subscription, BigQuery Data Editor on the specific dataset) to the dedicated service account used by the pipeline.
**Why the others are wrong:**
- B) Owner role grants far more access than needed, violating least privilege and increasing security risk.
- C) The default Compute Engine service account with Editor is overly broad and a known anti-pattern for production workloads.
- D) Sharing personal user credentials with an automated pipeline is a security anti-pattern (no accountability, broader access than needed, credential management risk).

---

**Q78.** What differentiates a Pub/Sub "subscription" from a "topic"?
A) A topic is the named resource producers publish to; a subscription represents a specific stream of messages from that topic for a consumer to pull/receive
B) They are interchangeable terms for the same resource
C) A subscription is where producers publish; a topic is where consumers read
D) Topics are only used in Pub/Sub Lite

**Correct answer: A**
**Why A is correct:** Producers publish messages to a topic; one or more subscriptions attached to that topic each deliver an independent copy of the message stream to their respective consumers.
**Why the others are wrong:**
- B) They are distinct resources with different roles in the pub/sub model.
- C) This reverses the actual roles — producers publish to topics, consumers read via subscriptions.
- D) Both standard Pub/Sub and Pub/Sub Lite use topics; it is not Lite-exclusive terminology.

---

**Q79.** You need a pipeline component that waits for an external file to land in GCS before triggering the next task in a Composer DAG. What should you use?
A) A GCS object sensor (e.g., `GCSObjectExistenceSensor`) in the Airflow DAG
B) A Dataflow side input
C) A Pub/Sub ordering key
D) A BigQuery materialized view

**Correct answer: A**
**Why A is correct:** Airflow (Composer) sensors like the GCS object existence sensor poll/wait for a condition (a file landing) before allowing downstream DAG tasks to proceed — exactly this use case.
**Why the others are wrong:**
- B) Side inputs are a Beam/Dataflow concept for broadcasting data within a pipeline, not a workflow-level wait condition.
- C) Ordering keys control Pub/Sub message order, unrelated to DAG task triggering.
- D) Materialized views are a BigQuery query performance feature, not a workflow dependency mechanism.

---

**Q80.** Why is it generally recommended to avoid extremely small, frequent BigQuery load jobs (e.g., one load job per second) in favor of batching or streaming inserts?
A) BigQuery load jobs have daily quotas and per-job overhead; excessive small jobs can hit quota limits and are less efficient than batching or using streaming inserts for near-real-time needs
B) Load jobs are always more expensive than streaming inserts regardless of frequency
C) BigQuery doesn't support load jobs at all
D) Load jobs automatically deduplicate data so frequency doesn't matter

**Correct answer: A**
**Why A is correct:** BigQuery enforces load job quotas (e.g., per table/per project per day), and many tiny load jobs add overhead without benefit; for near-real-time needs, streaming inserts are more appropriate, while batching reduces job count for less time-sensitive data.
**Why the others are wrong:**
- B) Streaming inserts typically cost more per row than batch loads (which are often free); the cost relationship is the opposite of what's stated.
- C) BigQuery clearly supports load jobs; this is a core ingestion method.
- D) Load jobs don't inherently deduplicate; dedup requires explicit design (e.g., MERGE statements or unique keys).

---

**Q81.** A company needs to ingest clickstream events, apply light transformation, and store both a raw copy (for reprocessing/audit) and a cleaned copy (for analytics). What pattern supports this with Dataflow?
A) Branch the pipeline after ingestion: write raw events to GCS (or a raw BigQuery table) and write transformed events to a cleaned BigQuery table, all within one job
B) Only store the cleaned data; raw data isn't needed
C) Use two completely separate Pub/Sub topics manually populated by hand
D) Store everything only in Memorystore

**Correct answer: A**
**Why A is correct:** Branching the pipeline after ingestion into a "raw" sink and a "transformed" sink is a standard pattern, preserving an audit trail/raw copy for reprocessing while also producing a clean analytics-ready copy — all in a single coherent pipeline.
**Why the others are wrong:**
- B) Discarding raw data removes the ability to reprocess or audit, which the requirement explicitly needs.
- C) Manually populating topics by hand isn't an automated pipeline pattern and doesn't scale.
- D) Memorystore is an in-memory cache, not suited for durable raw/audit storage.

---

**Q82.** What's the main reason to prefer BigQuery as a sink over Bigtable for ad-hoc SQL analytics on aggregated streaming results, even though both can technically store the data?
A) BigQuery provides native SQL query capability and is optimized for analytical scans/joins, while Bigtable has no SQL interface and is optimized for key-based point lookups
B) Bigtable is always more expensive
C) BigQuery cannot handle streaming data at all
D) Bigtable automatically provides dashboards

**Correct answer: A**
**Why A is correct:** BigQuery is purpose-built for SQL-based analytical queries (joins, aggregations, ad-hoc exploration), whereas Bigtable is optimized for extremely fast key-based lookups and lacks a native SQL query engine — making BigQuery the better fit for ad-hoc analytics.
**Why the others are wrong:**
- B) Relative cost depends on workload/scale; this isn't the deciding factor for the stated analytics requirement.
- C) BigQuery explicitly supports streaming inserts for near-real-time data availability.
- D) Neither service provides dashboards itself; that's a separate BI tool's role (Looker/Looker Studio).

---

**Q83.** Your organization needs an audit trail showing every Pub/Sub publish/consume action for compliance. Where would you look to configure/view this?
A) Cloud Audit Logs (Admin Activity and Data Access logs) integrated with Cloud Logging
B) BigQuery INFORMATION_SCHEMA only
C) VPC Flow Logs
D) Dataproc job history only

**Correct answer: A**
**Why A is correct:** Cloud Audit Logs capture administrative and (if enabled) data access activity across GCP services including Pub/Sub, viewable/exportable via Cloud Logging — the correct mechanism for compliance audit trails.
**Why the others are wrong:**
- B) INFORMATION_SCHEMA in BigQuery reflects BigQuery metadata/jobs, not Pub/Sub activity.
- C) VPC Flow Logs capture network traffic metadata, not application-level publish/consume events.
- D) Dataproc job history reflects Spark/Hadoop job runs, unrelated to Pub/Sub auditing.

---

**Q84.** Why would a team choose to run transformation logic in SQL within BigQuery (ELT) rather than building a separate Dataflow transformation pipeline (ETL) for a given dataset already loaded into BigQuery?
A) When transformations can be expressed well in SQL and data is already in BigQuery, ELT avoids extra pipeline infrastructure and leverages BigQuery's scalable query engine directly
B) SQL cannot express complex transformations
C) Dataflow is always required before any BigQuery usage
D) ELT is impossible in BigQuery

**Correct answer: A**
**Why A is correct:** When data already resides in BigQuery and the required transformations are SQL-expressible, performing transformations in-place (ELT, e.g., via scheduled queries or dbt) avoids the operational overhead of a separate Dataflow pipeline, leveraging BigQuery's own compute.
**Why the others are wrong:**
- B) SQL (especially with BigQuery's extensions, UDFs, and procedural scripting) can express a wide range of complex transformations.
- C) Many architectures load data directly into BigQuery without always requiring Dataflow first.
- D) ELT within BigQuery (load then transform via SQL) is a common, well-supported pattern.

---

**Q85.** When should you use a Pub/Sub "push" subscription rather than "pull"?
A) When you want Pub/Sub to actively deliver messages to a specific, always-available HTTPS endpoint (e.g., a Cloud Run service) rather than having the consumer poll
B) When you need exactly-once ordering guarantees automatically
C) When your consumer is offline most of the time
D) Push and pull are functionally identical in all respects

**Correct answer: A**
**Why A is correct:** Push subscriptions actively POST messages to a specified HTTPS endpoint, suiting scenarios where you have a reliable, always-on receiving service (e.g., Cloud Run/App Engine) rather than needing the consumer to poll via pull.
**Why the others are wrong:**
- B) Ordering guarantees come from ordering keys, independent of push vs. pull delivery mode.
- C) Push requires the endpoint to be available to receive messages; an often-offline consumer is better served by pull (fetching when ready).
- D) Push and pull differ meaningfully in delivery mechanism and consumer responsibilities.

---

**Q86.** A pipeline reading from Cloud SQL via Dataflow's JDBC connector is causing high load on the production OLTP database during business hours. What's a better-practice alternative for heavy analytical extraction?
A) Use Datastream CDC to replicate changes continuously into BigQuery/GCS, then run analytics there instead of querying production OLTP directly
B) Increase the number of concurrent JDBC connections against production
C) Run the extraction job more frequently throughout the day
D) Disable indexes on the production database to speed up reads

**Correct answer: A**
**Why A is correct:** CDC-based replication (Datastream) offloads continuous change capture from the production database's transaction logs with minimal query load, letting heavy analytics run against the replicated copy in BigQuery/GCS instead of hammering the OLTP system directly.
**Why the others are wrong:**
- B) More concurrent JDBC connections would increase, not reduce, load on the production database.
- C) Running extraction more frequently increases load frequency, worsening the problem.
- D) Disabling indexes would likely degrade application performance and is unrelated to reducing extraction load.

---

**Q87.** What's an appropriate use of Cloud Functions (or Cloud Run) in an ingestion pipeline alongside Pub/Sub?
A) Lightweight, event-driven processing triggered by a Pub/Sub message for simple transformations or routing, without managing servers
B) Running sustained, stateful, high-throughput streaming aggregation across hours of data
C) Replacing BigQuery as the analytical data warehouse
D) Acting as the long-term durable message store

**Correct answer: A**
**Why A is correct:** Cloud Functions/Cloud Run are well-suited for lightweight, short-lived, event-driven processing (e.g., triggered by a single Pub/Sub message) without infrastructure management — ideal for simple transformations, routing, or fan-out actions.
**Why the others are wrong:**
- B) Sustained, stateful, high-throughput streaming aggregation is better handled by Dataflow, which is designed for exactly this.
- C) Cloud Functions don't provide warehouse/analytics query capability like BigQuery.
- D) Pub/Sub itself is the durable message store, not Cloud Functions, which are stateless compute.

---

**Q88.** Which approach best supports reprocessing historical data with an updated transformation schema while keeping the original raw data unchanged for future reprocessing needs?
A) Keep raw/immutable data in GCS (or a raw BigQuery table) as the source of truth, and generate new transformed outputs/tables from it as logic changes
B) Overwrite the raw data in place with each new transformation version
C) Delete historical raw data once it's been processed once
D) Store only the final transformed output, discarding all raw inputs

**Correct answer: A**
**Why A is correct:** Treating raw data as immutable and reprocessing from it into new/versioned transformed outputs allows you to fix bugs or evolve transformation logic later without losing the ability to regenerate historical results — a key data engineering best practice.
**Why the others are wrong:**
- B) Overwriting raw data in place destroys the ability to reprocess from the true original source.
- C) Deleting raw data after one use removes future reprocessing capability entirely.
- D) Keeping only transformed output loses the raw source needed to correct or evolve transformations later.

---

**Q89.** You need your Dataflow streaming pipeline to automatically restart and resume processing (without data loss or duplication) after a worker crash. What Dataflow/Beam characteristic provides this?
A) Dataflow's built-in checkpointing and exactly-once processing guarantees within the pipeline runner
B) You must manually implement your own checkpointing from scratch
C) Crashes always require a full pipeline redeploy and data replay from the very beginning
D) This is only possible with Dataproc, not Dataflow

**Correct answer: A**
**Why A is correct:** Dataflow's runner manages internal checkpointing and state persistence, providing exactly-once processing guarantees and automatic recovery from individual worker failures without manual intervention or duplicate processing.
**Why the others are wrong:**
- B) This is a built-in Dataflow runner capability; you don't need to implement checkpointing yourself.
- C) A full data replay from the beginning isn't required for a single worker crash — the runner recovers more gracefully.
- D) This is a core Dataflow/Beam runner feature, not unique to or exclusive to Dataproc.

---

**Q90.** What advantage does using Avro or Protobuf (vs. plain JSON) for Pub/Sub message schemas typically provide?
A) More compact binary encoding and stronger schema enforcement/evolution support compared to loosely-typed JSON
B) JSON cannot be used with Pub/Sub at all
C) Avro/Protobuf eliminate the need for any consumer-side error handling
D) Avro/Protobuf are only supported by Dataproc, not Pub/Sub

**Correct answer: A**
**Why A is correct:** Avro and Protobuf provide compact binary serialization and formal schema definitions with built-in evolution rules, offering stronger type safety and smaller message sizes compared to loosely structured JSON.
**Why the others are wrong:**
- B) JSON is also a supported Pub/Sub schema type; the claim that it "cannot be used" is false.
- C) Schema enforcement reduces certain classes of errors but doesn't eliminate the need for general consumer-side error handling (e.g., business logic failures).
- D) Pub/Sub natively supports Avro and Protobuf schemas; this isn't Dataproc-specific.

---

**Q91.** A pipeline ingesting log data needs to drop personally identifiable information (PII) like email addresses before the data reaches BigQuery. Where is the most appropriate place to apply this?
A) Within the Dataflow pipeline (or via Cloud DLP integration) before writing to the BigQuery sink
B) After the data is already in BigQuery and widely queryable
C) Never — PII removal isn't technically possible in pipelines
D) Only at the BigQuery dataset's IAM level

**Correct answer: A**
**Why A is correct:** Removing/redacting PII as early as possible in the pipeline (e.g., using Cloud DLP transforms within Dataflow) before it lands in BigQuery minimizes exposure and avoids ever persisting sensitive raw PII in the warehouse.
**Why the others are wrong:**
- B) Removing PII only after it's already in BigQuery means it was exposed/queryable in the interim — a weaker security posture.
- C) PII redaction/tokenization is a well-supported pattern (e.g., via Cloud DLP), so the premise is false.
- D) IAM controls access to the dataset but does not remove or redact PII values within the data itself.

---

**Q92.** Which statement correctly contrasts Dataproc's autoscaling with Dataflow's autoscaling?
A) Dataproc autoscaling adjusts YARN-based cluster worker nodes; Dataflow autoscaling adjusts Beam pipeline worker VMs based on pipeline-specific metrics like backlog
B) They are the exact same underlying mechanism shared between both services
C) Only Dataflow supports any form of autoscaling
D) Only Dataproc supports any form of autoscaling

**Correct answer: A**
**Why A is correct:** Each service has its own autoscaling mechanism tailored to its execution model — Dataproc scales cluster nodes based on YARN pending memory/containers, while Dataflow scales pipeline workers based on throughput/backlog signals specific to the Beam runner.
**Why the others are wrong:**
- B) They are distinct, service-specific autoscaling implementations, not a shared mechanism.
- C) Dataproc also supports autoscaling policies; this statement is false.
- D) Dataflow also supports autoscaling; this statement is false.

---

**Q93.** A requirement states that ingestion must support "exactly-once delivery" semantics natively without any custom deduplication code. Which statement is most accurate regarding Pub/Sub?
A) Pub/Sub supports an exactly-once delivery feature for subscriptions, reducing (though applications should still design for possible edge cases) the need for custom dedup in many scenarios
B) Pub/Sub has never supported anything beyond at-least-once in any form
C) Exactly-once delivery is only available through third-party plugins
D) Exactly-once delivery requires switching entirely to Kafka

**Correct answer: A**
<br>
**Why A is correct:** Pub/Sub offers an exactly-once delivery feature at the subscription level (in addition to its baseline at-least-once guarantee), which significantly reduces duplicate delivery scenarios compared to standard at-least-once subscriptions.
**Why the others are wrong:**
- B) This ignores Pub/Sub's exactly-once delivery subscription feature, which does exist.
- C) It's a native Pub/Sub capability, not a third-party plugin requirement.
- D) Switching to self-managed Kafka is unnecessary and contradicts the goal of using managed GCP services.

---

**Q94.** Why is it important to set an appropriate acknowledgment deadline on a Pub/Sub subscription when consumer processing can occasionally take longer than expected?
A) If processing exceeds the ack deadline, Pub/Sub will redeliver the message, potentially causing duplicate processing unless handled properly (idempotency) or the deadline is extended
B) The ack deadline only affects billing, not message delivery
C) Ack deadlines are irrelevant to push subscriptions
D) Exceeding the ack deadline permanently deletes the message

**Correct answer: A**
**Why A is correct:** If a consumer doesn't acknowledge within the deadline, Pub/Sub assumes delivery failed and redelivers the message — understanding and properly configuring (or extending) this deadline is key to avoiding unnecessary duplicate processing.
**Why the others are wrong:**
- B) The ack deadline directly affects redelivery behavior, not just billing.
- C) Ack deadlines apply to both push and pull subscriptions.
- D) Exceeding the deadline triggers redelivery, not permanent deletion (messages are retained per the retention policy).

---

**Q95.** For a data pipeline requiring strict ordering guarantees across an entire topic (not just per key), which statement is true about Pub/Sub?
A) Pub/Sub ordering keys guarantee order only within each distinct key, not globally across the entire topic
B) Pub/Sub always guarantees strict global ordering across all messages by default
C) Ordering is guaranteed automatically with any subscription type with no configuration
D) Global ordering is a BigQuery feature, not a Pub/Sub concept

**Correct answer: A**
**Why A is correct:** Pub/Sub ordering is scoped to a given ordering key — messages sharing the same key arrive in order, but there's no built-in global-topic-wide ordering guarantee across different keys.
**Why the others are wrong:**
- B) Pub/Sub does not guarantee global ordering by default; ordering must be explicitly enabled per key.
- C) Ordering requires explicitly setting ordering keys and enabling message ordering on the subscription; it's not automatic.
- D) Ordering is a Pub/Sub concept concerning message delivery sequence, unrelated to BigQuery.

---

**Q96.** You need to process files as soon as they arrive in a bucket, but also occasionally need to reprocess the entire historical set of files on demand. Which architecture supports both needs cleanly?
A) Use GCS event notifications for real-time triggering of a Dataflow/Cloud Function pipeline, and separately support a batch mode (same or similar pipeline) that can be manually invoked against the full bucket contents
B) Only support real-time triggering; batch reprocessing isn't feasible with GCS
C) Only support manual batch reprocessing; discard the real-time requirement
D) Require all historical files to be re-uploaded to trigger notifications again

**Correct answer: A**
**Why A is correct:** Combining event-driven triggers (for new files) with an on-demand batch mode (reading the full bucket) covers both requirements without forcing an awkward workaround, leveraging the same or similar processing logic for consistency.
**Why the others are wrong:**
- B) Batch reprocessing of existing GCS objects is entirely feasible (e.g., listing objects and processing them in batch); this option incorrectly rules it out.
- C) This ignores the explicit real-time requirement stated in the scenario.
- D) Re-uploading files just to trigger notifications is wasteful and operationally poor compared to a dedicated batch reprocessing path.

---

**Q97.** What's the risk of setting a Pub/Sub subscription's message retention duration too short for a system that sometimes needs to replay/reprocess recent data after a bug fix?
A) Messages older than the retention duration become permanently unavailable for replay via `seek`, limiting how far back you can reprocess
B) There is no risk; retention duration only affects billing
C) Short retention automatically triggers data archival to BigQuery
D) Retention duration has no effect on the `seek` feature

**Correct answer: A**
**Why A is correct:** Pub/Sub's `seek`-based replay can only go back as far as the configured retention duration allows; if retention is too short, messages needed for reprocessing older issues may already be purged and unavailable.
**Why the others are wrong:**
- B) Retention duration directly affects data availability for replay, not just cost.
- C) Pub/Sub doesn't automatically archive to BigQuery based on retention settings; that would require explicit pipeline design.
- D) Retention duration directly determines the time window `seek` can replay within.

---

**Q98.** Why might you choose to have Dataflow write directly to a BigQuery table using the Storage Write API rather than legacy streaming inserts?
A) The Storage Write API offers higher throughput, lower cost, and exactly-once semantics compared to legacy streaming inserts
B) The Storage Write API is slower but cheaper in all cases
C) Legacy streaming inserts guarantee exactly-once semantics while the Storage Write API does not
D) There is no meaningful difference between the two APIs

**Correct answer: A**
**Why A is correct:** BigQuery's Storage Write API is the modern high-throughput ingestion path, offering better performance, lower cost at scale, and native exactly-once write semantics compared to the older streaming insert (tabledata.insertAll) API.
**Why the others are wrong:**
- B) It's generally faster and more cost-efficient at scale, not slower.
- C) This reverses the actual advantage — the Storage Write API, not legacy streaming inserts, provides exactly-once semantics.
- D) There are meaningful differences in throughput, cost, and consistency guarantees between the two.

---

**Q99.** A pipeline must ingest data that arrives in wildly inconsistent formats (CSV, JSON, XML) from various legacy partner systems, and the formats change occasionally without notice. Which approach minimizes pipeline breakage?
A) Build format-detection and per-format parsing logic with strong validation and dead-lettering of unparseable records, alerting on format-detection failures
B) Assume all data will always be CSV and hardcode a CSV parser only
C) Reject all data that isn't in the originally expected format permanently
D) Manually inspect every file before processing

**Correct answer: A**
**Why A is correct:** Building resilient format detection/parsing with validation and dead-lettering for unparseable records (plus alerting) allows the pipeline to handle format drift gracefully, surfacing issues without crashing or silently losing data.
**Why the others are wrong:**
- B) Hardcoding a single format ignores the stated multi-format reality and will break immediately on JSON/XML input.
- C) Permanently rejecting non-conforming data loses potentially valid data and doesn't adapt to legitimate format evolution.
- D) Manual inspection of every file doesn't scale as an automated pipeline practice.

---

**Q100.** Summarize: which single factor most often determines whether Dataflow or Dataproc is the "correct" exam answer for a new, greenfield pipeline (no legacy code)?
A) Preference for a fully managed, unified batch/streaming serverless model (Dataflow) unless there's a specific need for the Hadoop/Spark ecosystem itself
B) Whichever service is cheaper in all cases
C) Dataproc is always correct for greenfield pipelines
D) Dataflow cannot handle large-scale batch jobs

**Correct answer: A**
**Why A is correct:** Absent legacy Spark/Hadoop code or an explicit need for Spark-ecosystem tools, Dataflow's serverless, unified batch+streaming model with minimal operational overhead is generally the preferred default for new pipelines on the exam.
**Why the others are wrong:**
- B) Relative cost depends heavily on workload shape; there's no universal "always cheaper" rule driving this decision.
- C) Dataproc is preferred specifically when there's a Spark/Hadoop ecosystem reason, not as a default for all greenfield work.
- D) Dataflow fully supports large-scale batch processing; this is factually incorrect.
