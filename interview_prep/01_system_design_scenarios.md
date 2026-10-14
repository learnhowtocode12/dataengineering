# System Design & Scenario-Based Questions — Interview Guide & Q&A
> **Round mapping:** R3, run by a Staff Engineer or Tech Lead. This is the round most likely to single-handedly
> swing a borderline candidate — see the grading rubric below before you practice.

## Interview Guide
System design rounds for a senior data engineer are usually 45-60 minutes, open-ended, and evaluated on:
requirements clarification, trade-off articulation, ability to go deep on any component when pushed, and
production concerns (monitoring, failure modes, cost, security). Use a consistent framework:
**Clarify → Requirements (functional + non-functional) → High-level architecture → Deep dive on 1-2
components → Failure modes & trade-offs → Monitoring/cost/security wrap-up.**

A reusable mental checklist while designing:
1. Batch or streaming or both? What's the latency SLA?
2. Data volume (GB/TB/PB per day), growth rate, peak vs average.
3. Schema: structured/semi-structured, evolving?
4. Idempotency/exactly-once needs, backfill/replay requirements.
5. Who/what consumes the output (BI/Looker, ML, another service) and what access patterns does that imply?
6. Cost sensitivity and team skill set (justifies BigQuery vs Dataproc vs Dataflow choices).
7. Security/compliance (PII masking, row/column-level security, data residency).

## How This Round Is Graded
A Staff Engineer grading this round is listening for a specific sequence, and candidates lose points for
skipping steps even if the final architecture is correct:

| Step | What a Strong Hire does | What pulls it down to Lean/No Hire |
|---|---|---|
| **Clarify** | Asks 3-5 sharp questions before drawing anything (volume, latency SLA, consumers, budget) | Starts drawing boxes immediately with no clarifying questions |
| **High-level design** | Simple, labeled flow first (ingest → process → store → serve) | Jumps straight to deep detail on one component, loses the big picture |
| **Trade-offs** | Proactively states 2+ options and why one was chosen ("Dataflow vs Dataproc here because...") | States only one option as if it were the only possible answer |
| **Depth on request** | Goes deep smoothly when asked ("let's zoom into the schema design") | Is only shallow-ready; can't go beyond the diagram level on any single box |
| **Failure modes** | Volunteers what breaks (skew, late data, backfill, schema drift) without being asked | Only discusses the happy path unless explicitly pushed |
| **Cost/security** | Mentions cost and security/compliance unprompted as part of the design, not an afterthought | Never mentions cost or security unless directly asked |
| **Pushback handling** | Updates the design calmly when the interviewer challenges an assumption, without getting defensive | Gets defensive or simply repeats the original answer louder |

A candidate who nails the diagram but never volunteers a trade-off or a failure mode typically scores a
"Lean Hire" at best in this round — the diagram is table stakes, the *judgment* is what's being graded.

---

## Scenario Q&A

**Q1: Design an end-to-end pipeline to ingest clickstream events (billions/day) and make them available
for near-real-time dashboards and daily batch analytics.**
A: **Ingestion**: client/app SDKs publish events to Pub/Sub (high-throughput, durable buffer, decouples
producers from processing). **Streaming path**: a Dataflow (Beam) streaming pipeline reads from Pub/Sub,
parses/validates (dead-letter malformed events to a separate topic/GCS path), applies windowed
aggregations (e.g., 1-minute fixed windows for near-real-time counts) with watermarking/allowed lateness
for out-of-order events, writes to a BigQuery streaming table (Storage Write API) feeding a Looker
real-time dashboard (short cache TTL/datagroup). **Batch path**: the same raw events (or a GCS archive
sink from the Dataflow pipeline, or direct Pub/Sub-to-GCS export) are also loaded into a partitioned,
clustered BigQuery raw table, orchestrated by Airflow/Composer for daily reprocessing, late-data
reconciliation, and session/attribution modeling (join against other dimension tables not available in
the streaming path). **Serving**: curated marts partitioned/clustered appropriately, exposed via LookML
explores with access filters for row-level security. **Failure modes to call out**: Pub/Sub backlog
growth (autoscale Dataflow workers, alert on subscription backlog age), duplicate events (dedupe by event
ID with a bounded dedup window), schema drift from app releases (schema registry/contract testing
upstream).

**Q2: Design a system to migrate 50 nightly batch ETL jobs from an on-prem Informatica PowerCenter
environment to GCP with minimal business disruption.**
A: Inventory/classify all 50 mappings by complexity, data volume, source/target systems, and downstream
consumers. Stand up a landing zone: GCS buckets (raw, partitioned by date) and BigQuery staging datasets.
Build a connectivity bridge first (IICS Secure Agent or Datastream/PowerExchange CDC) to replicate
on-prem source data into GCS/BigQuery without touching transformation logic yet — this decouples
"get data into GCP" from "rewrite transformation logic" and de-risks the timeline. Triage transformation
rewrites: SQL-expressible mappings → BigQuery SQL/scheduled queries; complex procedural logic →
PySpark on Dataproc (closest paradigm match) or Beam/Dataflow. Re-platform orchestration: convert
PowerCenter workflows to Airflow DAGs preserving dependency/notification semantics. Run legacy and new
pipelines in parallel for a validation window, reconciling via automated row-count/checksum/aggregate
diffing (a dedicated reconciliation Airflow DAG comparing old vs new output tables). Cut over
dashboards/consumers only after sign-off, keep legacy on standby for a rollback window, then decommission.
Call out: this is as much a program-management/validation problem as a technical one — testing effort
usually dominates.

**Q3: A BigQuery table used by dozens of dashboards is becoming very expensive to query. Walk through
your diagnosis and fix.**
A: Check `INFORMATION_SCHEMA.JOBS_BY_PROJECT`/billing export for top queries by bytes billed — identify
whether it's a few expensive ad hoc queries or broad high-frequency dashboard traffic. Check the table's
partitioning/clustering against actual filter patterns in those queries (e.g., Looker-generated SQL) —
missing partition pruning is the most common root cause. Consider `require_partition_filter=true` to force
callers to filter. Add materialized views or aggregate tables for the most common aggregation patterns
(ties into Looker's `aggregate_table`/PDT features). Evaluate moving heavy, steady BI traffic to a
reservation/flat-rate slot commitment instead of on-demand if volume justifies it, and consider BI Engine
for sub-second dashboard acceleration on a curated reporting dataset. Longer-term: push cost/consumption
visibility to dashboard owners via labels and chargeback reporting so inefficient queries get fixed at the
source.

**Q4: Design a pipeline for daily CDC ingestion from an on-prem Oracle database into BigQuery, handling
inserts/updates/deletes, with a goal of <1 hour freshness.**
A: Use a log-based CDC tool (Datastream, or Informatica PowerExchange/IICS CDC connector) to capture
row-level changes continuously rather than batch-extracting entire tables (minimizes source load, meets
freshness SLA). Stream changes into a GCS staging area or directly into a BigQuery raw/staging table
(append-only change log, including operation type and a source commit timestamp/LSN). A scheduled
Airflow DAG (or a Dataflow pipeline) runs a `MERGE` every N minutes: match on primary key, apply updates
for the latest version per key (dedupe multiple changes to the same key within the batch, keeping the
most recent by source timestamp), handle deletes (soft-delete flag or hard delete depending on downstream
needs), writing to the curated BigQuery table. Monitor CDC lag (time between source commit and BigQuery
availability) as the core freshness SLA metric, and alert if lag exceeds threshold.

**Q5: Design a cost-efficient architecture for a PySpark workload that runs once nightly but needs to
process a rapidly growing data volume (10x over 2 years).**
A: Use ephemeral Dataproc clusters created per job run (via Airflow `DataprocCreateClusterOperator`) sized
by an autoscaling policy bound to the job's typical data volume, with secondary workers as preemptible/
Spot VMs for the bulk of compute cost savings, and primary workers as standard VMs for stability. Store
input/output on GCS (not HDFS) so cluster lifecycle and storage scale independently — growing data volume
doesn't require resizing persistent storage, just adjusting autoscaling max-worker bounds. Periodically
revisit whether parts of the job are better expressed as BigQuery SQL (if the growth is in simple
aggregation-style workloads that BigQuery would handle more cheaply than maintaining a growing Spark
cluster) — build this re-evaluation into a recurring architecture review rather than assuming Dataproc is
permanent.

**Q6: A critical Airflow DAG intermittently fails at 2am and pages on-call. How do you approach root-
causing and preventing recurrence?**
A: Check Airflow task logs and the specific failing task's error (timeout, OOM, upstream data not ready,
transient API/network error). Check whether it correlates with a specific condition (e.g., larger data
volume on certain days — month-end, weekends) suggesting a resource/timeout tuning issue vs a genuine data
problem (e.g., a source file sometimes missing at scheduled time — needs a sensor/retry with backoff
rather than failing immediately). Add better retries with exponential backoff for transient failures,
increase resource allocation or timeout if it's a scale-related failure, add a dead-letter/alert path that
distinguishes "needs immediate page" vs "can wait until morning," and write a short postmortem documenting
root cause and the specific fix (retry policy change, resource bump, sensor instead of fixed wait) to
prevent recurrence — and mention this is also a good behavioral story to have ready.

**Q7: How would you design a data quality framework across this stack (BigQuery, Dataflow, Dataproc,
Airflow)?**
A: Define expectations (not-null, uniqueness, referential integrity, freshness, value ranges, row-count
deltas vs historical trend) as declarative checks — either via a framework (e.g., Great Expectations,
dbt tests if using dbt, or custom BigQuery assertion queries) run as an explicit Airflow task after each
load/transform step, failing the DAG (or routing to a quarantine table) before bad data reaches curated/
BI layers. Track data quality metrics over time (e.g., in a dedicated BigQuery dataset) to catch slow
drift, not just hard failures, and surface a data quality dashboard (in Looker) to stakeholders so trust
in the pipeline is visible, not just assumed.

**Q8: Design a multi-tenant data platform on GCP where each business unit has its own data but shares
common infrastructure/tooling.**
A: Separate BigQuery datasets (or projects) per business unit for data isolation and cost
attribution/quota control, with a shared "common"/reference dataset (e.g., shared dimension tables,
currency conversion, calendar) exposed via authorized views so BUs don't duplicate reference data.
Shared orchestration (one Composer environment, or isolated per BU if noisy-neighbor/compliance concerns
require it) with per-BU DAG folders and IAM-scoped service accounts so one BU's pipeline can't
read/write another's data. Shared Looker instance with per-BU models/explores and access filters/
permission sets scoped to each BU's user group. Centralized platform team owns shared infra (Composer
upgrades, connector libraries, CI/CD templates) while BU teams own their own DAGs/transformations within
guardrails — balances central governance with team autonomy.

**Q9: How would you design disaster recovery / business continuity for a critical BigQuery-based
reporting pipeline?**
A: Identify RPO/RTO requirements first. Use BigQuery's built-in redundancy (multi-zone within a region) as
baseline; for regional-outage protection, consider cross-region dataset replication/scheduled exports to
a secondary region's bucket/dataset, or at minimum ensure raw source data (GCS) is in a multi-region/
dual-region bucket so pipelines can be replayed from raw data in a secondary region if needed. Keep
infrastructure-as-code (Terraform) for all pipeline resources (datasets, Composer environment, Dataflow
templates) so the entire stack can be redeployed in a new region/project quickly. Document and
periodically test the actual recovery runbook (not just assume the design works) — a stated failure mode
in DR design is untested runbooks.

**Q10: Walk through how you'd approach a take-home or live "design a pipeline" prompt you've never seen
before, in the first 2 minutes.**
A: Resist jumping straight to a diagram. First restate the problem in your own words and ask 2-4 clarifying
questions (data volume/velocity, latency SLA, existing infra constraints, team skill set/preferences,
budget sensitivity). Then state assumptions explicitly if the interviewer doesn't have answers ("I'll
assume batch daily volume of X, no sub-minute latency requirement — let me know if that's wrong").
Sketch a simple high-level flow first (ingest → process → store → serve) before adding detail, and
explicitly ask the interviewer which part they want you to go deeper on rather than guessing — this
signals senior-level collaborative design behavior rather than a memorized template dump.
