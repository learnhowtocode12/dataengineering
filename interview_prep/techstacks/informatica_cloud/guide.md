# Informatica Cloud (IICS / IDMC) — Interview Guide & Q&A
> **Round mapping:** R2 (technical deep dive) and often revisited as the centerpiece story in R4. Hands-on
> drills: [coding](coding.md). See also
> [../informatica_powercenter/guide](../informatica_powercenter/guide.md) (the legacy on-prem
> predecessor — the migration narrative below starts from there).

## Interview Guide
This is **the single most differentiating round for this specific profile**: Informatica Cloud (IICS/IDMC)
questions cover the iPaaS architecture itself, but the real signal interviewers are looking for is a
credible **Informatica-to-GCP migration narrative** (triage, reconciliation, cutover risk). Have this ready
in detail — it's also the centerpiece story many candidates reuse in the managerial round
(`02_managerial_round_leadership` at the repo root).

---

## Q&A

**Q1: How does Informatica Cloud (IICS, now branded IDMC) differ architecturally from PowerCenter?**

**Answer:** IICS is a SaaS/iPaaS platform — no on-prem repository/Integration Service to install/patch; a
lightweight **Secure Agent** (installed on-prem or in a VM/container in the cloud) handles the actual data
movement/connectivity to keep data within your network boundary while control/metadata lives in
Informatica's cloud control plane. It replaces PowerCenter's Designer/Workflow Manager with a browser-based
UI (Data Integration, Mapping Designer), and natively supports a much broader set of cloud connectors
(BigQuery, GCS, Snowflake, Salesforce, REST APIs) out of the box versus PowerCenter needing custom
connectors/PowerExchange add-ons. See [../informatica_powercenter/guide](../informatica_powercenter/guide.md)
Q1 for the PowerCenter architecture this replaces.

**Q2: What is the Secure Agent and why does it matter for a GCP-connected IICS deployment?**

**Answer:** The Secure Agent is a lightweight, self-updating process you deploy (on-prem, GCE VM, or containerized)
that executes the actual data integration tasks and handles connectivity to your sources/targets — data
doesn't flow through Informatica's cloud servers, only metadata/control does. For a GCP deployment, you'd
typically run Secure Agents on a GCE VM (or GKE) within the VPC that has network access to on-prem
sources (via VPN/Interconnect) and to GCP targets (BigQuery, GCS, Cloud SQL), with scaling by adding more
Secure Agent instances/groups for throughput and high availability.

**Q3: What are the main building blocks in IICS Data Integration (mappings, tasks, taskflows)?**

**Answer:** **Mappings** are the equivalent of PowerCenter mappings (source → transformation → target), built in a
web-based Mapping Designer. A **mapping task** wraps a mapping with run-time parameters/schedule (like a
PowerCenter session). A **taskflow** sequences multiple tasks (mapping tasks, synchronization tasks, Data
Integration tasks, decision/wait steps) — the equivalent of a PowerCenter workflow, but also able to call
external REST APIs, Cloud Application Integration processes, or notifications natively.

**Q4: How do you connect IICS to BigQuery, and what are common gotchas?**

**Answer:** Use the native Google BigQuery connector (V2) configured with a service account key/Workload
Identity-compatible auth, specifying project/dataset, and either a Secure Agent running in GCP (lower
latency, VPC-local) or on-prem (if source data is on-prem and BigQuery is just the target). Gotchas:
BigQuery's DML quota limits (frequent small upserts can hit per-table mutation limits — batch instead),
schema evolution handling (the connector's "Create or Replace" vs "Update" target behavior must match
your schema evolution strategy), and performance (staging to GCS + `bq load` is typically far faster than
row-by-row API inserts for bulk loads — check whether the connector uses the Storage Write
API/load-job path for the volumes involved). See [../bigquery/guide](../bigquery/guide.md) Q10.

**Q5: Walk through a migration plan: an existing PowerCenter mapping needs to move to GCP-native
(BigQuery/Dataflow) — how do you approach it?**

**Answer:** 1) **Inventory & classify**: catalog existing mappings/workflows by complexity (simple passthrough/
lookup-heavy vs complex business logic), source/target types, SLA/criticality, data volume. 2) **Triage
migration path per mapping**: simple, SQL-expressible mappings → rewrite directly as BigQuery SQL
(scheduled query, dbt model, or a Dataflow/Beam batch job if non-BigQuery sources are involved); complex
row-level/procedural logic (unconnected lookups chained with complex expressions) → port to PySpark on
Dataproc or a Beam pipeline where procedural logic translates more naturally (see
[coding](coding.md) Q1 for a full worked translation); mappings already migrated to IICS can sometimes
stay there temporarily (hybrid) if the source is still on-prem, using IICS to land data into GCS/BigQuery
as a staging step while downstream transforms move to BigQuery/Dataflow. 3) **Re-platform orchestration**:
convert PowerCenter workflows/IICS taskflows into Airflow DAGs (mapping session dependencies to task
dependencies), preserving notification/failure-handling semantics. 4) **Validate**: run old and new
pipelines in parallel for a window, reconcile row counts/checksums/aggregate metrics between legacy and
new output before cutover. 5) **Cutover & decommission**: switch consumers to the new tables/dashboards,
keep legacy running read-only for a rollback window, then retire PowerCenter/IICS components once stable.

**Q6: What are the key risks/pitfalls in an Informatica-to-GCP migration, and how do you mitigate them?**

**Answer:** **Hidden business logic** buried in complex Expression transformations or unconnected lookups that
isn't documented anywhere else — mitigate by extracting and translating transformation logic
carefully, not just "simulating" the mapping blindly, and getting business/analyst sign-off on reconciled
output. **Performance regressions** from naive 1:1 translation (e.g., row-by-row Lookup patterns don't
map efficiently to Spark/Beam's distributed model — need to redesign as broadcast joins). **Schema/
data-type mismatches** (Informatica's type system vs BigQuery's) causing silent precision loss (e.g.,
decimal/timestamp handling). **Orchestration semantics gaps** (PowerCenter's event-wait/decision tasks
need equivalent Airflow sensor/branch patterns). **Underestimating testing effort** — reconciliation
testing (count/sum/checksum diffing between old and new pipeline output) is usually the largest and most
important chunk of migration work, not the transformation rewrite itself.

**Q7: Why would an organization keep Informatica Cloud (IICS) alongside a GCP-native stack rather than
migrating everything?**

**Answer:** IICS remains valuable as a connectivity/iPaaS layer for a huge breadth of pre-built connectors to
SaaS/on-prem systems (Salesforce, SAP, mainframes, legacy databases) that would otherwise require custom
connector development in Dataflow/Python; for business/citizen-integrator-friendly low-code pipeline
building where not every integration needs engineering-heavy custom code; and for incremental
modernization — using IICS as the extraction/landing layer into GCS/BigQuery while the heavy
transformation and orchestration logic progressively moves to GCP-native tools, rather than a risky
big-bang cutover.

**Q8: How do you handle CDC (change data capture) from an on-prem Oracle/SQL Server source into GCP using
Informatica tooling?**

**Answer:** PowerExchange (PowerCenter) or IICS's CDC-capable connectors capture change logs (log-based CDC
preferred over trigger-based for lower source-system overhead) and stage changes incrementally; land raw
CDC events into GCS/a staging BigQuery table, then apply `MERGE` logic (matching the source's insert/
update/delete markers) into the target curated BigQuery table — conceptually similar to the SCD `MERGE`
pattern discussed in [../bigquery/guide](../bigquery/guide.md) Q6, just with Informatica (Secure Agent)
handling the capture/replication leg instead of Debezium/Datastream.

**Q9: How do you approach performance tuning in IICS compared to PowerCenter?**

**Answer:** Core principles carry over (minimize row-by-row processing, push down to source/target DB where
possible, size caches appropriately for Lookup transformations — see
[../informatica_powercenter/guide](../informatica_powercenter/guide.md) Q6), but IICS adds
cloud-specific levers: Secure Agent sizing/scaling (CPU/memory of the VM, number of agent instances in an
agent group for parallel task execution), advantage of serverless/elastic Secure Agent options in some
IDMC tiers, and leveraging target-native bulk-load paths (e.g., BigQuery load jobs/Storage Write API
through the connector) instead of row-level API calls for high-volume loads.

**Q10: What experience would you highlight if asked "why do you have both legacy Informatica and modern
GCP-native skills"?**

**Answer:** Position it as a strength: you've lived through a real modernization journey — you understand the
business logic debt embedded in 10+ year old ETL systems, you know how to reconcile/validate a migration
so nothing breaks silently, and you can bridge conversations between teams still running legacy
Informatica workloads and teams building GCP-native pipelines, which is exactly the skill set needed when
a company says "we want to get off Informatica but can't do it all at once."
