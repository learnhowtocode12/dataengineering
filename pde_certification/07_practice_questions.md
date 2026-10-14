# Practice Questions

Answer each, then check the explanation. These mirror common exam scenario patterns.

---

**Q1.** Your company has IoT sensors on delivery trucks sending GPS coordinates every second. You need to store this data for real-time dashboards (last 24 hours) and also run historical trend analysis going back 2 years. Which combination is best?

<details><summary>Answer</summary>
Ingest via **Pub/Sub** → **Dataflow** (streaming) writes recent data to **Bigtable** (low-latency time-series lookups for dashboards) and also writes aggregated/raw data to **BigQuery** (partitioned by date) for historical analytics. Using Bigtable alone is bad for ad-hoc SQL trend analysis; BigQuery alone adds latency for the "live dashboard" need.
</details>

---

**Q2.** You need to migrate an on-premises Hadoop cluster running Spark jobs to GCP as fast as possible with minimal code changes, while reducing cost during idle periods.

<details><summary>Answer</summary>
**Dataproc** with **ephemeral clusters** (create cluster, run job, write to GCS/BigQuery, delete cluster). Use the Cloud Storage connector instead of HDFS. Avoid rewriting in Dataflow/Beam unless there's a long-term reason to — the requirement is "fast migration, minimal change."
</details>

---

**Q3.** A BigQuery table storing 5 years of event data is queried almost always with a `WHERE event_date BETWEEN ...` filter, and query costs are high. What two changes reduce cost the most?

<details><summary>Answer</summary>
**Partition the table by `event_date`** (reduces bytes scanned to only relevant partitions) and **cluster by a frequently-filtered column** (e.g., `user_id` or `event_type`) for further pruning within partitions.
</details>

---

**Q4.** You must ensure that even if an engineer's IAM permissions are mistakenly over-granted, sensitive BigQuery datasets cannot be exfiltrated to an external project/organization.

<details><summary>Answer</summary>
**VPC Service Controls** — creates a security perimeter around the service, blocking data movement outside the perimeter regardless of IAM grants.
</details>

---

**Q5.** Your streaming Dataflow pipeline needs to handle events that arrive late (e.g., mobile devices offline for hours) without dropping them, while still producing timely aggregate results for on-time data.

<details><summary>Answer</summary>
Use **windowing with watermarks**, set **allowed lateness**, and configure **triggers** to emit early/on-time results plus a late/final firing when the late data arrives. This avoids either dropping late data or holding results indefinitely.
</details>

---

**Q6.** A startup wants to add sentiment analysis to customer support tickets but has no ML engineers and a tight deadline.

<details><summary>Answer</summary>
Use the **Natural Language AI** pre-trained API — no training required, fastest time to market. Building a custom model or even AutoML is unnecessary extra effort/cost for a solved, common problem.
</details>

---

**Q7.** Row keys in your Bigtable table are the raw event timestamp, and you're seeing severe write hotspotting on a few nodes.

<details><summary>Answer</summary>
Redesign the row key: use **field promotion** (e.g., prefix with device ID or a hash) or a **reversed/salted timestamp** so writes distribute evenly across the key space instead of all landing on the "newest" tablet.
</details>

---

**Q8.** You need a global, strongly consistent, relational database for a financial ledger system that must scale horizontally beyond what a single Cloud SQL instance can handle.

<details><summary>Answer</summary>
**Cloud Spanner** — the only GCP option offering horizontal scalability with ACID transactions and strong consistency globally. Cloud SQL scales vertically/with read replicas only, not horizontally for writes.
</details>

---

**Q9.** Your company must retain all data access audit logs for 7 years for compliance, cheaply.

<details><summary>Answer</summary>
Create a **log sink** exporting Cloud Logging audit logs to a **Cloud Storage bucket with Archive storage class** and a lifecycle/retention policy — cheapest long-term storage, decoupled from live logging retention limits.
</details>

---

**Q10.** A data science team wants to guarantee that the exact same feature transformations used during model training are applied during real-time online prediction, to avoid training/serving skew.

<details><summary>Answer</summary>
Use **Vertex AI Feature Store** to centrally compute, store, and serve features so both training and serving pipelines read from the same source.
</details>

---

## Tips for Exam Day
- Eliminate obviously wrong answers first (usually 1–2 of 4 options are clearly off-topic).
- When two options both "work," pick the one with **less operational overhead** or that **better matches explicitly stated constraints** (cost, latency, existing skills, compliance).
- Re-read the question stem for constraints you might have skimmed past (e.g., "minimize cost," "no ML team," "must be real-time") — these words usually point directly to the correct answer.
- Don't overthink: GCP certification questions reward the "well-architected, managed-service-first" answer over clever workarounds.
