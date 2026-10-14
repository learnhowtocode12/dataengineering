# BigQuery — Interview Guide & Q&A
> **Round mapping:** R2 (technical deep dive), with 1-2 SQL questions often appearing in R1. Hands-on
> drills: [coding.md](coding.md). See also [../gcp_fundamentals/guide.md](../gcp_fundamentals/guide.md)
> (general GCP service selection/IAM), [../pubsub/guide.md](../pubsub/guide.md) (streaming ingestion),
> [../apache_iceberg/guide.md](../apache_iceberg/guide.md) (BigLake/open table formats), and
> [../sql/guide.md](../sql/guide.md) (dialect-agnostic SQL fundamentals).

## Interview Guide
At 6+ years, expect deep BigQuery questions (it's usually the centerpiece of GCP data engineer interviews):
partitioning/clustering strategy, cost control (slots vs on-demand), query optimization, schema design
(nested/repeated vs normalized), and security/governance (IAM, row/column-level security, data masking).
Expect at least one live SQL question (write/optimize a query) and one "design the warehouse schema for X"
question.

---

## Q&A

**Q1: Explain BigQuery's architecture at a high level (Dremel, columnar storage, separation of
compute/storage).**
A: BigQuery stores data in a proprietary columnar format (Capacitor) on Colossus (Google's distributed
file system), fully decoupled from compute. Queries run on **Dremel**, a multi-level execution tree that
pushes query fragments down to thousands of workers in parallel ("slots") and aggregates results back up
the tree ("shuffle" via an in-memory network, Jupiter). Because storage and compute scale independently,
you pay for storage (cheap, per-GB) and compute (per-byte-scanned for on-demand, or per-slot-hour/flat-rate
for reserved) separately — this is the key cost lever to understand.

**Q2: On-demand vs flat-rate (capacity/slot-based) pricing — how do you decide, and how do you control
cost either way?**
A: On-demand charges per TB scanned ($/TB) — good for unpredictable/bursty, low-to-moderate volume
workloads; risk is a bad query (SELECT *, no partition filter) scanning huge data and costing a lot.
Flat-rate/capacity pricing (now "editions" with autoscaling slots) charges for reserved slot-hours
regardless of bytes scanned — better for predictable, high, steady query volume (e.g., BI dashboards hit
constantly) since cost becomes flat and scanning more doesn't cost more (but you can be slot-constrained).
Cost controls either way: partitioning + clustering to prune scanned data, `--maximum_bytes_billed` /
custom cost controls, materialized views for repeated aggregations, BI Engine for dashboard acceleration,
and query review (avoid `SELECT *`, avoid unnecessary `ORDER BY` on huge result sets).

**Q3: When do you partition a table, and by what? When do you also cluster?**
A: Partition on a column queries commonly filter on to prune data scanned — almost always a date/timestamp
column (`_PARTITIONDATE` or ingestion time, or a date column via `PARTITION BY DATE(col)`), or sometimes
an integer range. Partitioning reduces bytes scanned and bounds partition count (max partitions limits
apply). Cluster (up to 4 columns) on high-cardinality columns frequently used in filters/joins/aggregations
*within* a partition (e.g., `customer_id`, `country`) — BigQuery sorts data by cluster columns and prunes
blocks, which partitioning alone can't do for non-date dimensions. Rule of thumb: partition by date for
time-bound queries and incremental loads; cluster by the next-most-selective filter column(s).

**Q4: How do you design nested/repeated (STRUCT/ARRAY) schemas vs normalized star schema in BigQuery, and
why?**
A: Unlike row-oriented OLTP databases, BigQuery is optimized for denormalized, nested data because joins
across huge tables are expensive (shuffle) while nested/repeated fields are stored and scanned
column-wise with no join needed. Pattern: embed naturally 1:many relationships (e.g., an order with line
items) as a `RECORD REPEATED` field instead of a separate line-items table, when the child is always
queried in the context of the parent. Keep separate tables (star schema with dimension tables) when the
"child"/dimension entity is large, slowly-changing, and queried independently (e.g., a customer dimension
joined from many fact tables) — in that case use clustering on the join key and let BigQuery's join
optimizer (often broadcast for small dims) handle it. This denormalization trade-off is the opposite of
classic OLTP normal forms — see [../sql/guide.md](../sql/guide.md) Q3 for why the two worlds optimize
differently.

**Q5: Explain MERGE / upsert patterns in BigQuery for incremental loads / SCD.**
```sql
MERGE INTO target T
USING staging S
ON T.id = S.id
WHEN MATCHED AND S.updated_at > T.updated_at THEN
  UPDATE SET T.col1 = S.col1, T.updated_at = S.updated_at
WHEN NOT MATCHED THEN
  INSERT (id, col1, updated_at) VALUES (S.id, S.col1, S.updated_at);
```
A: Use `MERGE` for upserts from a staging/CDC table into a target, for SCD Type 1 (overwrite) and with
extra logic (closing out old row's `end_date`, inserting a new row) for SCD Type 2. Watch for: `MERGE`
cost/performance on very large targets (scan cost on the target side — partition filter on `T` if
possible), and that BigQuery has DML quotas (mutating partitions per table per day) that can bite with
very frequent small merges — batch updates instead of near-real-time row-by-row merges where possible.

**Q6: How do you handle slowly changing dimensions (SCD Type 2) in BigQuery?**
A: Maintain `effective_start_date`, `effective_end_date` (or `is_current` flag), and a surrogate key.
On each load: `MERGE` to set `effective_end_date = current load date` / `is_current = false` for existing
rows whose attributes changed, then `INSERT` new versioned rows with `is_current = true`. In BigQuery this
is often implemented as two DML statements or a single `MERGE` with `WHEN MATCHED` (expire old) and
`WHEN NOT MATCHED` (insert new) combined with a windowed staging dataset that already diffs current vs
incoming.

**Q7: What's the difference between a BigQuery native table, external table, and `BigLake` table?**
A: Native tables store data in BigQuery-managed storage (Capacitor/Colossus) — best performance, full
feature support. External tables query data in place (GCS, Bigtable, Drive, Cloud SQL federated) without
loading — convenient for infrequently-queried or large raw files, but slower, no clustering, limited
caching, and some SQL feature restrictions. BigLake tables are external tables with a unified
security/governance layer (fine-grained access control, consistent with native tables) over open formats
(Parquet/ORC/Iceberg/Delta on GCS) — used for lakehouse architectures without copying data into BigQuery
storage. See [../apache_iceberg/guide.md](../apache_iceberg/guide.md) Q10 for the full BigLake-Iceberg
integration story.

**Q8: Explain BigQuery query optimization: how do you debug a slow/expensive query?**
A: Use the query execution details / `EXPLAIN` plan in the console to see stage timing and
bytes shuffled, check "bytes processed" estimate before running (dry run,
`bq query --dry_run`), check for missing partition/cluster filters causing full scans, check for
expensive `JOIN`s (large-large join without a filter, cross join), repeated subqueries that should be
CTEs or materialized views, `ORDER BY` without `LIMIT` on huge result sets, and `APPROX_*` functions
(e.g., `APPROX_COUNT_DISTINCT`) instead of exact aggregation when approximate is acceptable. Also check
slot contention (INFORMATION_SCHEMA.JOBS / reservations) if using flat-rate pricing. See
[../sql/guide.md](../sql/guide.md) Q7 for the general-SQL version of execution-plan reading.

**Q9: How do you implement row-level and column-level security in BigQuery?**
A: Row-level security via `CREATE ROW ACCESS POLICY` filters rows based on a predicate tied to
`SESSION_USER()` or a group-membership lookup table. Column-level security via policy tags in
Data Catalog/Dataplex taxonomies attached to columns, combined with IAM to restrict which principals can
read tagged columns (and dynamic data masking policies to show masked/hashed values instead of outright
denial). Both are enforced regardless of which tool queries the table (Looker, BI tools, ad hoc SQL).

**Q10: How do you design a streaming ingestion pattern into BigQuery (streaming inserts vs
Storage Write API vs batch load)?**
A: Legacy `tabledata.insertAll` (streaming inserts) has per-row cost and a short dedup window via
`insertId`; the modern **BigQuery Storage Write API** is the recommended path — supports exactly-once
semantics via stream offsets, higher throughput, lower cost, and both default and application-created
streams for transactional multi-row commits. For near-real-time but not sub-second needs, micro-batch
loads (e.g., every few minutes via Dataflow or a scheduled job) are cheaper than per-record streaming.
Pure batch `bq load` / load jobs are free (quota-limited) and best for periodic bulk loads from GCS. See
[../pubsub/guide.md](../pubsub/guide.md) Q11 for the Pub/Sub-direct-to-BigQuery subscription option.

**Q11: How do you handle schema evolution in BigQuery pipelines?**
A: Use `ALLOW_FIELD_ADDITION`/`ALLOW_FIELD_RELAXATION` schema update options on load/query jobs to permit
additive, backward-compatible changes (new nullable columns, relaxing REQUIRED to NULLABLE). For breaking
changes (type changes, renames, removing columns), version the table/dataset or use a view layer to
decouple consumers from physical schema, and roll out changes with a deprecation window. Avoid wildcard
`SELECT *` in downstream views/ETL so schema additions don't silently break column-order-dependent logic.

**Q12: Write a query to find the top 3 products by revenue per category (window function).**
```sql
WITH ranked AS (
  SELECT
    category,
    product_id,
    SUM(revenue) AS total_revenue,
    RANK() OVER (PARTITION BY category ORDER BY SUM(revenue) DESC) AS rnk
  FROM sales
  GROUP BY category, product_id
)
SELECT category, product_id, total_revenue
FROM ranked
WHERE rnk <= 3
ORDER BY category, rnk;
```
Discuss `RANK()` vs `DENSE_RANK()` vs `ROW_NUMBER()` for tie-handling.

**Q13: What are materialized views in BigQuery and how do they differ from scheduled queries into a
table?**
A: Materialized views automatically and incrementally refresh precomputed results (BigQuery tracks base
table changes and updates only deltas), are transparently used by the query optimizer (smart tuning can
rewrite a query against the base table to hit the MV automatically), and reduce bytes scanned/cost for
repeated aggregation patterns. Scheduled queries writing into a plain table require you to manage
incremental refresh logic yourself and consumers must know to query the derived table directly — more
manual but more flexible for complex transformation logic MVs don't support.

**Q14: How do you monitor and control BigQuery costs across many teams (governance)?**
A: Use custom cost controls/quotas per project, separate projects or reservations per team with
assignment-based slot allocation, `INFORMATION_SCHEMA.JOBS_BY_*` and billing export to BigQuery for
chargeback dashboards (often visualized in Looker), labels on jobs/tables for cost attribution,
alerting on `bytes_billed` anomalies, and enforcing partition-filter-required tables
(`require_partition_filter=true`) to prevent accidental full scans.

**Q15: Explain `APPROX_COUNT_DISTINCT` / HyperLogLog sketches and when to use them.**
A: `COUNT(DISTINCT ...)` requires an exact shuffle/dedup which is expensive at high cardinality;
`APPROX_COUNT_DISTINCT` uses HyperLogLog++ sketches for a fast, small-error-margin approximation, and
BigQuery supports persisting sketches (`HLL_COUNT.INIT`/`MERGE`) so you can incrementally merge
distinct-count sketches across partitions/days without re-scanning historical data — valuable for daily
unique-user dashboards over huge event tables.

**Q16: How would you load and query semi-structured JSON logs in BigQuery efficiently?**
A: Load with autodetect or an explicit schema using nested RECORD/REPEATED fields (avoid storing raw JSON
strings and parsing with `JSON_EXTRACT` at query time for high-volume data — that defeats columnar
pruning). If schema is highly variable, BigQuery's native `JSON` type (distinct from STRING) allows
flexible querying with some columnar benefits, or stage raw JSON in GCS/external table and normalize into
a typed native table via a scheduled Dataflow/scheduled-query ETL step.

**Q17: How do you approach a "design the data warehouse" system design question for, say, an e-commerce
company?**
A: Clarify requirements (batch vs near-real-time, data volume, consumers — BI vs ML vs ad hoc). Propose:
raw/landing layer (GCS, immutable, partitioned by ingestion date) → staging dataset in BigQuery (typed,
deduped, minimal transformation, often via Dataflow/Dataproc) → curated/warehouse layer (star schema or
denormalized fact tables, partitioned/clustered, SCD-managed dimensions) → semantic/serving layer (Looker
LookML models, authorized views). Call out orchestration (Airflow/Composer DAGs with dependency-aware
backfills), data quality checks (e.g., row count/null checks, dbt tests or custom assertions), and
monitoring/alerting (freshness SLAs). See `01_system_design_scenarios.md` at the repo root for the full
worked version of this scenario.

**Q18: What are BigQuery reservations, slots, and autoscaling (Editions)?**
A: A slot is a unit of compute (CPU+RAM) for query execution. Reservations group slots and assign them to
projects/folders/organizations via assignments. BigQuery Editions (Standard/Enterprise/Enterprise Plus)
let you buy slots with different autoscaling, SLA, and feature tiers, and autoscaling reservations grow/
shrink slot capacity within a baseline/max range based on load, billed per-second — balancing predictable
cost with elasticity versus fixed flat-rate commitments.
