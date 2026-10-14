# SQL / BigQuery Coding Questions — Round 1 / Round 2 Drills

## Interview Guide
SQL is graded on **correctness, readability, and whether you reach for the right window function instead
of a convoluted self-join**. Expect to write GoogleSQL (BigQuery's dialect) in a shared editor or on a
doc. State assumptions about nulls/duplicates before writing, and narrate the logic as you type. For 6
YOE, at least one question will also ask you to *optimize* an existing slow query, not just write a new
one — that's the differentiating question (Q13).

---

### Q1. Nth highest value (e.g., 2nd highest salary per department)
```sql
WITH ranked AS (
  SELECT
    department,
    employee_id,
    salary,
    DENSE_RANK() OVER (PARTITION BY department ORDER BY salary DESC) AS rnk
  FROM employees
)
SELECT department, employee_id, salary
FROM ranked
WHERE rnk = 2;
```
**Talk through:** `DENSE_RANK` (not `ROW_NUMBER`) so genuine ties both count as "2nd highest" rather than
arbitrarily picking one — state this assumption explicitly, since "what counts as 2nd" is ambiguous without
it.

---

### Q2. Running total / cumulative sum
```sql
SELECT
  order_date,
  daily_revenue,
  SUM(daily_revenue) OVER (ORDER BY order_date
                           ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS running_total
FROM daily_sales;
```

---

### Q3. Year-over-year growth percentage
```sql
WITH yearly AS (
  SELECT EXTRACT(YEAR FROM order_date) AS yr, SUM(revenue) AS total_revenue
  FROM orders
  GROUP BY yr
)
SELECT
  yr,
  total_revenue,
  LAG(total_revenue) OVER (ORDER BY yr) AS prev_year_revenue,
  SAFE_DIVIDE(
    total_revenue - LAG(total_revenue) OVER (ORDER BY yr),
    LAG(total_revenue) OVER (ORDER BY yr)
  ) * 100 AS yoy_growth_pct
FROM yearly
ORDER BY yr;
```
**Talk through:** `SAFE_DIVIDE` instead of `/` avoids a divide-by-zero runtime error on the first year
(where `LAG` is NULL) — a small detail that signals production-mindedness.

---

### Q4. Consecutive login days (classic "gaps and islands" problem)
```sql
WITH numbered AS (
  SELECT
    user_id,
    login_date,
    DATE_SUB(login_date, INTERVAL ROW_NUMBER() OVER (
      PARTITION BY user_id ORDER BY login_date
    ) DAY) AS grp
  FROM logins
)
SELECT user_id, grp, COUNT(*) AS consecutive_days, MIN(login_date) AS streak_start, MAX(login_date) AS streak_end
FROM numbered
GROUP BY user_id, grp
ORDER BY user_id, streak_start;
```
**Talk through:** subtracting a sequential row number (in days) from the actual date produces a constant
value for every row inside one unbroken streak — this "island grouping" trick is worth memorizing, it
reappears constantly (sessionization, streaks, consecutive-anything problems).

---

### Q5. Top N per category
```sql
WITH ranked AS (
  SELECT
    category, product_id, SUM(revenue) AS total_revenue,
    RANK() OVER (PARTITION BY category ORDER BY SUM(revenue) DESC) AS rnk
  FROM sales
  GROUP BY category, product_id
)
SELECT category, product_id, total_revenue
FROM ranked
WHERE rnk <= 3;
```
**Follow-up:** explain `RANK` vs `DENSE_RANK` vs `ROW_NUMBER` tie-handling differences clearly — this is
one of the most commonly asked clarifying follow-ups.

---

### Q6. Deduplicate, keeping the most recent record
```sql
SELECT * EXCEPT(rn) FROM (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY id ORDER BY updated_at DESC) AS rn
  FROM staging_table
)
WHERE rn = 1;
```
**Talk through:** `SELECT * EXCEPT(rn)` is BigQuery-specific syntax worth knowing — cleaner than listing
every column manually.

---

### Q7. Pivot rows to columns
```sql
SELECT
  store_id,
  SUM(IF(month = 'Jan', revenue, 0)) AS jan,
  SUM(IF(month = 'Feb', revenue, 0)) AS feb,
  SUM(IF(month = 'Mar', revenue, 0)) AS mar
FROM sales_long
GROUP BY store_id;
-- Or, using BigQuery's native PIVOT:
SELECT * FROM sales_long
PIVOT (SUM(revenue) FOR month IN ('Jan', 'Feb', 'Mar'));
```

---

### Q8. Employee-manager hierarchy (recursive CTE)
```sql
WITH RECURSIVE org_chart AS (
  SELECT employee_id, manager_id, name, 1 AS level
  FROM employees
  WHERE manager_id IS NULL  -- the root/CEO
  UNION ALL
  SELECT e.employee_id, e.manager_id, e.name, oc.level + 1
  FROM employees e
  JOIN org_chart oc ON e.manager_id = oc.employee_id
)
SELECT * FROM org_chart ORDER BY level;
```
**Note:** BigQuery added recursive CTE support — mention that older/alternative approaches used
`GENERATE_ARRAY` tricks or exporting to Dataproc/Spark GraphX-style processing for deep hierarchies before
that; show awareness that this is a relatively newer capability.

---

### Q9. Sessionization in pure SQL
```sql
WITH gaps AS (
  SELECT
    user_id,
    event_time,
    TIMESTAMP_DIFF(
      event_time,
      LAG(event_time) OVER (PARTITION BY user_id ORDER BY event_time),
      MINUTE
    ) AS gap_min
  FROM events
),
sessions AS (
  SELECT
    user_id, event_time,
    SUM(CASE WHEN gap_min IS NULL OR gap_min > 30 THEN 1 ELSE 0 END)
      OVER (PARTITION BY user_id ORDER BY event_time) AS session_id
  FROM gaps
)
SELECT user_id, session_id, COUNT(*) AS events_in_session
FROM sessions
GROUP BY user_id, session_id;
```

---

### Q10. Funnel conversion analysis
```sql
WITH steps AS (
  SELECT
    user_id,
    MAX(IF(event_name = 'view_product', 1, 0)) AS did_view,
    MAX(IF(event_name = 'add_to_cart', 1, 0)) AS did_cart,
    MAX(IF(event_name = 'purchase', 1, 0)) AS did_purchase
  FROM events
  GROUP BY user_id
)
SELECT
  SUM(did_view) AS viewed,
  SUM(did_cart) AS carted,
  SUM(did_purchase) AS purchased,
  SAFE_DIVIDE(SUM(did_cart), SUM(did_view)) * 100 AS view_to_cart_pct,
  SAFE_DIVIDE(SUM(did_purchase), SUM(did_cart)) * 100 AS cart_to_purchase_pct
FROM steps;
```
**Follow-up:** "What if order matters (must view before cart before purchase)?" → use `MIN(IF(...,
event_time, NULL))` per step and compare timestamps instead of just presence/absence.

---

### Q11. Find missing IDs in a sequence
```sql
WITH bounds AS (SELECT MIN(id) AS min_id, MAX(id) AS max_id FROM my_table),
full_range AS (
  SELECT id FROM bounds, UNNEST(GENERATE_ARRAY(min_id, max_id)) AS id
)
SELECT f.id AS missing_id
FROM full_range f
LEFT JOIN my_table t ON f.id = t.id
WHERE t.id IS NULL;
```

---

### Q12. Cohort retention analysis
```sql
WITH first_seen AS (
  SELECT user_id, MIN(DATE_TRUNC(event_date, MONTH)) AS cohort_month
  FROM events
  GROUP BY user_id
),
activity AS (
  SELECT
    e.user_id,
    f.cohort_month,
    DATE_DIFF(DATE_TRUNC(e.event_date, MONTH), f.cohort_month, MONTH) AS month_number
  FROM events e
  JOIN first_seen f USING (user_id)
)
SELECT
  cohort_month,
  month_number,
  COUNT(DISTINCT user_id) AS active_users
FROM activity
GROUP BY cohort_month, month_number
ORDER BY cohort_month, month_number;
```

---

### Q13. Query optimization exercise — "this query is slow and expensive, fix it"
**Given (slow):**
```sql
SELECT *
FROM `project.dataset.events`
WHERE DATE(event_timestamp) = '2026-10-01'
  AND user_id IN (SELECT user_id FROM `project.dataset.flagged_users`)
ORDER BY event_timestamp;
```
**Issues to call out, then the fix:**
1. `SELECT *` scans every column, even unused ones — list only needed columns.
2. `DATE(event_timestamp) = '2026-10-01'` wraps the partitioning column in a function, which can defeat
   partition pruning — rewrite as a direct range filter on the raw column.
3. `user_id IN (subquery)` can be rewritten as a `JOIN`, which the optimizer plans more predictably at
   scale than a large `IN` subquery.
4. An `ORDER BY` with no `LIMIT` forces a full sort of the entire result set — confirm whether the caller
   actually needs global ordering or just wants a sample.
```sql
SELECT event_id, user_id, event_type, event_timestamp
FROM `project.dataset.events`
WHERE event_timestamp >= TIMESTAMP('2026-10-01')
  AND event_timestamp <  TIMESTAMP('2026-10-02')
  AND EXISTS (
    SELECT 1 FROM `project.dataset.flagged_users` f WHERE f.user_id = events.user_id
  )
ORDER BY event_timestamp;
```

---

### Q14. Write a MERGE (upsert) statement
```sql
MERGE INTO `project.dataset.dim_customer` T
USING `project.dataset.stg_customer` S
ON T.customer_id = S.customer_id
WHEN MATCHED AND S.updated_at > T.updated_at THEN
  UPDATE SET T.name = S.name, T.email = S.email, T.updated_at = S.updated_at
WHEN NOT MATCHED THEN
  INSERT (customer_id, name, email, updated_at)
  VALUES (S.customer_id, S.name, S.email, S.updated_at);
```

---

### Q15. Approximate distinct counts at scale
```sql
SELECT
  event_date,
  APPROX_COUNT_DISTINCT(user_id) AS approx_dau
FROM events
GROUP BY event_date;

-- Persisting HLL sketches to merge across days without re-scanning history:
SELECT event_date, HLL_COUNT.INIT(user_id) AS sketch
FROM events
GROUP BY event_date;

SELECT HLL_COUNT.MERGE(sketch) AS rolling_distinct_users
FROM daily_sketches
WHERE event_date BETWEEN '2026-10-01' AND '2026-10-07';
```
**Talk through:** exact `COUNT(DISTINCT ...)` over billions of rows is expensive; HLL sketches trade a
small, bounded error for the ability to merge pre-aggregated sketches across days/partitions without
re-scanning raw history — directly reusable from [guide.md](guide.md) Q16.
