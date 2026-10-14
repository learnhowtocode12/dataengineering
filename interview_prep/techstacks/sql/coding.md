# General SQL Coding Questions — Round 1 Drills

## Interview Guide
These are the classic, dialect-agnostic SQL interview questions (ANSI/Postgres-style syntax) that show up
regardless of warehouse — distinct from the BigQuery-dialect problems in
[../bigquery/coding.md](../bigquery/coding.md). Expect these in a general
technical screen, sometimes before the interviewer even knows your warehouse background. State the schema/
assumptions out loud before writing the query.

---

### Q1. Second-highest salary (classic, without window functions — shows you know both ways)
```sql
SELECT MAX(salary) AS second_highest
FROM employees
WHERE salary < (SELECT MAX(salary) FROM employees);
```
**Follow-up:** "What if there are ties for highest?" → this correctly returns the next *distinct* value
below the max regardless of how many people share the max — walk through why that's correct.

---

### Q2. Employees who earn more than their manager (self-join)
```sql
SELECT e.employee_id, e.name, e.salary, m.salary AS manager_salary
FROM employees e
JOIN employees m ON e.manager_id = m.employee_id
WHERE e.salary > m.salary;
```

---

### Q3. Department with the highest average salary
```sql
SELECT department_id, AVG(salary) AS avg_salary
FROM employees
GROUP BY department_id
ORDER BY avg_salary DESC
LIMIT 1;
```
**Follow-up:** "What if you need a tie-safe version (all departments tied for highest)?" → use a CTE plus
`WHERE avg_salary = (SELECT MAX(avg_salary) FROM ...)` instead of `LIMIT 1`.

---

### Q4. Find duplicate email addresses
```sql
SELECT email, COUNT(*) AS occurrences
FROM users
GROUP BY email
HAVING COUNT(*) > 1;
```

---

### Q5. Delete duplicate rows, keeping only one
```sql
DELETE FROM users
WHERE user_id NOT IN (
  SELECT MIN(user_id)
  FROM users
  GROUP BY email
);
```
**Talk through:** `MIN(user_id)` arbitrarily but deterministically picks which duplicate survives (the
oldest by ID) — state that choice explicitly, since "which copy survives" is a business decision, not just
a technical one.

---

### Q6. Swap values in a column without a temp variable (classic puzzle)
**Problem:** Swap `'M'`/`'F'` values in a `gender` column in a single `UPDATE`.
```sql
UPDATE users
SET gender = CASE gender
  WHEN 'M' THEN 'F'
  WHEN 'F' THEN 'M'
END;
```
**Why it's asked:** tests whether you understand that `CASE` evaluates against the *original* row value
for every branch within one statement — a naive two-step `UPDATE ... SET gender = 'F' WHERE gender = 'M'`
followed by the reverse would incorrectly convert everything to one value.

---

### Q7. Find gaps in a numeric ID sequence (generic ANSI version)
```sql
SELECT (t1.id + 1) AS gap_start, (MIN(t2.id) - 1) AS gap_end
FROM my_table t1
JOIN my_table t2 ON t2.id > t1.id
WHERE NOT EXISTS (SELECT 1 FROM my_table t3 WHERE t3.id = t1.id + 1)
GROUP BY t1.id
HAVING MIN(t2.id) > t1.id + 1;
```
**Talk through:** this is deliberately more involved than the BigQuery `GENERATE_ARRAY` version in
[../bigquery/coding.md](../bigquery/coding.md) Q11 — use it to show you can
reason in plain ANSI SQL when a convenient dialect-specific function isn't available, then mention you'd
prefer the simpler `GENERATE_ARRAY`/`generate_series` version when the engine supports it.

---

### Q8. Pagination query
```sql
SELECT *
FROM products
ORDER BY product_id
OFFSET 40 ROWS FETCH NEXT 20 ROWS ONLY;   -- ANSI standard syntax (page 3, 20 per page)
-- Postgres/MySQL equivalent:
-- SELECT * FROM products ORDER BY product_id LIMIT 20 OFFSET 40;
```
**Follow-up:** "What's the problem with `OFFSET` pagination at very high page numbers?" → the engine still
has to scan and discard all skipped rows, so performance degrades linearly with page depth — the fix is
**keyset/cursor pagination** (`WHERE product_id > :last_seen_id ORDER BY product_id LIMIT 20`), which jumps
directly via an index instead of scanning and discarding.

---

### Q9. Running median (harder — shows window-function fluency)
```sql
WITH ordered AS (
  SELECT
    value,
    ROW_NUMBER() OVER (ORDER BY value) AS rn,
    COUNT(*) OVER () AS total
  FROM measurements
)
SELECT AVG(value) AS median
FROM ordered
WHERE rn IN ((total + 1) / 2, (total + 2) / 2);
```
**Talk through:** this handles both even and odd row counts in one expression — for odd counts both
`rn` values in the `IN` list end up equal (so `AVG` of one value is itself), for even counts they're the
two middle values and `AVG` correctly averages them.

---

### Q10. Find the longest streak of consecutive values per group (generic gaps-and-islands)
```sql
WITH numbered AS (
  SELECT
    user_id,
    activity_date,
    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY activity_date) AS rn
  FROM activity
),
grouped AS (
  SELECT
    user_id,
    activity_date,
    DATE_SUB(activity_date, INTERVAL rn DAY) AS grp  -- MySQL-style date function; adjust per dialect
  FROM numbered
)
SELECT user_id, COUNT(*) AS streak_length, MIN(activity_date) AS streak_start
FROM grouped
GROUP BY user_id, grp
ORDER BY streak_length DESC
LIMIT 1;
```
**Why it's asked:** same "island grouping" trick as the BigQuery sessionization/consecutive-days problems
— interviewers like seeing you recognize it's the identical pattern across dialects, just different date
arithmetic syntax.

---

### Q11. Query optimization conversation starter: rewrite this to use an index effectively
**Given (index-unfriendly):**
```sql
SELECT * FROM orders WHERE YEAR(order_date) = 2026;
```
**The problem:** wrapping the indexed column `order_date` in a function (`YEAR(...)`) usually prevents the
engine from using a standard B-tree index on `order_date` at all, forcing a full table scan.
**The fix:**
```sql
SELECT * FROM orders
WHERE order_date >= '2026-01-01' AND order_date < '2027-01-01';
```
**Talk through:** rewriting as a sargable range predicate (no function wrapping the column) lets the
optimizer use an index seek on `order_date` directly — this is the general-SQL version of the same
"don't wrap the partition column in a function" point made for BigQuery in
[../bigquery/coding.md](../bigquery/coding.md) Q13.

---

### Q12. Primary key / foreign key / unique constraint — write them, then explain referential integrity
```sql
CREATE TABLE orders (
  order_id    BIGINT PRIMARY KEY,
  customer_id BIGINT NOT NULL REFERENCES customers(customer_id),
  order_code  VARCHAR(20) UNIQUE
);
```
**Talk through:** the `REFERENCES` foreign key constraint means the database itself rejects an `INSERT`/
`UPDATE` that would leave `customer_id` pointing at a non-existent customer — referential integrity
enforced by the engine rather than relying on application code to always get it right; discuss
`ON DELETE CASCADE` vs `ON DELETE RESTRICT` trade-offs as a natural follow-up.
