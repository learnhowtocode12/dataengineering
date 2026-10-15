# PySpark Coding Questions — Round 2 Drills

## Interview Guide
Expect either a live shared-editor PySpark exercise or a "whiteboard code, don't worry about perfect
syntax" style question. Narrate your approach before typing: which transformations, whether a shuffle is
involved, and how you'd validate the output. Interviewers care more about correct use of window
functions/joins and shuffle-awareness than memorized API syntax.

---

### Q1. Word count / log parsing (the classic warm-up)
```python
from pyspark.sql import functions as F

word_counts = (
    lines_df
    .select(F.explode(F.split(F.col("line"), r"\s+")).alias("word"))
    .groupBy("word")
    .count()
    .orderBy(F.desc("count"))
)
```
**Talk through:** `explode` turns one row into many (array → rows), `groupBy().count()` triggers a shuffle
— mention this is a `reduceByKey`-style aggregation under the hood, efficient because `count` is
associative/combinable (partial aggregation before shuffle).

---

### Q2. Deduplicate, keeping the latest row per key
```python
from pyspark.sql import Window
from pyspark.sql import functions as F

w = Window.partitionBy("id").orderBy(F.col("updated_at").desc())
deduped = (
    df.withColumn("rn", F.row_number().over(w))
      .filter(F.col("rn") == 1)
      .drop("rn")
)
```
**Follow-up:** "Why `row_number` over `rank`/`dense_rank` here?" → `row_number` guarantees exactly one row
per key even on exact ties, which is what dedup requires; `rank`/`dense_rank` would keep all tied rows.

---

### Q3. Top-N per group (window function)
```python
from pyspark.sql import Window
from pyspark.sql import functions as F

w = Window.partitionBy("category").orderBy(F.col("revenue").desc())
top_3 = (
    sales_df.groupBy("category", "product_id").agg(F.sum("revenue").alias("revenue"))
    .withColumn("rnk", F.dense_rank().over(w))
    .filter(F.col("rnk") <= 3)
)
```
**Follow-up:** discuss that this requires a full shuffle+sort by `category` — for very high-cardinality
categories, mention salting or pre-partitioning upstream to reduce skew.

---

### Q4. Sessionization (30-minute inactivity gap closes a session)
```python
from pyspark.sql import Window
from pyspark.sql import functions as F

w = Window.partitionBy("user_id").orderBy("event_time")
sessions = (
    df.withColumn("prev_time", F.lag("event_time").over(w))
      .withColumn(
          "gap_min",
          (F.col("event_time").cast("long") - F.col("prev_time").cast("long")) / 60,
      )
      .withColumn(
          "new_session",
          F.when(F.col("gap_min").isNull() | (F.col("gap_min") > 30), 1).otherwise(0),
      )
      .withColumn("session_id", F.sum("new_session").over(w))
)
```
**Why it works:** a running `sum` over a 0/1 "new session" indicator produces a monotonically increasing
session id per user — a very reusable trick worth memorizing cold.

---

### Q5. SCD Type 2 merge logic in PySpark (staging vs. current table)
**Problem:** Given `current` (existing dimension with `is_current` flag) and `staging` (today's full
snapshot), produce the rows to expire and the rows to insert.
```python
from pyspark.sql import functions as F

joined = current.alias("c").join(
    staging.alias("s"), on="business_key", how="full_outer"
)

# Rows whose tracked attributes changed -> expire the old version
to_expire = (
    joined.filter(
        F.col("c.is_current") & (F.col("c.attr_hash") != F.col("s.attr_hash"))
    )
    .select("c.*")
    .withColumn("is_current", F.lit(False))
    .withColumn("end_date", F.current_date())
)

# New business keys OR changed keys -> insert a fresh current version
to_insert = (
    joined.filter(F.col("c.business_key").isNull() | (F.col("c.attr_hash") != F.col("s.attr_hash")))
    .select("s.*")
    .withColumn("is_current", F.lit(True))
    .withColumn("start_date", F.current_date())
)

result = to_expire.unionByName(to_insert, allowMissingColumns=True)
```
**Talk through:** `attr_hash` is typically `F.md5(F.concat_ws("||", *tracked_cols))` computed on both
sides — this mirrors the exact MD5-hash change-detection pattern used in Informatica PowerCenter (see
[../informatica_powercenter/coding](../informatica_powercenter/coding.md) Q3),
a great bridge to mention live in an interview.

---

### Q6. Fixing a skewed join via salting
**Problem:** `fact` has a few `customer_id`s with millions of rows; a plain join against `dim_customer` is
slow because of skew.
```python
from pyspark.sql import functions as F

N = 10  # number of salt buckets
fact_salted = fact.withColumn("salt", (F.rand() * N).cast("int"))
dim_salted = dim_customer.withColumn(
    "salt", F.explode(F.array([F.lit(i) for i in range(N)]))
)

joined = fact_salted.join(
    dim_salted, on=["customer_id", "salt"]
).drop("salt")
```
**Talk through:** spreading the hot key's rows across `N` synthetic buckets on the large side, and
exploding the small side to match every bucket, turns one overloaded partition into `N` balanced ones.
Mention AQE's automatic skew-join handling (`spark.sql.adaptive.skewJoin.enabled`) as the "let Spark do it
for you" alternative in Spark 3+.

---

### Q7. pandas UDF vs. row-at-a-time UDF — show the difference
```python
from pyspark.sql.functions import pandas_udf
import pandas as pd

# Row-at-a-time (slow: Python process round-trip per row)
@F.udf("double")
def celsius_to_f_row(c):
    return c * 9 / 5 + 32

# Vectorized pandas UDF (fast: Arrow-batched, operates on a pandas Series)
@pandas_udf("double")
def celsius_to_f_vec(c: pd.Series) -> pd.Series:
    return c * 9 / 5 + 32
```
**Talk through:** the pandas UDF receives a whole batch as a `pandas.Series` (Arrow-serialized), avoiding
per-row Python call overhead — always prefer native Spark SQL functions first, pandas UDFs second, row
UDFs last.

---

### Q8. Find missing dates per key (gap detection in a time series)
```python
from pyspark.sql import functions as F

date_bounds = df.groupBy("sensor_id").agg(
    F.min("event_date").alias("min_d"), F.max("event_date").alias("max_d")
)
all_dates = date_bounds.select(
    "sensor_id", F.explode(F.sequence("min_d", "max_d")).alias("event_date")
)
missing = all_dates.join(df, on=["sensor_id", "event_date"], how="left_anti")
```
**Talk through:** `F.sequence` generates the full expected date range per key; `left_anti` join returns
rows present in the expected set but absent from the actual data — a very common data-quality check.

---

### Q9. Exploding nested JSON (array of structs) for a flat BigQuery table
```python
from pyspark.sql import functions as F

flat = (
    orders_df
    .select(
        "order_id",
        "customer_id",
        F.explode("line_items").alias("item"),
    )
    .select(
        "order_id", "customer_id",
        F.col("item.sku").alias("sku"),
        F.col("item.qty").alias("qty"),
        F.col("item.price").alias("price"),
    )
)
```
**Follow-up:** "When would you *not* do this?" → when BigQuery consumers actually want the nested/repeated
structure preserved (see [../bigquery/guide](../bigquery/guide.md) Q4) — flattening is a query-pattern
decision, not a default.

---

### Q10. Unit test a PySpark transformation with pytest
```python
import pytest
from pyspark.sql import SparkSession

@pytest.fixture(scope="session")
def spark():
    return SparkSession.builder.master("local[2]").appName("test").getOrCreate()

def dedupe_latest(df):
    from pyspark.sql import Window
    from pyspark.sql import functions as F
    w = Window.partitionBy("id").orderBy(F.col("ts").desc())
    return df.withColumn("rn", F.row_number().over(w)).filter("rn = 1").drop("rn")

def test_dedupe_latest(spark):
    data = [(1, 100, "a"), (1, 200, "b"), (2, 50, "c")]
    df = spark.createDataFrame(data, ["id", "ts", "val"])
    result = dedupe_latest(df).orderBy("id").collect()
    assert [(r.id, r.val) for r in result] == [(1, "b"), (2, "c")]
```
**Talk through:** keep the transformation a pure function (DataFrame in → DataFrame out), use a cheap
local `SparkSession` fixture, and assert on collected rows for small test data — no cluster needed.

---

### Q11. Pivot long-format data to wide
```python
pivoted = (
    sales_long.groupBy("store_id")
    .pivot("month", ["Jan", "Feb", "Mar"])  # explicit values avoid a second scan to discover them
    .agg(F.sum("revenue"))
)
```
**Talk through:** always pass explicit pivot values in production — without them, Spark runs an extra job
just to discover distinct values before pivoting, doubling the scan cost on a large table.

---

### Q12. Debug exercise: this job keeps spilling to disk / running out of memory — what do you check?
**Prompt given verbally:** "Here's a PySpark job joining a 2TB fact table with a 500MB dimension table,
then doing a `groupBy` with 300 Spark partitions configured, and it's spilling heavily." Walk through the
diagnosis out loud:
1. Is the 500MB dimension table being broadcast? If not, force it: `F.broadcast(dim_df)` — avoids a
   shuffle-sort-merge join entirely for the join step.
2. Is `spark.sql.shuffle.partitions=300` appropriate for 2TB? Target ~128-200MB per post-shuffle
   partition — 2TB / 200MB ≈ 10,000 partitions, so 300 is almost certainly too few, causing huge
   partitions that spill.
3. Check `explain()` for `Exchange` nodes and confirm `BroadcastHashJoin` is actually chosen, not
   `SortMergeJoin`.
4. Check for skew on the `groupBy` key specifically (a few keys dominating) — AQE skew handling or salting
   if so.
This is as much a "do you reason like an engineer out loud" test as a coding test — narrate the checklist.
