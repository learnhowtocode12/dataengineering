# Core SQL Concepts — Interview Guide & Q&A
> **Round mapping:** R1 (coding screen) & R2 (deep dive) — these are dialect-agnostic fundamentals asked
> regardless of warehouse. For BigQuery-specific SQL (partitioning, MERGE, APPROX functions), see
> [../bigquery/guide](../bigquery/guide.md). Hands-on drills:
> [coding](coding.md).

## Interview Guide
Every SQL-heavy interview loop includes a handful of **fundamentals questions that have nothing to do with
BigQuery specifically** — joins, normalization, transactions, indexing, execution plans. These get asked
because they reveal whether you understand *how a database actually works* underneath the dialect you use
daily. At 6+ years, you should be able to explain not just the definition but *why* a given concept exists
and what breaks without it — and be honest about which parts (stored procedures, index tuning on an OLTP
engine) you have less day-to-day exposure to if your recent experience has been warehouse-centric.

---

## Q&A

**Q1: Explain the types of SQL joins with a one-line use case for each.**

**Answer:** **INNER JOIN** — only rows matching in both tables (e.g., orders that have a valid customer).
**LEFT/RIGHT OUTER JOIN** — all rows from one side plus matches from the other, NULLs where no match
(e.g., all customers, with their orders if any, to find customers with zero orders). **FULL OUTER JOIN** —
all rows from both sides, NULLs on whichever side has no match (e.g., reconciling two systems' records to
find mismatches on either side). **CROSS JOIN** — every combination of rows from both tables (Cartesian
product; e.g., generating all date × store combinations before left-joining actual sales to find gaps).
**SELF JOIN** — a table joined to itself (e.g., employee-to-manager, both rows from the `employees`
table).

**Q2: WHERE vs. HAVING — what's the actual difference?**

**Answer:** `WHERE` filters rows **before** grouping/aggregation (operates on raw rows, can't reference an
aggregate function). `HAVING` filters groups **after** aggregation (operates on the grouped/aggregated
result, so it can reference `SUM()`, `COUNT()`, etc.). A common mistake is trying to filter on an aggregate
in `WHERE` — that's precisely the case `HAVING` exists for.

**Q3: What are the normal forms (1NF, 2NF, 3NF), and when would you deliberately break them?**

**Answer:** **1NF** — atomic column values, no repeating groups/arrays in a single column. **2NF** — 1NF plus every
non-key column depends on the *whole* primary key (relevant for composite keys — no partial dependency).
**3NF** — 2NF plus no non-key column depends on another non-key column (no transitive dependency). These
rules exist to eliminate update/insert/delete anomalies in **OLTP** systems. In **OLAP/analytics warehouses
(BigQuery)**, you deliberately denormalize (star schemas, nested/repeated fields) because join cost at
scale matters more than storage-normalization purity — explicitly connect this to
[../bigquery/guide](../bigquery/guide.md) Q4 to show you understand *why* the two worlds optimize
differently, not just that they do.

**Q4: Explain the ACID properties with a concrete example each.**

**Answer:** **Atomicity** — a transaction's operations all succeed or all roll back together (a funds transfer
debiting one account and crediting another either both happen or neither does). **Consistency** — a
transaction moves the database from one valid state to another, respecting constraints (a check constraint
preventing a negative balance can never be violated even mid-transaction-commit). **Isolation** —
concurrent transactions don't see each other's uncommitted intermediate state (two people booking the last
seat shouldn't both succeed). **Durability** — once committed, data survives a crash (written to durable
storage/WAL, not just memory).

**Q5: What are the transaction isolation levels, and what anomaly does each prevent?**

**Answer:** From weakest to strongest: **Read Uncommitted** — allows **dirty reads** (seeing another transaction's
uncommitted changes). **Read Committed** — prevents dirty reads, but allows **non-repeatable reads**
(re-reading the same row within a transaction can see a different value if another transaction committed a
change in between). **Repeatable Read** — prevents non-repeatable reads, but can still allow **phantom
reads** (a repeated range query can return new rows inserted by another transaction). **Serializable** —
prevents all of the above by making concurrent transactions behave as if they ran one at a time (at the
cost of the most locking/contention). Higher isolation = more correctness guarantees but less concurrency.

**Q6: How do indexes work, and when can an index make things slower?**

**Answer:** Most indexes are a **B-tree** — a sorted structure letting the engine binary-search/seek to matching
rows instead of scanning every row (a **table scan**), dramatically speeding up selective `WHERE`/`JOIN`/
`ORDER BY` lookups. The cost: every `INSERT`/`UPDATE`/`DELETE` must also update every index on that table,
so **write-heavy** tables with many indexes pay a real write-amplification cost, and an index on a
**low-selectivity** column (e.g., a boolean flag where 95% of rows are the same value) often isn't worth
it since the optimizer may just table-scan anyway. A **covering index** (includes all columns a query
needs) lets the engine satisfy a query from the index alone, never touching the underlying table — the
fastest case.

**Q7: How do you read a query execution plan, and what are you looking for?**

**Answer:** Look at whether the plan shows a **table scan** (reads every row — fine for a small table, a red flag
on a huge one) versus an **index seek/scan** (uses an index to jump to relevant rows), the **join
algorithm** chosen (nested loop — good for small outer input; hash join — good for large unsorted inputs;
merge join — good when both sides are already sorted on the join key), and the **estimated vs. actual row
counts** at each step (a big mismatch usually means stale statistics, causing the optimizer to pick a bad
plan). This is the general-SQL version of the BigQuery-specific `explain()`/execution-details reading
covered in [../bigquery/guide](../bigquery/guide.md) Q8 and
[../pyspark/guide](../pyspark/guide.md) Q11 for Spark.

**Q8: CTE vs. subquery vs. temp table vs. view vs. materialized view — when do you use each?**

**Answer:** A **CTE** (`WITH x AS (...)`) improves readability for a multi-step query and can be referenced multiple
times within the same statement, but most engines don't cache/materialize it (re-evaluated per reference
unless the optimizer decides otherwise). A **subquery** is similar but less readable for complex nesting.
A **temp table** physically materializes intermediate results — worth it when the same intermediate result
is reused across multiple separate statements/steps in a session. A **view** is a saved, reusable query
definition (always runs live against current data — no storage of results). A **materialized view**
physically stores the result and refreshes on a schedule/trigger — use it when the same expensive
aggregation is queried repeatedly and slightly-stale data is acceptable (same concept as
[../looker/guide](../looker/guide.md) Q3 PDTs and [../bigquery/guide](../bigquery/guide.md) Q14
BigQuery materialized views — same idea, different product).

**Q9: Explain window functions — how is `OVER (PARTITION BY ... ORDER BY ...)` different from `GROUP BY`?**

**Answer:** `GROUP BY` collapses multiple rows into one row per group, losing row-level detail. A window function
computes an aggregate/ranking **per row**, within a "window" defined by `PARTITION BY` (like a `GROUP BY`
key, but rows aren't collapsed) and optionally ordered/framed (`ROWS BETWEEN ... AND ...` /
`RANGE BETWEEN ...`), so you keep every original row *and* get the aggregate alongside it — essential for
running totals, rankings, and row-to-row comparisons (`LAG`/`LEAD`) that a plain `GROUP BY` can't express.

**Q10: Explain NULL's three-valued logic and a common bug it causes.**

**Answer:** SQL has three truth values: `TRUE`, `FALSE`, and `UNKNOWN` (any comparison involving `NULL` evaluates to
`UNKNOWN`, not `TRUE`/`FALSE`). This is why `WHERE col != NULL` or `col = NULL` never matches anything —
you need `IS NULL`/`IS NOT NULL`. It also silently affects `NOT IN` subqueries: `WHERE id NOT IN (SELECT
id FROM t)` returns **zero rows** if that subquery's result contains even one `NULL`, because every
comparison against that `NULL` is `UNKNOWN`, not `TRUE` — a classic, easy-to-miss production bug. Use
`COALESCE`/`NULLIF` to handle defaults explicitly, and prefer `NOT EXISTS` over `NOT IN` when the subquery
could contain NULLs.

**Q11: UNION vs. UNION ALL, and why does it matter for performance?**

**Answer:** `UNION` deduplicates the combined result (requires an implicit sort/hash-distinct step — real cost on
large result sets); `UNION ALL` just concatenates without deduping (cheaper). Default to `UNION ALL`
whenever you already know the two result sets can't overlap, or duplicates are acceptable/desired —
reaching for `UNION` out of habit on large queries is a common unnecessary-cost mistake.

**Q12: Where do stored procedures/triggers fit in a modern cloud-warehouse-centric data stack?**

**Answer:** They're still common in OLTP application databases (enforcing business rules close to the data,
auditing via triggers), but in a modern ELT/warehouse-centric pipeline, most transformation logic is
deliberately kept **out** of triggers/procedures and instead lives in version-controlled,
testable/orchestrated code (dbt models, Airflow-orchestrated SQL/PySpark) — because trigger logic is
invisible to anyone not specifically looking inside the database, hard to unit test, and easy to
accidentally create cascading/recursive side effects with. Being able to articulate *why* the industry
moved away from heavy trigger/procedure logic (not just that it did) is the senior-level signal here.

**Q13: SQL vs. NoSQL — how do you frame the decision?** *(cross-reference)*

**Answer:** See [../gcp_fundamentals/guide](../gcp_fundamentals/guide.md) Q1 for the GCP-specific service comparison (BigQuery vs.
Bigtable vs. Spanner vs. Firestore) — the general framing: choose SQL/relational when you need strong
consistency, complex multi-table joins/ad hoc querying, and well-understood schema; choose NoSQL when you
need flexible/evolving schema, massive horizontal scale with simple access patterns (key-value, wide-row
time series), or latency profiles relational engines struggle with at that scale.

**Q14: What causes a deadlock, and how do you avoid one in application code?**

**Answer:** A deadlock happens when two transactions each hold a lock the other needs (Transaction A holds a lock
on row 1 and wants row 2; Transaction B holds a lock on row 2 and wants row 1) — neither can proceed, and
the database detects this and kills one as a "deadlock victim." Avoidance: always acquire locks/update rows
in a **consistent order** across all code paths (e.g., always update the lower primary key first), keep
transactions short, and add application-level retry logic for the specific deadlock error code rather than
treating it as a fatal error.

**Q15: Correlated vs. non-correlated subquery — what's the performance implication?**

**Answer:** A **non-correlated** subquery runs once, independent of the outer query, and its result can be reused.
A **correlated** subquery references a column from the outer query, so conceptually it re-runs once **per
outer row** — if not optimized (rewritten as a join) by the engine, this can be far slower on large tables.
Modern optimizers often rewrite simple correlated subqueries into joins automatically, but it's still worth
knowing how to manually rewrite one into an explicit `JOIN` or `EXISTS` form if you suspect the optimizer
isn't doing it for you.

**Q16: `GROUP BY` with `ROLLUP`/`CUBE` — what do they add over plain `GROUP BY`?**

**Answer:** `ROLLUP(a, b)` produces the normal per-`(a,b)` group rows **plus** subtotal rows for each `a` and a grand
total row — useful for hierarchical subtotal reports (e.g., sales by region and store, plus a region
subtotal and a grand total) without a separate `UNION` of three different aggregation queries. `CUBE(a, b)`
goes further and produces subtotals for **every combination** of the grouping columns, not just the
hierarchical rollup order.
