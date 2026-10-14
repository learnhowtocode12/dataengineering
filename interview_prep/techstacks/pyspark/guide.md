# PySpark — Interview Guide & Q&A
> **Round mapping:** R1 (coding screen) & R2 (deep dive). Hands-on drills:
> [coding.md](coding.md). Related: [../python/guide.md](../python/guide.md) (core language fundamentals)
> and [../dataproc/guide.md](../dataproc/guide.md) (the GCP cluster platform PySpark jobs usually run on).

## Interview Guide
At 6+ years, interviewers expect fluency in:
- **PySpark architecture**: driver/executor model, DAG/stages/tasks, shuffle, partitioning, catalyst
  optimizer, Tungsten, broadcast joins, skew handling, caching/persistence strategy.
- **Performance tuning**: knowing *why* a job is slow (skew, spill, small files, too many/few partitions)
  and the specific config/code fix.
- **Production coding**: writing idiomatic, testable PySpark code (not just notebooks) — modular
  transformations, unit tests with `pytest` + `chispa`/`pyspark.testing`, logging.
- **Live coding**: expect a coding round with a data-munging task (e.g., dedupe records, sessionization,
  top-N per group, slowly changing dimension logic) done in PySpark, sometimes on a shared editor without
  full IDE support.

Common format: 45-60 min round, 1-2 conceptual questions + 1 live coding problem.

---

## Q&A

**Q1: What is the GIL and how does PySpark avoid it for heavy computation?**
A: See [../python/guide.md](../python/guide.md) Q1 for the GIL itself. PySpark sidesteps it almost
entirely for heavy computation because the actual data processing happens in the JVM (Spark executors);
Python UDFs are the exception — they serialize data to a Python worker process per task (via Py4J/Arrow),
which is why native Spark SQL functions are preferred over Python UDFs for performance, and why pandas
UDFs (vectorized, Arrow-based) are faster than row-at-a-time UDFs.

**Q2: Explain Spark's architecture: driver, executors, cluster manager.**
A: The **driver** runs the user's `main()`, builds the DAG of transformations, and schedules tasks. The
**cluster manager** (YARN on Dataproc, Kubernetes, or standalone) allocates resources. **Executors** are
JVM processes on worker nodes that run tasks and hold cached data/shuffle output. Each action triggers a
job → split into stages (at shuffle boundaries) → split into tasks (one per partition).

**Q3: Narrow vs wide transformations, and why it matters.**
A: Narrow transformations (`map`, `filter`, `select`) don't require data movement — each output partition
depends on one input partition, so they can be pipelined within a stage. Wide transformations
(`groupBy`, `join`, `distinct`, `repartition`) require a **shuffle** — data is redistributed across the
cluster, which is expensive (network + disk I/O + serialization). Stage boundaries occur at shuffles.
Minimizing shuffles (e.g., using `reduceByKey`-style aggregation instead of `groupByKey`, broadcasting
small tables for joins) is a core tuning lever.

**Q4: How does a broadcast join work and when do you force one?**
A: Spark can broadcast a small DataFrame to every executor so a join becomes a local hash-join with no
shuffle of the large table. Triggered automatically if the small side is under
`spark.sql.autoBroadcastJoinThreshold` (default 10MB), or forced with
`broadcast(df)` hint. Use it when joining a large fact table to a small dimension table (e.g., a lookup/
reference table) to avoid an expensive shuffle-sort-merge join. Watch out for driver/executor OOM if you
force-broadcast something larger than expected.

**Q5: What is data skew and how do you fix it?**
A: Skew is when a small number of partition keys hold a disproportionate share of data (e.g., one
`customer_id` with millions of rows), causing a few tasks to run far longer than others and stalling the
whole stage. Fixes: salting the skewed key (append a random suffix, join, then aggregate/strip the
salt), enabling Adaptive Query Execution (AQE) with `spark.sql.adaptive.skewJoin.enabled=true` (Spark 3+
auto-splits skewed partitions), isolating and handling the hot key separately (filter it out, process
separately, union back), or repartitioning with a better key.

**Q6: Explain Spark's Catalyst optimizer and Tungsten engine at a high level.**
A: Catalyst is the query optimizer that converts DataFrame/SQL operations into a logical plan, applies
rule-based optimizations (predicate pushdown, constant folding, projection pruning) and cost-based
optimization, then generates a physical plan. Tungsten is the execution engine that manages memory
off-heap in binary format and does whole-stage code generation (compiling multiple operators into a
single JVM bytecode function) to avoid virtual function call/boxing overhead — this is why DataFrame/SQL
API outperforms RDD API for the same logic.

**Q7: `cache()` vs `persist()` vs checkpointing — when to use each.**
A: `cache()` is `persist(MEMORY_AND_DISK)` by default — use it when a DataFrame is reused multiple times
(e.g., referenced in several downstream branches) to avoid recomputation. `persist(storageLevel)` lets you
choose MEMORY_ONLY, MEMORY_AND_DISK, DISK_ONLY, with `_SER` variants to save memory at CPU cost, and
`_2` variants for replication (fault tolerance). `checkpoint()` truncates lineage by writing data to
reliable storage (HDFS/GCS) — used for very long lineage chains (e.g., iterative algorithms) to avoid
stack overflow / huge recompute on failure, at the cost of an extra write+read.

**Q8: How do you handle small files problem in Spark/GCS output?**
A: Symptoms: thousands of tiny output files from over-partitioned writes, slowing downstream reads
(metadata overhead) and BigQuery load/external-table performance. Fixes: `coalesce(n)` before write to
reduce output partition count (cheaper than `repartition` since it avoids a full shuffle when reducing
partitions), tune `spark.sql.shuffle.partitions` for the actual data volume (default 200 is often wrong),
use adaptive execution (AQE coalesces post-shuffle partitions automatically), or compact files with a
periodic maintenance job.

**Q9: Repartition vs coalesce — difference and cost.**
A: `repartition(n)` does a full shuffle to create exactly `n` roughly-equal partitions — use it to increase
partitions or to fix skew by repartitioning on a better key. `coalesce(n)` merges existing partitions
without a full shuffle (only decreases partition count) — much cheaper, use it just before writing output
to reduce file count after a wide operation.

**Q10: How do you tune `spark.sql.shuffle.partitions` and executor sizing for a Dataproc job?**
A: Start from data volume: shuffle partitions should target ~128-200MB per partition post-shuffle
(too few → large partitions, OOM/spill; too many → task scheduling overhead, small files). With AQE
enabled (Spark 3.x default on recent Dataproc images), set an initial high value
(`spark.sql.adaptive.coalescePartitions.enabled=true`) and let Spark coalesce automatically. For executor
sizing: prefer several mid-sized executors (4-5 cores, ~16-20GB memory each) over few huge ones, to
balance parallelism with JVM GC overhead and avoid the "fat executor" HDFS/GCS-throughput bottleneck. See
[../dataproc/guide.md](../dataproc/guide.md) for the cluster-level side of this tuning.

**Q11: Explain `explain()`/physical plan reading — what do you look for?**
A: `df.explain(True)` (or `EXPLAIN FORMATTED` in SQL) shows parsed/analyzed/optimized logical plans and
the physical plan. Look for: `Exchange` nodes (shuffles — count and justify each one), `BroadcastHashJoin`
vs `SortMergeJoin` (confirm small-table broadcasting happened as expected), `PushedFilters` (confirm
predicate pushdown reached the source, e.g., Parquet/BigQuery connector), `*(n) WholeStageCodegen` markers,
and scan node partition/file counts to catch unexpected full scans.

**Q12: How do you implement incremental/CDC processing in PySpark reading from BigQuery or GCS?**
A: Pattern: track a high-watermark (max `updated_at`/`ingestion_timestamp` or a GCS "processed manifest")
in a control table; each run reads only new/changed partitions (`WHERE updated_at > :watermark` pushed down
to BigQuery, or GCS prefix filtering by date partition); write results with a MERGE/upsert into BigQuery
or Iceberg table (see [../apache_iceberg/guide.md](../apache_iceberg/guide.md)) keyed on business key,
handling late-arriving data within the window; update the watermark only after successful commit
(idempotent, re-runnable on failure).

**Q13: How do you write unit tests for PySpark transformation logic?**
A: Use a local/session-scoped `SparkSession` fixture (`pyspark.testing` or `chispa` for DataFrame
equality assertions), create small literal input DataFrames (`spark.createDataFrame`), run the
transformation function, and assert on the output schema and rows (`assertDataFrameEqual`), ignoring row
order where appropriate. Keep transformation functions pure (DataFrame in → DataFrame out) so they don't
need a real cluster or external I/O to test.

**Q14: Live-coding style problem: Given a DataFrame of `(user_id, event_time, event_type)`, compute each
user's session count where a session ends after 30 minutes of inactivity.**
```python
from pyspark.sql import Window
from pyspark.sql import functions as F

w = Window.partitionBy("user_id").orderBy("event_time")
df = (df
    .withColumn("prev_time", F.lag("event_time").over(w))
    .withColumn("gap_min", (F.col("event_time").cast("long") - F.col("prev_time").cast("long")) / 60)
    .withColumn("new_session", F.when((F.col("gap_min").isNull()) | (F.col("gap_min") > 30), 1).otherwise(0))
    .withColumn("session_id", F.sum("new_session").over(w))
)
session_counts = df.groupBy("user_id").agg(F.countDistinct("session_id").alias("num_sessions"))
```
Talk through: window function choice, why `sum` over an indicator column gives a running session id,
handling ties in `event_time` (secondary sort key), and performance (this requires a shuffle+sort on
`user_id` — fine for moderate cardinality, consider pre-partitioning upstream for very high volume).

**Q15: How would you migrate a PySpark batch job to handle streaming with Structured Streaming, and what
changes?**
A: Swap batch `read` for `readStream` (e.g., reading from Pub/Sub via a connector, or Kafka — see
[../pubsub/guide.md](../pubsub/guide.md)), define watermarking (`withWatermark`) for event-time
aggregations to bound state size, choose output mode (append/update/complete) based on whether
aggregations are involved, and write with `writeStream` plus a checkpoint location (GCS) for
exactly-once-ish fault tolerance across restarts. Discuss trigger intervals (`processingTime`) vs
continuous processing, and that most GCP shops prefer Dataflow/Beam for true streaming (see
[../dataflow/guide.md](../dataflow/guide.md)) and reserve Spark Structured Streaming for teams
standardized on Spark/Dataproc.

**Q16: What's the difference between RDD, DataFrame, and Dataset APIs, and which do you default to?**
A: RDDs are low-level, untyped-at-compile-time-in-Python, distributed collections with no Catalyst
optimization — used today mainly for unstructured data or fine-grained control. DataFrames are
Catalyst-optimized, schema-aware, and the default for almost all production PySpark work (Python has no
compile-time Dataset API — Datasets are JVM/Scala-only typed DataFrames). Default to DataFrame/Spark SQL
API; drop to RDD only for custom partitioning logic or algorithms that don't map to relational operators.
