# Informatica PowerCenter Expression & Migration Coding Questions — Round 2 Drills

## Interview Guide
Informatica PowerCenter is low-code, so "coding" here means **Expression Language snippets, SQL
overrides, and — the highest-value exercise for this specific role — translating a described mapping into
equivalent PySpark or BigQuery SQL.** That last category is the single best way to demonstrate the
Informatica→GCP migration narrative live, so spend the most practice time there. See
[../informatica_cloud/coding.md](../informatica_cloud/coding.md) for the IICS-side parameterization
equivalent.

---

### Q1. Conditional logic: `IIF`/`DECODE` equivalents
**Problem:** Classify an order as `HIGH`, `MEDIUM`, or `LOW` value in an Expression transformation.
```
-- IIF (nested, like a ternary chain)
IIF(ORDER_TOTAL > 1000, 'HIGH',
  IIF(ORDER_TOTAL > 100, 'MEDIUM', 'LOW'))

-- DECODE (more readable for many discrete branches)
DECODE(TRUE,
  ORDER_TOTAL > 1000, 'HIGH',
  ORDER_TOTAL > 100,  'MEDIUM',
  'LOW')
```
**Talk through:** `DECODE(TRUE, cond1, val1, cond2, val2, default)` is PowerCenter's way of expressing a
`CASE WHEN` chain — call out the direct SQL equivalent (`CASE WHEN ... END`) to show you can translate it.

---

### Q2. NULL handling / default substitution
```
IIF(ISNULL(CUSTOMER_EMAIL), 'unknown@example.com', CUSTOMER_EMAIL)
-- or, for numeric defaults:
IIF(ISNULL(DISCOUNT_PCT), 0, DISCOUNT_PCT)
```
**SQL equivalent (for the migration conversation):** `COALESCE(customer_email, 'unknown@example.com')`.

---

### Q3. SCD Type 2 change detection via hash comparison (the classic PowerCenter pattern)
```
-- In an Expression transformation, computed on the staging (incoming) side:
NEW_HASH = MD5(
  TO_CHAR(FIRST_NAME) || '|' ||
  TO_CHAR(LAST_NAME)  || '|' ||
  TO_CHAR(ADDRESS)    || '|' ||
  TO_CHAR(PHONE)
)

-- After a Lookup against the current dimension row, compare:
IIF(ISNULL(LKP_CURRENT_HASH) , 'INSERT',
  IIF(LKP_CURRENT_HASH != NEW_HASH, 'EXPIRE_AND_INSERT', 'NO_CHANGE'))
```
**Why this is a great interview answer:** hashing every tracked column into one value and comparing it
against the stored hash on the current row avoids writing a brittle column-by-column `!=` chain for every
tracked attribute, and it's exactly the same pattern used for the `attr_hash` column in the PySpark SCD2
merge (see [../pyspark/coding.md](../pyspark/coding.md) Q5) — explicitly draw that connection in the
interview, it's a strong signal.

---

### Q4. Unconnected Lookup call from an Expression
```
:LKP.lkp_get_exchange_rate(CURRENCY_CODE, TRANSACTION_DATE)
```
**Talk through:** called like a function, only evaluated for rows that actually reach this expression
branch (e.g., inside an `IIF` so it's skipped for domestic-currency rows) — cheaper than a connected Lookup
that runs for every row regardless of whether it's needed.

---

### Q5. Source Qualifier SQL override to push down filtering/joins
```sql
-- Source Qualifier override (replaces the default "SELECT * FROM table"):
SELECT o.order_id, o.customer_id, o.order_total, c.region
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_date >= TRUNC(SYSDATE) - 1
```
**Talk through:** pushing the join and date filter into the source database via SQL override means the
database's own optimizer (with its indexes) does the filtering, instead of pulling the full `orders` table
across the network into PowerCenter and filtering row-by-row in the engine — this is manual pushdown,
distinct from automatic Pushdown Optimization (PDO), and useful when PDO can't cover the full mapping.

---

### Q6. Full translation exercise: PowerCenter mapping → PySpark
**Given mapping (described, as it would be in an interview):** `Source Qualifier (orders table, filtered
to yesterday) → Lookup (customer region, unconnected) → Expression (compute order_value_tier via DECODE)
→ Router (split HIGH tier to one target, rest to another) → Update Strategy (insert new, update changed
by a Type 1 SCD rule) → Target (dim_order_summary)`.

**PySpark translation:**
```python
from pyspark.sql import functions as F

orders = (
    spark.read.format("bigquery").option("table", "proj.raw.orders").load()
    .filter(F.col("order_date") == F.date_sub(F.current_date(), 1))
)

customers = spark.read.format("bigquery").option("table", "proj.raw.customers").load()

# Lookup -> broadcast join (customers is small; avoids a shuffle, mirrors the unconnected Lookup intent)
enriched = orders.join(F.broadcast(customers.select("customer_id", "region")), "customer_id", "left")

# Expression (DECODE) -> CASE WHEN equivalent
tiered = enriched.withColumn(
    "order_value_tier",
    F.when(F.col("order_total") > 1000, "HIGH")
     .when(F.col("order_total") > 100, "MEDIUM")
     .otherwise("LOW"),
)

# Router -> filter into two DataFrames
high_tier = tiered.filter(F.col("order_value_tier") == "HIGH")
other_tier = tiered.filter(F.col("order_value_tier") != "HIGH")

# Update Strategy (Type 1) -> MERGE on write, not expressible purely in Spark - write to staging,
# then run a BigQuery MERGE (see Q7) as the actual upsert step.
tiered.write.format("bigquery").option("table", "proj.staging.order_summary_stg").mode("overwrite").save()
```
**Talk through out loud:** the Lookup becomes a broadcast join (small side), Router becomes a `filter`
branch, and — critically — the PowerCenter "Update Strategy" DML behavior doesn't have a direct Spark
equivalent, so it's pushed down into a BigQuery `MERGE` step after landing to staging (next question).
Narrating *why* each piece maps the way it does is worth more than the code itself here.

---

### Q7. Same mapping's Update Strategy → BigQuery MERGE
```sql
MERGE INTO `proj.curated.dim_order_summary` T
USING `proj.staging.order_summary_stg` S
ON T.order_id = S.order_id
WHEN MATCHED THEN
  UPDATE SET T.order_value_tier = S.order_value_tier, T.region = S.region
WHEN NOT MATCHED THEN
  INSERT (order_id, customer_id, order_total, region, order_value_tier)
  VALUES (S.order_id, S.customer_id, S.order_total, S.region, S.order_value_tier);
```
**Talk through:** this completes the translation — SQL-expressible DML logic (Update Strategy) lands in
BigQuery as a `MERGE`, while the row-level/procedural transformation logic (Expression, Router, Lookup)
runs in PySpark, exactly matching the triage framework from
[../informatica_cloud/guide.md](../informatica_cloud/guide.md) Q5.

---

### Q8. Debug exercise: Update Strategy is inserting duplicate rows
**Prompt:** "A mapping's Lookup is supposed to find the existing dimension row by `business_key`, but the
target is ending up with duplicate rows for the same key after each run. What's the likely bug?"
**Answer:** Almost always one of: (a) the Lookup condition matches on a non-unique key (e.g., missing a
secondary attribute, or the lookup source itself has duplicate business keys so "first matching row"
behavior picks inconsistently), or (b) the Lookup is configured to return no match when it should
(stale/cached lookup not refreshed, or a case-sensitivity/whitespace mismatch between source and lookup
key), causing the Update Strategy to mark every row `DD_INSERT` instead of `DD_UPDATE` for rows that
already exist. **Fix:** validate uniqueness on the lookup source's key first (`SELECT business_key, COUNT(*)
... HAVING COUNT(*) > 1`), then correct the Lookup condition/trim-and-case-normalize both sides of the
match.

---

### Q9. Reusable "data quality mapplet" pseudocode
```
Mapplet: mplt_dq_checks
  Input:  any row + a list of "required" column names
  Expression:
    IS_NULL_CHECK = IIF(ISNULL(REQUIRED_COL_1) OR ISNULL(REQUIRED_COL_2), 'REJECT', 'PASS')
    RANGE_CHECK   = IIF(AMOUNT < 0 OR AMOUNT > 1000000, 'REJECT', 'PASS')
  Router:
    Group "pass_group":   IS_NULL_CHECK = 'PASS' AND RANGE_CHECK = 'PASS'
    Group "reject_group": default (anything else)
  Output: pass_group -> continues to main mapping logic
          reject_group -> error/reject target table with rejection reason appended
```
**Talk through:** a single reusable mapplet standardizes null/range checks across every mapping that
includes it, instead of re-implementing the same checks by hand in each mapping — directly answers "how
did you ensure data quality across dozens of migrated pipelines" if asked in the managerial round.
