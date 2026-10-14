# Apache Iceberg Coding Questions — Round 2 Drills

## Interview Guide
Expect Spark SQL / PySpark snippets against an Iceberg catalog (Dataproc context) and, increasingly,
BigQuery SQL against a BigLake Iceberg table. Graded on correct catalog/table syntax and — more
importantly — on narrating *why* each operation is metadata-only vs. a real data rewrite.

---

### Q1. Create an Iceberg table with a partition spec (Spark SQL on Dataproc)
```sql
CREATE TABLE iceberg_catalog.sales.orders (
  order_id BIGINT,
  customer_id BIGINT,
  order_ts TIMESTAMP,
  amount DECIMAL(10, 2)
)
USING iceberg
PARTITIONED BY (days(order_ts));
```
**Talk through:** `days(order_ts)` is a **partition transform** — Iceberg derives the partition value from
the column automatically (hidden partitioning); queries filter on `order_ts` directly, they never need to
know the physical partition expression exists.

---

### Q2. Read/write an Iceberg table from PySpark
```python
spark = (
    SparkSession.builder
    .config("spark.sql.catalog.iceberg_catalog", "org.apache.iceberg.spark.SparkCatalog")
    .config("spark.sql.catalog.iceberg_catalog.catalog-impl", "org.apache.iceberg.gcp.biglake.BigLakeCatalog")
    .config("spark.sql.catalog.iceberg_catalog.warehouse", "gs://my-bucket/warehouse")
    .getOrCreate()
)

df = spark.read.table("iceberg_catalog.sales.orders")
df.filter(F.col("amount") > 100).write.mode("append").insertInto("iceberg_catalog.sales.orders")
```
**Talk through:** the catalog config block is the key thing to get right — it's what tells Spark "this
table lives in BigLake's Iceberg catalog, backed by this GCS warehouse path," the same catalog a BigQuery
query against the equivalent BigLake table would resolve through.

---

### Q3. Schema evolution — add a column without rewriting data
```sql
ALTER TABLE iceberg_catalog.sales.orders ADD COLUMN discount_pct DECIMAL(5, 2);
```
**Talk through:** this is a metadata-only operation (new column ID added to the schema) — existing data
files are untouched and simply read back as `NULL` for `discount_pct`; contrast explicitly with a Hive
table where this kind of change can require a full table rewrite or break older partitions' readability.

---

### Q4. Partition evolution — change partitioning going forward
```sql
ALTER TABLE iceberg_catalog.sales.orders
  REPLACE PARTITION FIELD days(order_ts) WITH hours(order_ts);
```
**Talk through:** data written before this statement keeps its old daily partition layout; data written
after uses hourly — Iceberg's planner transparently queries across both without the user specifying which
range uses which scheme. Explicitly state: no historical data is rewritten by this statement.

---

### Q5. Time travel query
```sql
-- By timestamp
SELECT * FROM iceberg_catalog.sales.orders FOR SYSTEM_TIME AS OF '2026-10-01 00:00:00';

-- By snapshot ID (Spark syntax)
SELECT * FROM iceberg_catalog.sales.orders VERSION AS OF 8606349245630051323;
```
**Follow-up:** "How would you find available snapshot IDs?" →
`SELECT * FROM iceberg_catalog.sales.orders.snapshots` (Iceberg's metadata tables expose snapshot history
queryable like a regular table).

---

### Q6. Rollback to a previous snapshot after a bad load
```sql
CALL iceberg_catalog.system.rollback_to_snapshot('sales.orders', 8606349245630051323);
```
**Talk through:** this atomically moves the table's current-snapshot pointer backward — it's an instant
metadata operation, not a data-restore-from-backup operation, which is why it's fast enough to use as a
real incident-response tool, not just a disaster-recovery last resort.

---

### Q7. Compact small files (maintenance procedure)
```sql
CALL iceberg_catalog.system.rewrite_data_files(
  table => 'sales.orders',
  options => map('target-file-size-bytes', '536870912')  -- 512MB target
);
```
**Talk through:** run this periodically (e.g., a nightly/weekly Dataproc maintenance job) on tables that
receive many small streaming commits — frame it the same way you'd frame routine warehouse maintenance:
necessary upkeep, not a one-time fix.

---

### Q8. Expire old snapshots to reclaim storage
```sql
CALL iceberg_catalog.system.expire_snapshots(
  table => 'sales.orders',
  older_than => TIMESTAMP '2026-09-01 00:00:00',
  retain_last => 10
);
```
**Follow-up:** "What's the risk of expiring snapshots too aggressively?" → you lose the ability to time
travel/rollback to anything older than the retained window — balance storage cost against how far back
your incident-response/audit needs realistically require rollback capability.

---

### Q9. Query a BigLake Iceberg table directly from BigQuery
```sql
-- Once a BigLake Iceberg table is registered against the same GCS warehouse/catalog:
SELECT customer_id, SUM(amount) AS total_spend
FROM `my_project.sales.orders`   -- a BigLake table, same underlying Iceberg data
WHERE order_ts >= TIMESTAMP('2026-10-01')
GROUP BY customer_id
ORDER BY total_spend DESC
LIMIT 10;
```
**Talk through:** this is the actual payoff to call out — the PySpark job in Q2 and this BigQuery query
are reading the *same physical files* through the *same catalog*, not two separately-synced copies of the
data, which is the core lakehouse value proposition versus maintaining a separate ETL pipeline just to copy
data into BigQuery-native storage for analysts to query.

---

### Q10. Debug exercise: a reader is seeing stale data after a Spark job committed new rows
**Prompt:** "A Dataproc Spark job successfully wrote new rows to an Iceberg table, confirmed by checking
the data files in GCS — but a BigQuery query against the same BigLake table doesn't show them. Why?"
**Answer:** Almost always a **catalog pointer** issue, not a data issue — either the Spark job wrote data
files but the commit (the atomic swap of the catalog's current-metadata pointer) didn't actually succeed/
propagate (check for a swallowed exception around the commit step), or BigQuery/BigLake is resolving
against a different catalog/metastore instance than the one Spark committed through (a catalog
configuration mismatch between the two engines). Walk through checking
`SELECT * FROM table.snapshots ORDER BY committed_at DESC` to see whether the new snapshot actually exists
in the catalog at all before assuming it's a BigQuery-side caching issue.
